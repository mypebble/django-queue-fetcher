# QueueFetcher for Django and SQS

[![CircleCI](https://circleci.com/gh/mypebble/django-queue-fetcher.svg?style=svg)](https://circleci.com/gh/mypebble/django-queue-fetcher)
[![PyPI version](https://badge.fury.io/py/queue-fetcher.svg)](https://badge.fury.io/py/queue-fetcher)

QueueFetcher allows you to deal with Amazon SQS queues
in an easier manner in Django.

It provides:

* `run_queue` management task to start the task from cli
* `QueueFetcher` class to do the heavy lifting with the pieces
  seperated out and testable

## Getting started

Install `queue-fetcher` from pip

Add `queue_fetcher` to `INSTALLED_APPLICATIONS`

Add to your settings.py:

```python
TEST_SQS = False

QUEUES = {
    'Internal Name': 'Name On Amazon'
}
```

Now build your tasks in your tasks package:

```
from queue_fetcher.tasks import QueueFetcher

class SampleQueueTask(QueueFetcher):
    queue = 'test'

    def process_sample(self, msg):
        raise NotImplementedError('This does nothing.. yet')
```

QueueFetcher expects messages from SQS to contain
a list of events, with each event containing a `message_type`
attribute of something like `update_transaction`.

This is then dispatched to a function prefixed with `process_`.

### Visibility Timeout

Tasks run from Django Queue Fetcher can, when they hit an error, keep thrashing
your SQS queues. We recommend you set a `visibility_timeout` on each task to
minimise your costs and any errors you send to your logs:

```python
from queue_fetcher.tasks import QueueFetcher


class MyQueueFetcher(QueueFetcher):
    """Same Queue Fetcher.
    """

    queue = 'test'
    visibility_timeout = 60  # Tell SQS to give us 60 seconds to process

    def process_my_message(self, msg):
        """Process a message.
        """
        return True
```

### Testing your Code

The `queue-fetcher` app includes a `QueueTestCase` class that removes the need
to handle SQS in your test code. To use it, simple extend the class and use
`get_yaml` or `get_json` to get your fixtures, located in the same app as your
test.

```python
from queue_fetcher.test import QueueTestCase

from .tasks import ExampleTaskClass


class ExampleTestCase(QueueTestCase):
    """
    """

    def test_my_app(self):
        """
        """
        fixture = self.get_json('exampleapp/test.sqs.json')
        task = ExampleTaskClass()
        task.read(fixture)

        # Insert your assertions here
```
