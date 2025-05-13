from django.contrib import admin
from .models import Impressao

@admin.register(Impressao)
class ImpressaoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'impresso', 'data_impressao', 'tentativas')
    list_filter = ('impresso',)
    search_fields = ('pedido__numero_diario',)
    readonly_fields = ('conteudo', 'ultimo_erro')