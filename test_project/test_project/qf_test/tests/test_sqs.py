from mock import patch, MagicMock

from django.test import TestCase, override_settings

from queue_fetcher.utils import sqs


class SQSTestCase(TestCase):
    """Test SQS works in the test mode correctly
    """

    def test_sqs(self):
        # Get queue
        queue = sqs.get_queue('test')
        self.assertEquals(queue.name, 'test')
        # Send a message
        sqs.send_message(queue, {
            'message_type': 'demo',
            'this': 'should work'
        })
        # It should drop into the outbox
        self.assertEquals(len(sqs._OUTBOX['test']), 1)
        self.assertEquals(sqs._OUTBOX['test'][0], {
            'message_type': 'demo',
            'this': 'should work'
        })

    @patch('queue_fetcher.utils.sqs.connect_to_region')
    @override_settings(TEST_SQS=False)
    def test_arn(self, connect_to_region):
        """Test if using an ARN works
        """
        sqs.get_queue('arn:aws:sqs:nowhere:4444455556666:queuenamehere')
        connect_to_region.assert_called_with('nowhere')
        connect_to_region.return_value.get_queue.assert_called_with(
            'queuenamehere', '4444455556666')
