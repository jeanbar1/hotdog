from django.urls import path
from . import views

urlpatterns = [
    # Produtos
    path('produto/<int:id>/', views.detalhes_produto, name='detalhes_produto'),
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produto/criar/', views.create_produto, name='addProduto'),
    path('produto/editar/<int:id>/', views.edit_produto, name='editProduto'),
    path('produto/remover/<int:id>/', views.remove_produto, name='deleteProduto'),



    # ... suas outras URLs ...
    path('categoria/adicionar/', views.addCategoria, name='addCategoria'),
    path('categoria/listar/', views.listCategoria, name='listCategoria'),
    path('categoria/editar/<int:id>/', views.editCategoria, name='editCategoria'),
    path('categoria/excluir/<int:id>/', views.deleteCategoria, name='deleteCategoria'),



    # Pesquisa
    path('produto/pesquisa/', views.pesquisar_produtos, name='pesquisar_produto'),

]