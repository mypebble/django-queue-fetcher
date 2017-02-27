"""Run the selected queue task.
"""
from django.utils.module_loading import import_string
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    """Connect to the SQS queue on our behalf.
    """

    help = ('Run the selected queue task')

    def add_arguments(self, parser):
        """Add the required task argument.
        """
        parser.add_argument('task', type=str, help='Task to run')

    def get_app_module(self, app_name):
        """Return the app module containing the task.
        """
        config = apps.get_app_config(app_name)
        return config.module

    def handle(self, task, *args, **kwargs):  # pylint: disable=W0613
        """Handle the run_queue command.
        """
        app_label, task = task.split('.')
        task = import_string('{}.tasks.{}'.format(
            self.get_app_module(app_label).__name__, task))
        task().run()
