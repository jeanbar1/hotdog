from django.core.management.base import BaseCommand
from django.conf import settings
from produto.models import Produto  # ajuste o nome do app e model se necessário
import os

class Command(BaseCommand):
    help = 'Migra imagens locais de produtos para o S3'

    def handle(self, *args, **kwargs):
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('Você está em DEBUG=True, use isso em produção com DEBUG=False'))
            return

        for produto in Produto.objects.all():
            if produto.imagem and not produto.imagem.name.startswith('produtos/'):
                local_path = produto.imagem.path
                nome_arquivo = os.path.basename(local_path)
                produto.imagem.name = f'produtos/{nome_arquivo}'
                produto.imagem.storage.save(produto.imagem.name, open(local_path, 'rb'))
                produto.save()
                self.stdout.write(self.style.SUCCESS(f'Migrado: {produto.nome} -> {produto.imagem.url}'))
