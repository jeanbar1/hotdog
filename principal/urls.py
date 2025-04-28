from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"), # pagina inicial
    path("settings/", settings, name="settings"), # configurações
]