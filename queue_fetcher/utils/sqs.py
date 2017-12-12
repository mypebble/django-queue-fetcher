"""Helper functions for interacting with SQS
"""
import json
import logging

import boto3
import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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


def get_queue(name, region_name='eu-west-1', account=None):
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

    if test_sqs:
        if name not in _MOCKS:
            _MOCKS[queue_name] = MockQueue(queue_name)
        queue = _MOCKS[queue_name]
    else:
        sqs = boto3.resource('sqs', region_name=region_name)

        if sqs is None:
            raise Exception("could not initialise SQS Resource")

        try:
            if account is not None:
                queue = sqs.get_queue_by_name(
                        QueueName=queue_name,
                        QueueOwnerAWSAccountId=account)
            else:
                queue = sqs.get_queue_by_name(QueueName=queue_name)

        except ClientError as e:
            print("Error getting queue for name: "
                  "{} - {}".format(queue_name, e))

    return queue


def send_message(queue, message):
    """Send message on queue.

    This handles the nitty-gritty of interacting with SQS from your Django app.
    If TEST_SQS is set in settings, this will print the output to console.
    NOTE: TEST_SQS must be set to either True or False for this to work.
    """
    try:
        test_sqs = settings.TEST_SQS
    except AttributeError:
        raise ImproperlyConfigured(SQS_NOT_SETUP)

    if test_sqs:
        # Test Mode: Don't even try and send it!
        if queue.name not in outbox:
            outbox[queue.name] = []
        outbox[queue.name].append(message)
        logger.info('New message on queue %s: %s',
                    queue.name, json.dumps(message))
    else:
        is_text = (
            isinstance(message, six.string_types)
            or isinstance(message, six.binary_type)
        )
        if not is_text:
            message = json.dumps(message)

        queue.send_message(MessageBody=message)


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
    """Clear the test outbox.
    """
    keys = [k for k in outbox]
    for key in keys:
        del outbox[key]
