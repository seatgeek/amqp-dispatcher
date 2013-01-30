from unittest import TestCase

from mock import MagicMock, call
from haigha.channel import Channel
import gevent

from amqpdispatcher.dispatcher import ConsumerPool


class TestConsumerPool(TestCase):

    def setUp(self):
        self.channel = MagicMock(Channel)
        self.greenlet_maker = MagicMock(gevent.Greenlet)
        self.consumer_class = MagicMock('consumer_class')
        self.consumer_class.__name__ = 'Mock consumer class'

    def test_creates_consumer_specific_number_of_times(self):
        i = 3
        pool = ConsumerPool(
            self.channel,
            self.consumer_class,
            self.greenlet_maker,
            i,
        )
        calls = [call() for i in range(i)]

        self.consumer_class.assert_has_calls(calls)
