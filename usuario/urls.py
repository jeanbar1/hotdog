from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('loginadmin/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Operações de usuário
    #path('criar/', views.create_usuario, name='create_usuario'),
    #path('editar/<int:id>/', views.edit_usuario, name='edit_usuario'),  # Descomente esta linha
    path('remover/<int:id>/', views.remove_usuario, name='remove_usuario'),
    
    # Perfil
    #path('perfil/', views.perfil_usuario, name='perfil_usuario'),  # Para o próprio usuário
    #path('perfil/<int:id>/', views.perfil_usuario, name='perfil_usuario_com_id'),  # Para visualizar outros perfis
    
    # Listagem de usuários
    path('usuarios/', views.listar_usuarios, name='listUser'),
    
    # Acesso rápido
    path('acesso-rapido/', views.acesso_rapido, name='acesso_rapido'),
    path('login/', views.loginRapido, name='loginRapido'),
    
    # Perfil simples (se ainda necessário)
    path('perfil-simples/', views.perfil_simples, name='perfil_simples'),
    path('perfil-simples/editar/', views.editar_perfil_simples, name='editar_perfil_simples'),  # Reutiliza a view existente
]