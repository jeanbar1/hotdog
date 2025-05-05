from django.core.management.base import BaseCommand
from produto.models import Produto
from django.core.files.storage import default_storage
from django.conf import settings

class Command(BaseCommand):
    help = 'Migra imagens locais para o Amazon S3'

    def handle(self, *args, **options):
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR('Execute apenas em produção!'))
            return

        produtos = Produto.objects.exclude(imagem='')
        total = produtos.count()
        
        self.stdout.write(f'Iniciando migração de {total} imagens...')

        for i, produto in enumerate(produtos, 1):
            if produto.imagem:
                try:
                    with produto.imagem.open('rb') as f:
                        default_storage.save(produto.imagem.name, f)
                    self.stdout.write(
                        self.style.SUCCESS(f'[{i}/{total}] Migrado: {produto.imagem.name}'))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Erro ao migrar {produto.imagem.name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Migração concluída!'))