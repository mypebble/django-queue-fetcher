# QueueFetcher for Django and SQS

[![CircleCI](https://circleci.com/gh/mypebble/django-queue-fetcher.svg?style=svg)](https://circleci.com/gh/mypebble/django-queue-fetcher)

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
a list of events, with each event containg a `message_type`
attribute of something like `update_transaction`.

This is then dispatched to a function prefixed with `process_`.
