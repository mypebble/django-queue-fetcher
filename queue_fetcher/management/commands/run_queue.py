"""Run the selected queue task
"""
from django.utils.module_loading import import_string
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    """
    """
    args = '<task>'
    help = (
        'Run the selected queue task'
    )

    def get_app_module(self, app_name):
        config = apps.get_app_config(app_name)
        return config.module

    def handle(self, task, *args, **kwargs):
        """
        """
        app_label, task = task.split('.')
        task = import_string('{}.tasks.{}'.format(
            self.get_app_module(app_label).__name__, task))
        t = task()
        t.run()
