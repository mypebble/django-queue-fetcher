"""Test queue integrations.
"""
from mock import MagicMock, patch

from django.test import TestCase

from test_project.qf_test.tasks.queues import (
    SampleQueueTask, VisibilityTask, SampleCalledException)
from queue_fetcher.utils import sqs
from queue_fetcher.tasks import MessageError


class SampleTestQueueTestCase(TestCase):
    """Test a sample QueueFetcher.
    """

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

    @patch('queue_fetcher.tasks.base.sqs')
    def test_visibility(self, _sqs):
        """Test the visibility_timeout gets assigned.
        """
        mock_queue = MagicMock()

        _sqs.get_queue.return_value = mock_queue
        task = VisibilityTask()
        task.run_once()

        self.assertTrue(mock_queue.receive_messages.called)
        call_args = mock_queue.receive_messages.call_args[1]

        self.assertEqual(call_args['VisibilityTimeout'], 30)
