"""Test with gevent that it runs the consumer as expected"""
from unittest import TestCase

from gevent.event import AsyncResult
from haigha.channel import Channel
from mock import MagicMock, call
import gevent

from amqpdispatcher.dispatcher import ConsumerPool

def create_working_consumer():
    result = AsyncResult()
    class Consumer(object):

        def consume(self, proxy, msg):
            result.set()

        def shutdown(self, exception):
            pass

    return result, Consumer


def create_error_consumer():
    result = AsyncResult()
    class Consumer(object):

        def consume(self, proxy, msg):
            raise Exception()

        def shutdown(self, exception):
            result.set()

    return result, Consumer

class TestConsumerPoolHandlingMessage(TestCase):

    def test_consumers_consume_is_run(self):
        channel = MagicMock(name='channel')
        msg = MagicMock(name='msg')
        result, consumer = create_working_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)

        result.get(timeout=1)

    def test_consumers_shutdown_is_called_when_erroring(self):
        channel = MagicMock(name='channel')
        msg = MagicMock(name='msg')
        result, consumer = create_working_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)

        result.get(timeout=1)
