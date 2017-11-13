from queue_fetcher.tasks import QueueFetcher


class SampleCalledException(Exception):
    '''Exception used to flag if the sample method was called
    '''
    pass


class SampleQueueTask(QueueFetcher):
    """A test queue.
    """

    queue = 'test'

    def process_sample(self, msg):
        """Process a test message.
        """
        if msg['test'] == 'hello':
            raise SampleCalledException()


class VisibilityTask(QueueFetcher):
    """Set the visibility timeout.
    """

    queue = 'test'
    visibility_timeout = 30

    def process_sample(self, msg):
        """Process a sample message.
        """
        return True
