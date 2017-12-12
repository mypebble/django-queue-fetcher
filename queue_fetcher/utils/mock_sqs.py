"""Mock SQS to let you "interact" with SQS
"""


class MockMessage(object):
    def __init__(self, body):
        self.body = body

    def delete():
        pass


class MockQueue(object):
    def __init__(self, name):
        self.name = name
        self._inbox = []

    def add_message(self, msg):
        self._inbox.append(MockMessage(msg))

    def receive_messages(self, *args, **kwargs):
        i = self._inbox
        self._inbox = []
        return i
