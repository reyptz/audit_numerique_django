from django.apps import AppConfig

class AuditNumeriqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Audit_Numerique'
    
    def ready(self):
        import Audit_Numerique.signals
