from django.contrib import admin
from produto.models import Produto, CategoriaProduto
# Register your models here.
admin.site.register(Produto)
admin.site.register(CategoriaProduto)