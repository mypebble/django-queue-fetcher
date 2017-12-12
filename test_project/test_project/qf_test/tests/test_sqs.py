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
        self.assertEquals(len(sqs.outbox['test']), 1)
        self.assertEquals(sqs.outbox['test'][0], {
            'message_type': 'demo',
            'this': 'should work'
        })

    @patch('boto3.resource')
    @override_settings(TEST_SQS=False)
    def test_arn(self, resource):
        """Test if using an ARN works
        """
        sqs.get_queue('arn:aws:sqs:nowhere:4444455556666:queuenamehere')
        resource.assert_called_with('sqs', region_name='nowhere')
        resource.return_value.get_queue_by_name.assert_called_with(QueueName='queuenamehere', QueueOwnerAWSAccountId='4444455556666')
