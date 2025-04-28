from django.contrib import admin
from pedido.models import Pedido, LocalEntrega
# Register your models here.
admin.site.register(Pedido)
admin.site.register(LocalEntrega)
