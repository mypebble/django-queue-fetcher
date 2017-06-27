"""Helper functions for interacting with SQS
"""
import json
import logging

import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from boto.sqs import connect_to_region, message

from queue_fetcher.utils.mock_sqs import MockQueue


outbox = {}


logger = logging.getLogger(__name__)


SQS_NOT_SETUP = (
    "TEST_SQS is not set in your application's settings file. "
    "Please add TEST_SQS = False to your settings."
)


_mocks = {}


def get_connection(region='eu-west-1'):
    return connect_to_region(region)


def get_queue(name, region='eu-west-1'):
    if not hasattr(settings, 'TEST_SQS'):
        raise ImproperlyConfigured(SQS_NOT_SETUP)
    if settings.TEST_SQS:
        if name not in _mocks:
            _mocks[name] = MockQueue(name)
        return _mocks[name]
    elif name.startswith('arn:aws:sqs:'):
        # This is an ARN
        _, _, _, region, account, queue = name.split(':')
        region = get_connection(region)
        queue = region.get_queue(queue, account)
        queue.set_message_class(message.RawMessage)
        return queue
    else:
        region = get_connection(region)
        queue = region.get_queue(name)
        queue.set_message_class(message.RawMessage)
        return queue


def send_message(queue, message):
    if not hasattr(settings, 'TEST_SQS'):
        raise ImproperlyConfigured(SQS_NOT_SETUP)
    if settings.TEST_SQS:
        # Test Mode: Don't even try and send it!
        if queue.name not in outbox:
            outbox[queue.name] = []
        outbox[queue.name].append(message)
        logger.info('New message on queue {}: {}'.format(
            queue, json.dumps(message)))
    else:
        if not isinstance(message, six.string_types):
            message = json.dumps(message)

        q_message = queue.new_message(message)
        queue.write(q_message)


def queue_send(queue, message):
    """Combined queue retrieval and send
    """
    queue = get_queue(settings.QUEUES[queue])
    send_message(queue, message)


def requeue(queue, message):
    """Put the message back on the queue.
    """
    queue_send(queue, [message])


def clear_outbox():
    global outbox
    outbox = {}
