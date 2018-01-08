class QueueFetcherException(Exception):
    """The django-queue-fetcher base exception.
    """


class BotoInitFailedException(QueueFetcherException):
    """Raised when Boto3 isn't able to initialise.
    """


class QueueNotFoundError(QueueFetcherException):
    """Raised when an SQS Queue can't be found.
    """


class MessageSendFailed(QueueFetcherException):
    """Raised when a message can't be sent.
    """


class MessageProcessingError(QueueFetcherException):
    """Raised when a message could not be processed inside queue-fetcher.
    """
