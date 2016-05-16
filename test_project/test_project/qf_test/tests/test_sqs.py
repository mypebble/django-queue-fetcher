from django.test import TestCase

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
