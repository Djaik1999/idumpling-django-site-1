from django.apps import AppConfig


class DumplingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dumpling'

    # def ready(self):
    #     import dumpling.signals  # noqa
