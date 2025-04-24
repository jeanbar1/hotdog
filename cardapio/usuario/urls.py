from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Operações de usuário
    path('criar/', views.create_usuario, name='create_usuario'),
    path('editar/<int:id>/', views.edit_usuario, name='edit_usuario'),
    path('remover/<int:id>/', views.remove_usuario, name='remove_usuario'),
    
    # Perfil (ambas versões - com e sem ID)
    path('perfil/', views.perfil, name='perfil_usuario'),
    path('perfil/<int:id>/', views.perfil, name='perfil_usuario_com_id'),
    
    # Listagem de usuários (apenas para administradores)
    path('usuarios/', views.listar_usuarios, name='listUser'),
]

