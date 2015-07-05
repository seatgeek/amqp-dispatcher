#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gevent
import gevent.queue
import logging

from amqpdispatcher.amqp_proxy import AMQPProxy


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

    def handle(self, msg):
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
