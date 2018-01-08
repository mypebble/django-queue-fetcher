"""Test queue integrations.
"""
import json
from mock import MagicMock, patch

from django.test import TestCase

from test_project.qf_test.tasks.queues import (
    SampleQueueTask, VisibilityTask, SampleCalledException)
from queue_fetcher.utils import sqs
from queue_fetcher.exceptions import MessageProcessingError


class SampleTestQueueTestCase(TestCase):
    """Test a sample QueueFetcher.
    """

    def test_full_integration(self):
        """End-to-end test.
        """
        queue = sqs.get_queue('test')
        queue.add_message({
            'message_type': 'sample',
            'test': 'hello'
        })

        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.run_once()

    def test_read_list(self):
        """Read a list of messages.
        """
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.read([{
                'message_type': 'sample',
                'test': 'hello',
            }])

    def test_read_single(self):
        """Read an individual message.
        """
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.read({
                'message_type': 'sample',
                'test': 'hello',
            })

    def test_read_json(self):
        """Read a JSON string.
        """
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.read(json.dumps([{
                'message_type': 'sample',
                'test': 'hello',
            }]))

    def test_read_binary(self):
        """Read a binary JSON string.
        """
        with self.assertRaises(SampleCalledException):
            json_in = json.dumps([{
                'message_type': 'sample',
                'test': 'hello',
            }]).encode('utf-8')
            task = SampleQueueTask()
            task.read(json_in)

    def test_simple(self):
        """Receive a single message.
        """
        with self.assertRaises(SampleCalledException):
            task = SampleQueueTask()
            task.process({
                'message_type': 'sample',
                'test': 'hello'
            })

    def test_multiple(self):
        """Receive a list of messages.
        """
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
        """Unknown messages raise an exception.
        """
        with self.assertRaises(MessageProcessingError):
            task = SampleQueueTask()
            task.process([{
                'message_type': 'nonsample',
            }])

    def test_no_message_type(self):
        """Messages with no message_type will not be processed.
        """
        with self.assertRaises(MessageProcessingError):
            task = SampleQueueTask()
            task.process([{'key': 'value'}])

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
