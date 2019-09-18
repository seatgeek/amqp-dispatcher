#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Test with gevent that it runs the consumer as expected"""
from unittest import TestCase

from gevent.event import AsyncResult
from mock import MagicMock
import gevent

from amqpdispatcher.consumer_pool import ConsumerPool


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


def create_acking_error_consumer():
    result = AsyncResult()

    class Consumer(object):
        def consume(self, proxy, msg):
            proxy.ack()
            raise Exception()

        def shutdown(self, exception):
            result.set()

    return result, Consumer


class TestConsumerPoolHandlingMessage(TestCase):
    def test_consumers_consume_is_run(self):
        channel = MagicMock(name="channel")
        msg = MagicMock(name="msg")
        result, consumer = create_working_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)

        result.get(timeout=1)

    def test_consumers_shutdown_is_called_when_erroring(self):
        channel = MagicMock(name="channel")
        msg = MagicMock(name="msg")
        result, consumer = create_error_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)

        result.get(timeout=1)

    def test_channel_reject_is_called_when_erroring(self):
        channel = MagicMock(name="channel")
        msg = MagicMock(name="msg")
        result, consumer = create_error_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)
        result.get(timeout=1)

        tag = msg.delivery_info["delivery_tag"]
        channel.basic_reject.assert_called_once_with(tag, requeue=True)

    def test_channel_reject_is_not_called_when_erroring_after_ack(self):
        channel = MagicMock(name="channel")
        msg = MagicMock(name="msg")
        result, consumer = create_acking_error_consumer()

        cp = ConsumerPool(channel, consumer, gevent.Greenlet)
        cp.handle(msg)
        result.get(timeout=1)

        tag = msg.delivery_info["delivery_tag"]
        self.assertEqual(channel.basic.reject.mock_calls, [])
