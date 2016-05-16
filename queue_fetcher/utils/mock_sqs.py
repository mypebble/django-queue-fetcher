"""Mock SQS to let you "interact" with SQS
"""


class MockMessage(object):
    def __init__(self, body):
        self._body = body

    def get_body(self):
        return self._body


class MockQueue(object):
    def __init__(self, name):
        self.name = name
        self._inbox = []

    def add_message(self, msg):
        self._inbox.append(MockMessage(msg))

    def get_messages(self, *args, **kwargs):
        i = self._inbox
        self._inbox = []
        return i
