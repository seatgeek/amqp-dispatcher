#!/usr/bin/env python
# -*- coding:utf-8 -*-

from amqpdispatcher.channel_proxy import proxy_channel


class AMQPProxy(object):

    def __init__(self, channel, msg):
        self._channel = proxy_channel(channel)
        self._msg = msg
        self._terminal_state = False

    @property
    def tag(self):
        return self._msg.delivery_info['delivery_tag']

    @property
    def has_responded_to_message(self):
        return self._terminal_state

    def ack(self):
        self._error_if_already_terminated()
        self._channel.basic_ack(self.tag)

    def nack(self):
        self._error_if_already_terminated()
        self._channel.basic_nack(self.tag)

    def reject(self, requeue=True):
        self._error_if_already_terminated()
        self._channel.basic_reject(self.tag, requeue=requeue)

    def publish(self, exchange, routing_key, headers, body):
        self._channel.basic_publish(exchange, routing_key, body, headers)

    def _error_if_already_terminated(self):
        if self._terminal_state:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True
