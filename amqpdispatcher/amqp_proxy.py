#!/usr/bin/env python
# -*- coding:utf-8 -*-

from haigha.message import Message


class AMQPProxy(object):

    def __init__(self, channel, msg):
        self._channel = channel
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
        self._channel.basic.ack(self.tag)

    def nack(self):
        self._error_if_already_terminated()
        self._channel.basic.nack(self.tag)

    def reject(self, requeue=True):
        self._error_if_already_terminated()
        self._channel.basic.reject(self.tag, requeue=requeue)

    def publish(self, exchange, routing_key, headers, body):
        msg = Message(body, headers)
        self._channel.basic.publish(msg, exchange, routing_key)

    def _error_if_already_terminated(self):
        if self._terminal_state:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True
