from queue_fetcher.tasks import QueueFetcher


class SampleCalledException(Exception):
    '''Exception used to flag if the sample method was called
    '''
    pass


class SampleQueueTask(QueueFetcher):
    queue = 'test'

    def process_sample(self, msg):
        if msg['test'] == 'hello':
            raise SampleCalledException()
