import re
from sqlite3 import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from principal.decorators import group_required
from .models import Usuario
from .forms import (
    EditarPerfilSimplesForm,
    UsuarioAdminForm,
    UsuarioClienteForm,
    UsuarioImagemForm,
    AcessoRapidoForm
)

def user_login(request):
    """View para login tradicional (admin/clientes com senha)"""
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
                messages.success(request, f"Bem-vindo(a), {user.nome_completo or user.username}!")
                next_url = request.GET.get('next', 'home')
                
                # Redireciona admins para painel administrativo
                if user.is_admin:
                    return redirect(next_url if 'admin' in next_url else 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuario/login.html', {
        'form': form,
        'titulo': 'Login'
    })

def user_logout(request):
    """View para logout"""
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('home')

def create_usuario(request):
    """View para cadastro completo de usuários (com senha)"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        form = UsuarioAdminForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            
            # Define tipo padrão como cliente se não for admin
            if not form.cleaned_data.get('tipo_usuario') == 'ADMINISTRADOR':
                user.tipo_usuario = 'CLIENTE'
                user.is_staff = False
            
            user.save()
            
            # Configura grupos
            if user.tipo_usuario == 'ADMINISTRADOR':
                grupo_admin, _ = Group.objects.get_or_create(name='Administradores')
                user.groups.add(grupo_admin)
            else:
                grupo_clientes, _ = Group.objects.get_or_create(name='Clientes')
                user.groups.add(grupo_clientes)
            
            # Login automático
            login(request, user)
            messages.success(request, f"Cadastro realizado com sucesso! Bem-vindo, {user.nome_completo}!")
            return redirect('home')
    else:
        form = UsuarioAdminForm()
    
    return render(request, "usuario/addUser.html", {
        "form": form,
        'titulo': 'Criar Conta'
    })

@login_required(login_url='loginRapido')
def edit_usuario(request, id):
    """View para edição de usuários"""
    if not request.user.is_superuser and id != request.user.id:
        messages.error(request, "Você não tem permissão para editar este usuário.")
        return redirect('perfil_usuario')

    usuario = get_object_or_404(Usuario, pk=id)
    is_admin_editing = request.user.is_admin and request.user != usuario

    if request.method == "POST":
        form = UsuarioAdminForm(request.POST, request.FILES, instance=usuario) if is_admin_editing \
              else UsuarioClienteForm(request.POST, request.FILES, instance=usuario)
              
        if form.is_valid():
            user = form.save()
            
            # Se a senha foi fornecida, atualiza
            if 'password1' in form.cleaned_data and form.cleaned_data['password1']:
                user.set_password(form.cleaned_data['password1'])
                user.save()

            # Se o usuário for o mesmo que está editando, faz login novamente
            if request.user.id == usuario.id:
                login(request, user)
                
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil_usuario')
    else:
        form = UsuarioAdminForm(instance=usuario) if is_admin_editing \
              else UsuarioClienteForm(instance=usuario)

    context = {
        'form': form,
        'titulo': 'Editar Perfil',
        'usuario': usuario,
    }

    if usuario.imagem and hasattr(usuario.imagem, 'url'):
        context['current_image_url'] = usuario.imagem.url

    return render(request, 'usuario/editUser.html', context)

@login_required(login_url='loginRapido')
@group_required('Administradores')
def remove_usuario(request, id):
    """View para remoção de usuários (apenas admin)"""
    usuario = get_object_or_404(Usuario, pk=id)
    
    if usuario == request.user:
        messages.error(request, "Você não pode remover seu próprio usuário!")
    else:
        usuario.delete()
        messages.success(request, "Usuário removido com sucesso!")
    
    return redirect('listUser')


@login_required(login_url='loginRapido')
def perfil_usuario(request, id=None):
    """
    View para exibição e atualização do perfil.
    Se um ID for fornecido, mostra o perfil do usuário correspondente (apenas para administradores).
    Caso contrário, mostra o perfil do usuário logado.
    """
    # Determina qual usuário visualizar/editar
    if id is not None:
        if not request.user.is_staff:  # Apenas administradores podem ver outros perfis
            messages.error(request, "Você não tem permissão para acessar este perfil.")
            return redirect('perfil_usuario')  # Redireciona para o próprio perfil
        
        user = get_object_or_404(Usuario, pk=id)
        is_own_profile = (user == request.user)
    else:
        user = request.user
        is_own_profile = True

    # Processamento do formulário (apenas para o próprio perfil)
    if request.method == 'POST' and is_own_profile:
        form = UsuarioImagemForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto de perfil atualizada com sucesso!")
            return redirect('perfil_usuario', id=id if id else None)
    else:
        form = UsuarioImagemForm(instance=user)

    context = {
        'user': user,
        'form': form,
        'titulo': 'Meu Perfil' if is_own_profile else f'Perfil de {user.nome_completo}',
        'is_own_profile': is_own_profile,
        'can_edit': is_own_profile,  # Flag para template saber se pode mostrar o formulário
    }

    return render(request, 'usuario/perfil_simples.html', context)

@login_required
@group_required('Administradores')
def listar_usuarios(request):
    """View para listagem de usuários (apenas admin)"""
    usuarios = Usuario.objects.all().order_by('nome_completo')
    return render(request, 'usuario/listUser.html', {
        'usuarios': usuarios,
        'titulo': 'Lista de Usuários'
    })


def acesso_rapido(request):
    """View para acesso rápido sem senha (apenas para clientes normais)"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AcessoRapidoForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            telefone = form.cleaned_data['telefone']

            # Padroniza o telefone
            telefone_limpo = re.sub(r'\D', '', telefone)
            if len(telefone_limpo) != 11:
                messages.error(request, "Telefone deve conter 11 dígitos (DDD + número)")
                return redirect('acesso_rapido')
            
            telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"

            try:
                usuario = Usuario.objects.get(telefone=telefone_formatado)

                # ❌ Impede login rápido de administradores
                if usuario.tipo_usuario == 'ADMINISTRADOR' or usuario.is_superuser:
                    messages.warning(request, "Administradores devem acessar pelo login tradicional.")
                    return redirect('login')

                # ✅ Atualiza nome caso tenha sido alterado
                if usuario.nome_completo != nome:
                    usuario.nome_completo = nome
                    usuario.save()

            except Usuario.DoesNotExist:
                # ✅ Cria novo usuário cliente
                usuario = Usuario.objects.create(
                    telefone=telefone_formatado,
                    nome_completo=nome,
                    email=f'cliente_{telefone_limpo}@dominio.com',
                    username=f'cliente_{telefone_limpo}',
                    tipo_usuario='CLIENTE'
                )
                usuario.set_unusable_password()
                usuario.save()

            # 🔐 Autentica e faz login do cliente
            usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, usuario)
            messages.success(request, f"Bem-vindo(a), {nome}!")
            return redirect('home')

    else:
        form = AcessoRapidoForm()

    return render(request, 'usuario/acesso_rapido.html', {
        'form': form,
        'titulo': 'Acesso Rápido para Clientes'
    })
    
    
    
def loginRapido(request):
    """View para login tradicional por telefone (clientes sem senha)"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        telefone = request.POST.get('telefone', '').strip()
        
        # Validação do formato visual
        if not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
            messages.error(request, "Formato inválido. Use (DDD) 99999-9999")
            return redirect('loginRapido')
        
        # Remove formatação
        telefone_limpo = re.sub(r'\D', '', telefone)

        # Reaplica a formatação para o padrão usado no banco
        if len(telefone_limpo) == 11:
            telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        else:
            messages.error(request, "Telefone inválido. Deve conter 11 dígitos.")
            return redirect('loginRapido')

        try:
            # Busca o usuário com o telefone formatado
            usuario = Usuario.objects.get(telefone=telefone_formatado)
            
            # Verifica tipo de usuário
            if usuario.tipo_usuario == 'CLIENTE':
                usuario.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, usuario)
                messages.success(request, f"Bem-vindo(a) de volta, {usuario.nome_completo or 'Cliente'}!")
                return redirect('home')
            else:
                messages.info(request, "Administradores devem usar email e senha.")
                return redirect('admin:login')

        except Usuario.DoesNotExist:
            # Redireciona para o acesso rápido com telefone salvo na sessão
            request.session['telefone_cadastro'] = telefone
            return redirect('acesso_rapido')
        
        except Exception as e:
            messages.error(request, f"Erro ao fazer login: {str(e)}")
            return redirect('loginRapido')
    
    return render(request, 'usuario/user_login.html', {'titulo': 'Login por Telefone'})



@login_required(login_url='loginRapido')
def editar_perfil_simples(request):
    """
    Edição simplificada do perfil - apenas nome e telefone
    """
    usuario = request.user
    
    if request.method == "POST":
        form = EditarPerfilSimplesForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil_simples')
    else:
        form = EditarPerfilSimplesForm(instance=usuario)
    
    return render(request, 'usuario/editar_perfil_simples.html', {
        'form': form,
        'titulo': 'Editar Meus Dados'
    })
    
    
@login_required(login_url='loginRapido')
def perfil_simples(request):
    """
    Perfil simplificado para usuários de acesso rápido
    Mostra apenas nome e telefone com opção de edição
    """
    usuario = request.user
    return render(request, 'usuario/perfil_simples.html', {
        'usuario': usuario,
        'titulo': 'Meu Perfil'
    })