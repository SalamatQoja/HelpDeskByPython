from django.apps import AppConfig


class HelpdesksideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'helpdeskside'

    def ready(self):
        import helpdeskside.signals 
