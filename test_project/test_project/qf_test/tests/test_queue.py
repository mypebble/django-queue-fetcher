from django.test import TestCase

from test_project.qf_test.tasks.queues import (
    SampleQueueTask, SampleCalledException)
from queue_fetcher.utils import sqs
from queue_fetcher.tasks import MessageError


class SampleTestQueueTestCase(TestCase):
    def test_full_integration(self):
        queue = sqs.get_queue('test')
        queue.add_message({
            'message_type': 'sample',
            'test': 'hello'
        })

        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.run_once()

    def test_simple(self):
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.process({
                'message_type': 'sample',
                'test': 'hello'
            })

    def test_multiple(self):
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.process([
                {
                    'message_type': 'sample',
                    'test': 'hello'
                },
                {
                    'message_type': 'sample',
                    'test': 'hello again'
                }
            ])

    def test_unknown_message(self):
        with self.assertRaises(MessageError):
            task = SampleQueueTask()
            task.process([{
                'message_type': 'nonsample',
            }])
