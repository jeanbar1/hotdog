from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrinho, name='carrinho'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('<int:id>/', views.carrinho, name='carrinho_usuario'),
    path('atualizar/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('confirmar/', views.confirmar_compra, name='confirmar_compra'),
    path('carrinho/count/', views.carrinho_count, name='carrinho_count'),
    # Exemplo no seu urls.py
    # urls.py
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),

    path('carrinho/remover/<int:id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
]