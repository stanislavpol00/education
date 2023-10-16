from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "main"
    verbose_name = "Application"

    def ready(self):
        import main.signals  # noqa
