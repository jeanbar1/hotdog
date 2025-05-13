from django.db import models
from pedido.models import Pedido  # Supondo que seu app de pedidos se chama 'pedidos'

class Impressao(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='impressao')
    conteudo = models.TextField()
    impresso = models.BooleanField(default=False)
    data_impressao = models.DateTimeField(null=True, blank=True)
    tentativas = models.PositiveIntegerField(default=0)
    ultimo_erro = models.TextField(blank=True)

    class Meta:
        verbose_name = "Impressão"
        verbose_name_plural = "Impressões"

    def __str__(self):
        return f"Impressão #{self.pedido.numero_diario}"