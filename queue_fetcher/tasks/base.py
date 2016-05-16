"""Base classes for background tasks
"""
import logging
import json
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from queue_fetcher.utils import sqs


# Max number of messages to work on in a cycle - 10 is the maximium supported
BATCH_SIZE = 10
# Max number of seconds to hold request open (long polling)
WAIT_TIME = 20

logger = logging.getLogger(__name__)

QUEUES_NOT_SETUP = (
    "QUEUES is not in your application's settings file." 
    "This needs to be a dict of `internal name`: `name on amazon`"
)


class MessageError(Exception):
    """An error occurred while processing the message
    and you would like to requeue it
    """
    pass


class QueueFetcher(object):
    """Deals with fetching things from an Amazon SQS queue
    """
    queue = None

    def run(self):
        """Polls the messaging queue for any messages
        and asks the implementor to deal with them
        """
        self._prerun()

        while True:
            self._run()

    def _prerun(self):
        """Setup the QueueFetcher for getting messages from SQS
        """
        if self.queue is None:
            raise AttributeError('QueueFetcher.queue is not set')

        if not hasattr(settings, 'QUEUES'):
            raise ImproperlyConfigured(QUEUES_NOT_SETUP)

        queue_name = settings.QUEUES[self.queue]
        logger.info(u'Polling {queue} for messages'.format(
            queue=queue_name))
        self._queue = sqs.get_queue(queue_name)

    def run_once(self):
        """Run the queue fetcher just once
        """
        self._prerun()
        self._run()

    def _run(self):
        messages = self._queue.get_messages(
            BATCH_SIZE,
            wait_time_seconds=WAIT_TIME)
        if len(messages):
            logger.info(u'{} Received {} messages'.format(
                datetime.now(),
                len(messages)))
            for message in messages:
                if self.read(message.get_body()):
                    self._queue.delete_message(message)

    def read(self, q_message):
        """Process a raw message from Amazon SQS. Retruns
        true if processed without error

        Also used for testing
        """
        rsp = False
        try:
            # Use transactions by default in case something goes
            # wrong, then the database isn't left in a mess
            with transaction.atomic():
                if isinstance(q_message, basestring):
                    q_message = json.loads(q_message)
                for real_message in q_message:
                    logger.debug(json.dumps(real_message))
                    self.process(real_message)
        except MessageError as ex:
            logger.error(unicode(ex))
            logger.info('Message could not be processed')
        else:
            rsp = True
        return rsp

    def process(self, msg):
        """Process the message passed in

        @param msg Python object of message
        """
        if isinstance(msg, (list, tuple)):  # Handle somewhat invalid data
            for message_item in msg:
                self.process(message_item)
        elif hasattr(self, "process_{}".format(msg['message_type'])):
            getattr(self, "process_{}".format(msg['message_type']))(msg)
        else:
            raise MessageError('Message type {} not handled'.format(
                msg['message_type']))
