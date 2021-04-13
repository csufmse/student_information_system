from django.apps import AppConfig


class SchooladminConfig(AppConfig):
    name = 'schooladmin'
    label = 'admin.school'

    def ready(self):
        from . import scheduler
        scheduler.start()
