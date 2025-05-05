from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"), # pagina inicial
    path("settings/", user_settings, name="settings"), # configurações
    path('api/migrate-images/', migrate_images, name='migrate_images_api'),
]