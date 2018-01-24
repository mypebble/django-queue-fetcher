import json

from mock import patch

from django.test import TestCase, override_settings

from queue_fetcher.utils import sqs


class SQSTestCase(TestCase):
    """Test SQS works in the test mode correctly
    """

    def setUp(self):
        """Clear the text outbox.
        """
        sqs.clear_outbox()

    def test_sqs(self):
        """Test the send_message method with a dict.
        """
        # Get queue
        queue = sqs.get_queue('test')
        self.assertEquals(queue.name, 'test')  # Send a message
        sqs.send_message(queue, {
            'message_type': 'demo',
            'this': 'should work'
        })
        # It should drop into the outbox
        self.assertEquals(len(sqs.outbox['test']), 1)
        self.assertEquals(sqs.outbox['test'][0], {
            'message_type': 'demo',
            'this': 'should work'
        })

    def test_sqs_list(self):
        """Test the send_message method with a list.
        """
        # Get queue
        queue = sqs.get_queue('test')
        self.assertEquals(queue.name, 'test')  # Send a message
        sqs.send_message(queue, [{
            'message_type': 'demo',
            'this': 'should work'
        }])
        # It should drop into the outbox
        self.assertEquals(len(sqs.outbox['test']), 1)
        self.assertEquals(sqs.outbox['test'][0], [{
            'message_type': 'demo',
            'this': 'should work'
        }])

    def test_sqs_string(self):
        """Test the send_message method with a string.
        """
        # Get queue
        queue = sqs.get_queue('test')
        self.assertEquals(queue.name, 'test')
        # Send a message
        sqs.send_message(
            queue, '{"message_type": "demo","this": "should work"}')
        # It should drop into the outbox
        self.assertEquals(len(sqs.outbox['test']), 1)
        self.assertEquals(sqs.outbox['test'][0], {
            'message_type': 'demo',
            'this': 'should work'
        })

    def test_sqs_binary(self):
        """Test the send_message method with a binary string.
        """
        # Get queue
        queue = sqs.get_queue('test')
        self.assertEquals(queue.name, 'test')
        # Send a message
        sqs.send_message(
            queue, b'{"message_type": "demo","this": "should work"}')
        # It should drop into the outbox
        self.assertEquals(len(sqs.outbox['test']), 1)
        self.assertEquals(sqs.outbox['test'][0], {
            'message_type': 'demo',
            'this': 'should work'
        })


@override_settings(TEST_SQS=False)
class SQSProductionTestCase(TestCase):
    """Test SQS methods with TEST_SQS = False.
    """

    @patch('queue_fetcher.utils.sqs.get_queue')
    def test_sqs(self, mock_queue):
        """Test the send_message method with a dict.
        """
        message = [{
            'message_type': 'demo',
            'this': 'should work'
        }]

        sqs.send_message(mock_queue, message)

        _args, cwargs = mock_queue.send_message.call_args
        self.assertEqual(cwargs['MessageBody'], json.dumps(message))

    @patch('queue_fetcher.utils.sqs.get_queue')
    def test_sqs_list(self, mock_queue):
        """Test the send_message method with a list.
        """
        message = [{
            'message_type': 'demo',
            'this': 'should work'
        }]

        sqs.send_message(mock_queue, message)

        _args, cwargs = mock_queue.send_message.call_args
        self.assertEqual(cwargs['MessageBody'], json.dumps(message))

    @patch('queue_fetcher.utils.sqs.get_queue')
    def test_sqs_string(self, mock_queue):
        """Test the send_message method with a string.
        """
        message = json.dumps({
            'message_type': 'demo',
            'this': 'should work'
        })

        sqs.send_message(mock_queue, message)

        _args, cwargs = mock_queue.send_message.call_args
        self.assertEqual(cwargs['MessageBody'], message)

    @patch('queue_fetcher.utils.sqs.get_queue')
    def test_sqs_binary(self, mock_queue):
        """Test the send_message method with a binary string.
        """
        message = json.dumps({
            'message_type': 'demo',
            'this': 'should work'
        })

        sqs.send_message(mock_queue, message.encode('utf-8'))

        _args, cwargs = mock_queue.send_message.call_args
        self.assertEqual(cwargs['MessageBody'], message)

    @patch('boto3.resource')
    def test_arn(self, resource):
        """Test if using an ARN works
        """
        sqs.get_queue('arn:aws:sqs:nowhere:4444455556666:queuenamehere')
        resource.assert_called_with('sqs', region_name='nowhere')
        resource.return_value.get_queue_by_name.assert_called_with(
            QueueName='queuenamehere', QueueOwnerAWSAccountId='4444455556666')
