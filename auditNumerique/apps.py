from django.apps import AppConfig

class SadciConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditNumerique'
    
    def ready(self):
        import auditNumerique.signals
