from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from principal.decorators import group_required
from .models import *
from .forms import *

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bem-vindo(a), {user.username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuario/login.html', {'form': form, 'titulo': 'Login'})

def user_logout(request):
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('home')

from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import UsuarioFormSingup

def create_usuario(request):
    """
    View para criação de novos usuários, garantindo que sempre sejam criados como Clientes
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        form = UsuarioFormSingup(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Define senha e configurações obrigatórias para cliente
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.is_staff = False  # Nunca staff
            user.is_superuser = False  # Nunca admin
            
            # Garante que o tipo seja CLIENTE, mesmo se o formulário tentar definir outro
            if hasattr(user, 'tipo_cliente'):
                user.tipo_cliente = "CLIENTE"

            # Salva imagem se fornecida
            if 'imagem' in request.FILES:
                user.imagem = request.FILES['imagem']

            # Salva o usuário
            user.save()

            # Remove de todos os grupos existentes (por segurança)
            user.groups.clear()
            
            # Adiciona apenas ao grupo Clientes (cria se não existir)
            grupo_clientes, created = Group.objects.get_or_create(name='Clientes')
            user.groups.add(grupo_clientes)
            
            # Login automático
            login(request, user)
            messages.success(request, "Cadastro de cliente realizado com sucesso! Bem-vindo!")
            return redirect('home')
    else:
        form = UsuarioFormSingup()
    
    return render(request, "usuario/addUser.html", {
        "form": form,
        'titulo': 'Criar Conta de Cliente'
    })

@login_required
def edit_usuario(request, id):
    if not request.user.is_superuser and id != request.user.id:
        return redirect('perfil_usuario')

    usuario = Usuario.objects.filter(pk=id).first()

    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            user = form.save()  # Salva os dados do usuário

            # Se a senha foi fornecida, salva a senha
            if 'password1' in request.POST and request.POST['password1']:
                user.set_password(request.POST['password1'])
                user.save()

            # Se o usuário for o mesmo que está editando, faz login
            if request.user.id == usuario.id:
                login(request, user)
                messages.success(request, "Perfil atualizado com sucesso!")

            return redirect('perfil_usuario')

    else:
        form = UsuarioForm(instance=usuario)

    context = {
        'form': form,
        'titulo': 'Editar Usuário',
    }

    if usuario.imagem and hasattr(usuario.imagem, 'url'):
        context['current_image_url'] = usuario.imagem.url

    return render(request, 'usuario/editUser.html', context)




@login_required
@group_required('Administradores')
def remove_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    
    if usuario == request.user:
        messages.error(request, "Você não pode remover seu próprio usuário!")
    else:
        usuario.delete()
        messages.success(request, "Usuário removido com sucesso!")
    
    return redirect('listUser')

@login_required
def perfil(request, id=None):
    if not request.user.is_superuser and id is not None and id != request.user.id:
        return redirect('perfil_usuario')
    
    user = request.user if id is None else get_object_or_404(Usuario, pk=id)
    
    if request.method == 'POST':
        # Crie um formulário apenas para a imagem
        form = UsuarioImagemForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto de perfil atualizada com sucesso!")
            return redirect('perfil_usuario')
    else:
        form = UsuarioImagemForm(instance=user)
    
    return render(request, 'usuario/perfil.html', {
        'user': user,
        'titulo': 'Perfil do Usuário',
        'form': form  # Adicione o formulário ao contexto
    })

@login_required
@group_required('Administradores')
def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by('username')
    return render(request, 'usuario/listUser.html', {
        'usuarios': usuarios,
        'titulo': 'Lista de Usuários'
    })