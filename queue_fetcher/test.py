"""Helper test classes for your SQS integrations.
"""
from os.path import join
import json

import logging

from django.test import TestCase
from django.conf import settings

logger = logging.getLogger(__name__)


class QueueTestCase(TestCase):
    """Provides helper methods to make it easier to test tasks without SQS.
    """

    def get_yaml(self, name):
        """Return the SQS fixture parsed from YAML.
        """
        try:
            import yaml
        except ImportError:
            logger.warning('pyYAML not installed - YAML is not supported')

        return yaml.load(self.get_fixture(name))

    def get_json(self, name):
        """Return the SQS fixture parsed from JSON.
        """
        return json.loads(self.get_fixture(name))

    def get_fixture(self, name):
        """Retrieve the specified fixture.
        """
        parts = name.split('/')
        path = join(settings.BASE_DIR,
                    parts[0],
                    'fixtures',
                    parts[0],
                    *parts[1:])

        with open(path) as fd:
            return fd.read()
