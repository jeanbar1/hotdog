from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf.urls.static import static
from cardapio import settings

def error_handler(request, exception=None, status_code=None):
    if status_code is None:
        status_code = 500
    context = {
        'status_code': status_code,
        'exception': exception,
    }
    return render(request, 'error.html', context, status=status_code)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("principal.urls"), name="index"),
    path('usuario/', include("usuario.urls"), name="usuario"),
    path('produto/', include("produto.urls"), name="produto"),
    path('pedido/', include('pedido.urls'), name='pedido'),
    path('carrinho/', include("carrinho.urls"), name="carrinho"),
]

# Configuração dos manipuladores de erro
handler400 = error_handler
handler403 = error_handler
handler404 = error_handler
handler500 = error_handler

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

