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
                messages.success(request, f"Bem-vindo(a), {user.nome or user.username}!")
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

def create_usuario(request):
    """
    View para criação de novos usuários com username automático
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Configurações obrigatórias para cliente
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.tipo_cliente = "CLIENTE"  # Garante que seja sempre cliente

            # Remove o username do formulário pois será gerado automaticamente
            if hasattr(form, 'cleaned_data') and 'username' in form.cleaned_data:
                del form.cleaned_data['username']

            # Salva imagem se fornecida
            if 'imagem' in request.FILES:
                user.imagem = request.FILES['imagem']

            # Salva o usuário (o username será gerado no método save() do modelo)
            user.save()

            # Configura grupos
            user.groups.clear()
            grupo_clientes, created = Group.objects.get_or_create(name='Clientes')
            user.groups.add(grupo_clientes)
            
            # Login automático
            login(request, user)
            messages.success(request, f"Cadastro realizado com sucesso! Bem-vindo, {user.nome}!")
            return redirect('home')
    else:
        form = UsuarioForm()
    
    return render(request, "usuario/addUser.html", {
        "form": form,
        'titulo': 'Criar Conta'
    })

@login_required
def edit_usuario(request, id):
    if not request.user.is_superuser and id != request.user.id:
        return redirect('perfil_usuario')

    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            user = form.save()

            # Se a senha foi fornecida, atualiza
            if 'password1' in request.POST and request.POST['password1']:
                user.set_password(request.POST['password1'])
                user.save()

            # Se o usuário for o mesmo que está editando, faz login novamente
            if request.user.id == usuario.id:
                login(request, user)
                messages.success(request, "Perfil atualizado com sucesso!")

            return redirect('perfil_usuario')
    else:
        form = UsuarioForm(instance=usuario)

    context = {
        'form': form,
        'titulo': 'Editar Perfil',
        'usuario': usuario,
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
        form = UsuarioImagemForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto de perfil atualizada com sucesso!")
            return redirect('perfil_usuario')
    else:
        form = UsuarioImagemForm(instance=user)
    
    return render(request, 'usuario/perfil.html', {
        'user': user,
        'titulo': 'Meu Perfil',
        'form': form
    })

@login_required
@group_required('Administradores')
def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by('nome')
    return render(request, 'usuario/listUser.html', {
        'usuarios': usuarios,
        'titulo': 'Lista de Usuários'
    })