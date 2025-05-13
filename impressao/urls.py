from django.urls import path
from .views import imprimir_pedido, receber_webhook_impressao

urlpatterns = [
    path('api/imprimir/<int:pedido_id>/', imprimir_pedido, name='imprimir_pedido'),
    path('api/imprimir/', receber_webhook_impressao, name='webhook_impressao'),
]