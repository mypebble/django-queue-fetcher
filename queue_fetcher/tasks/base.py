"""Base classes for background tasks
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import json
from datetime import datetime

import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from queue_fetcher.exceptions import MessageProcessingError
from queue_fetcher.utils import sqs


# Max number of messages to work on in a cycle - 10 is the maximum supported
BATCH_SIZE = 10
# Max number of seconds to hold request open (long polling)
WAIT_TIME = 20

logger = logging.getLogger(__name__)

QUEUES_NOT_SETUP = (
    "QUEUES is not in your application's settings file. "
    "This needs to be a dict of `internal name`: `name on amazon`. "
    "See https://github.com/mypebble/django-queue-fetcher/blob/master/"
    "README.md#getting-started for more information."
)


class QueueFetcher(object):
    """Deals with fetching things from an Amazon SQS queue
    """

    queue = None
    region = 'eu-west-1'
    visibility_timeout = None

    def __init__(self):
        """Setup internal variables.
        """
        self._queue = None

    def get_queue(self):
        """Return the queue.
        """
        return self.queue

    def get_region(self):
        """Return the region lookup.
        """
        return self.region

    def run(self):
        """Poll the messaging queue for any messages and asks the implementer
        to deal with them.
        """
        self._prerun()

        while True:
            self._run()

    def _prerun(self):
        """Setup the QueueFetcher for getting messages from SQS.
        """
        queue_key = self._get_queue()
        if not hasattr(settings, 'QUEUES'):
            raise ImproperlyConfigured(QUEUES_NOT_SETUP)

        queue_name = settings.QUEUES[queue_key]

        logger.info('Polling %s for messages', queue_name)

        self._queue = sqs.get_queue(queue_name, self.get_region())

    def run_once(self):
        """Run the queue fetcher just once.
        """
        self._prerun()
        self._run()

    def _get_queue(self):
        """Proxy the get_queue internally.
        """
        queue = self.get_queue()
        if queue is None:
            raise ImproperlyConfigured('QueueFetcher.queue is not set')
        return queue

    def _run(self):
        """Do the actual queue_fetcher execution.
        """
        if self.visibility_timeout:
            messages = self._queue.receive_messages(
                MaxNumberOfMessages=BATCH_SIZE,
                WaitTimeSeconds=WAIT_TIME,
                VisibilityTimeout=self.visibility_timeout)
        else:
            messages = self._queue.receive_messages(
                MaxNumberOfMessages=BATCH_SIZE,
                WaitTimeSeconds=WAIT_TIME)

        if len(messages):
            logger.info('%s Received %d messages',
                        datetime.now().isoformat(),
                        len(messages))

            for message in messages:
                if self.read(message.body):
                    message.delete()

    def read(self, q_message):
        """Process a raw message from Amazon SQS.

        This can be used for testing.

        :returns: `True` if successful, otherwise `False`
        """
        rsp = False
        try:
            # Each iteration of the queue-fetcher should be all-or-nothing.
            with transaction.atomic():
                if isinstance(q_message, six.binary_type):
                    q_message = q_message.decode('utf-8')
                if isinstance(q_message, six.text_type):
                    q_message = json.loads(q_message)

                self.process(q_message)

        except MessageProcessingError as ex:
            logger.error(six.text_type(ex))
            logger.info('Message could not be processed')
        else:
            rsp = True

        return rsp

    def process(self, msg):
        """Process the message passed in

        :type msg: list, tuple or dict
        :param msg: Python object of message
        """
        if isinstance(msg, (list, tuple)):  # Handle somewhat invalid data
            for message_item in msg:
                self.process(message_item)
        else:
            try:
                message_type = msg['message_type']
            except KeyError:
                logger.warning('Message did not have a message_type: %s',
                               six.text_type(msg))
                raise MessageProcessingError(
                    'Message did not have a message_type {}'.format(
                        six.text_type(msg)))

            process = getattr(self, 'process_{}'.format(message_type), None)
            if process is not None:
                process(msg)
            else:
                logger.warning('Message type %s not handled. You may need to '
                               'write process_%s.',
                               message_type, message_type)
                raise MessageProcessingError(
                    'Message type {} not handled'.format(message_type))
