from django.contrib import admin
from pedido.models import Pedido, LocalEntrega, Bairro
# Register your models here.
admin.site.register(Pedido)
admin.site.register(LocalEntrega)
admin.site.register(Bairro)