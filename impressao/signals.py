from django.db.models.signals import post_save
from django.dispatch import receiver
from pedido.models import Pedido
from .models import Impressao
from .printers import PrinterService

@receiver(post_save, sender=Pedido)
def criar_impressao_para_pedido(sender, instance, created, **kwargs):
    if created:
        conteudo = PrinterService.gerar_conteudo_impressao(instance)
        Impressao.objects.create(
            pedido=instance,
            conteudo=conteudo
        )