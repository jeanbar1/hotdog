from django.contrib import admin
from produto.models import Produto, CategoriaProduto, Adicional, ProdutoAdicional
# Register your models here.
admin.site.register(Produto)
admin.site.register(CategoriaProduto)
admin.site.register(Adicional)
admin.site.register(ProdutoAdicional)