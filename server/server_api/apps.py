from django.apps import AppConfig


class SensorApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server_api'

    def ready(self):
        import server_api.signals  # Import signals when app is ready
