#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gevent
import gevent.queue
import logging

from amqpdispatcher.amqp_proxy import AMQPProxy
from haigha.message import Message


class ConsumerPool(object):
    def __init__(self, channel, klass, greenlet_maker, size=1):
        self._channel = channel
        self._pool = gevent.queue.Queue()
        self._klass = klass
        self._gm = greenlet_maker
        self._logger = logging.getLogger('amqp-dispatcher')
        for i in range(size):
            self._create()

    def _create(self):
        self._logger.debug('Creating consumer instance: {0}'.format(
            self._klass.__name__
        ))
        self._pool.put(self._klass())

    def _to_dict(self, data_bag):
        data = {}
        for key, value in data_bag.__dict__.items():
            if value is None:
                continue
            data[key] = value
        return data

    def handle(self, msg, *args, **kwargs):
        # wrap pika responses in a dummy Message class
        if len(args) == 3:
            delivery_info = self._to_dict(args[0])
            properties = self._to_dict(args[1])

            body = args[2]
            msg = Message(body, delivery_info, **properties)

        def func():
            consumer = self._pool.get()
            amqp_proxy = AMQPProxy(self._channel, msg)

            def put_back(successful_greenlet):
                self._logger.debug('Successful run, putting consumer back')
                if not amqp_proxy.has_responded_to_message:
                    amqp_proxy.ack()
                self._pool.put(consumer)

            def recreate(failed_greenlet):
                self._logger.info('Consume failed, shutting down consumer')
                if not amqp_proxy.has_responded_to_message:
                    amqp_proxy.reject(requeue=True)
                shutdown_greenlet = gevent.Greenlet(
                    consumer.shutdown,
                    failed_greenlet.exception
                )

                def create_wrapper(*args):
                    self._create()
                shutdown_greenlet.link(create_wrapper)
                shutdown_greenlet.start()

            greenlet = self._gm(consumer.consume, amqp_proxy, msg)
            greenlet.link_value(put_back)
            greenlet.link_exception(recreate)
            greenlet.start()
        self._gm(func).start()
