from django.apps import AppConfig


class ImpressaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'impressao'

    
    def ready(self):
        import impressao.signals  # Registra os signals