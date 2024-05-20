from django.apps import AppConfig


class ChainedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chained"

    def ready(self):
        import chained.signals

