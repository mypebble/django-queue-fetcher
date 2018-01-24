"""Helper functions for interacting with SQS
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging

import boto3
import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from queue_fetcher.exceptions import (BotoInitFailedException,
                                      QueueNotFoundError,
                                      MessageSendFailed)
from queue_fetcher.utils.mock_sqs import MockQueue


outbox = {}


logger = logging.getLogger(__name__)


SQS_NOT_SETUP = (
    "TEST_SQS is not set in your application's settings file. "
    "Please add TEST_SQS = False to your settings."
)


_MOCKS = {}


def _get_sqs_queue(region_name, queue_name, account=None):
    sqs = boto3.resource('sqs', region_name=region_name)

    if account is not None:
        queue = sqs.get_queue_by_name(
            QueueName=queue_name,
            QueueOwnerAWSAccountId=account)
    else:
        queue = sqs.get_queue_by_name(QueueName=queue_name)

    return queue


def _is_arn(name):
    """Return whether the given name is an ARN.
    """
    return name.startswith('arn:aws:sqs:')


def get_queue(name, region_name='eu-west-1', account=None,
              raise_exception=True):
    """Return the AWS Queue Object referenced by name.

    You can specify a region_name or account to get a specific queue.
    The name can also be an ARN, overriding the region_name and account set
    here.

    If TEST_SQS is set in settings, this will return a mock object.
    NOTE: TEST_SQS must be set to either True or False for this to work.
    """
    try:
        test_sqs = settings.TEST_SQS
    except AttributeError:
        raise ImproperlyConfigured(SQS_NOT_SETUP)

    if _is_arn(name):
        region_name, account, queue_name = name.split(':')[3:]

    if account is None:
        queue_name = name

    sqs = boto3.resource('sqs', region_name=region_name)

    if sqs is None:
        raise BotoInitFailedException('Could not initialise sqs')

    if test_sqs:
        if name not in _MOCKS:
            _MOCKS[queue_name] = MockQueue(queue_name)
        queue = _MOCKS[queue_name]
    else:

        try:
            if account is None:
                queue = sqs.get_queue_by_name(QueueName=queue_name)
            else:
                queue = sqs.get_queue_by_name(
                    QueueName=queue_name,
                    QueueOwnerAWSAccountId=account)

        except Exception as e:
            if raise_exception:
                raise QueueNotFoundError(
                    'Error getting queue for {}'.format(queue_name))

            logger.warning('Error getting queue for name: %s - %s',
                           queue_name, e)
            queue = None

    return queue


def send_message(queue, message, raise_exception=True):
    """Send message on queue.

    This handles the nitty-gritty of interacting with SQS from your Django app.
    If TEST_SQS is set in settings, this will print the output to console.
    NOTE: TEST_SQS must be set to either True or False for this to work.
    """
    try:
        test_sqs = settings.TEST_SQS
    except AttributeError:
        raise ImproperlyConfigured(SQS_NOT_SETUP)

    if isinstance(message, six.binary_type):
        message = message.decode('utf-8')

    is_text = isinstance(message, six.string_types)

    if test_sqs:
        # Test Mode: Don't even try and send it!
        if is_text:
            message = json.loads(message)

        if queue.name not in outbox:
            outbox[queue.name] = []
        outbox[queue.name].append(message)
        logger.info('New message on queue %s: %s', queue.name, message)
    else:
        if not is_text:
            message = json.dumps(message)

        try:
            queue.send_message(MessageBody=message)
        except Exception as exc:
            if raise_exception:
                raise MessageSendFailed(
                    'Could not send message {} over queue {}'.format(message,
                                                                     queue))
            logger.warning('Could not send message over queue %s - %s',
                           six.text_type(queue),
                           six.text_type(exc))


def queue_send(queue, message, raise_exception=True):
    """Combined queue retrieval and send
    """
    queue = get_queue(settings.QUEUES[queue], raise_exception=raise_exception)
    send_message(queue, message, raise_exception=raise_exception)


def requeue(queue, message, raise_exception=True):
    """Put the message back on the queue.
    """
    queue_send(queue, [message], raise_exception=raise_exception)


def clear_outbox():
    """Clear the test outbox.
    """
    keys = [k for k in outbox]
    for key in keys:
        del outbox[key]
