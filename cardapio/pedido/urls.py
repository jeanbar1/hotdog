from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('usuario/<int:id>/', views.listar_pedidos, name='listar_pedidos_por_usuario'),
    path('detalhes/<int:id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('criar/', views.create_pedido, name='create_pedido'),
    path('editar/<int:id>/', views.edit_pedido, name='edit_pedido'),
    path('remover/<int:id>/', views.remove_pedido, name='remove_pedido'),
    path('criar-do-carrinho/', views.criar_pedido_do_carrinho, name='criar_pedido_do_carrinho'),
]