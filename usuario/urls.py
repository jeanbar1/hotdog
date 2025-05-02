from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('loginadmin/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Operações de usuário
    path('criar/', views.create_usuario, name='create_usuario'),
    path('editar/<int:id>/', views.edit_usuario, name='edit_usuario'),
    path('remover/<int:id>/', views.remove_usuario, name='remove_usuario'),
    
    # Perfil (ambas versões - com e sem ID)
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/<int:id>/', views.perfil_usuario, name='perfil_usuario'),
    
    # Listagem de usuários (apenas para administradores)
    path('usuarios/', views.listar_usuarios, name='listUser'),
    
    # acesso rapido
    path('acesso-rapido/', views.acesso_rapido, name='acesso_rapido'),
    path('login/', views.loginRapido, name='loginRapido'),
    path('perfil/', views.perfil_simples, name='perfil_simples'),
    path('perfil/editar/', views.editar_perfil_simples, name='editar_perfil_simples'),
]

