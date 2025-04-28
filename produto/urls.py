from django.urls import path
from . import views

urlpatterns = [
    # Produtos
    path('produto/<int:id>/', views.detalhes_produto, name='detalhes_produto'),
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produto/criar/', views.create_produto, name='addProduto'),
    path('produto/editar/<int:id>/', views.edit_produto, name='editProduto'),
    path('produto/remover/<int:id>/', views.remove_produto, name='deleteProduto'),

    # Categorias
    path('categoria/adicionar/', views.addCategoria, name='addCategoria'),
    path('categoria/listar/', views.listCategoria, name='listCategoria'),
    path('categoria/listar/<int:id>/', views.listCategoria, name='listCategoria'),
    path('categoria/editar/<int:id>/', views.editCategoria, name='editCategoria'),
    path('categoria/excluir/<int:id>/', views.deleteCategoria, name='deleteCategoria'),

    # Pesquisa
    path('produto/pesquisa/', views.pesquisar_produtos, name='pesquisar_produto'),

    # URLs para Adicionais (NOVAS) --------------------------------------------
    path('adicionais/', views.listar_adicionais, name='listar_adicionais'),
    path('adicional/criar/', views.criar_adicional, name='criar_adicional'),
    path('adicional/editar/<int:id>/', views.editar_adicional, name='editar_adicional'),
    path('adicional/remover/<int:id>/', views.remover_adicional, name='remover_adicional'),
    
    # URLs para gerenciar adicionais de produtos
    path('produto/<int:produto_id>/adicionais/', views.gerenciar_adicionais_produto, name='gerenciar_adicionais_produto'),
    path('produto/adicional/toggle/<int:produto_adicional_id>/',views.toggle_adicional_produto, name='toggle_adicional_prod1uto'),
]