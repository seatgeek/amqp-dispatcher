#!/usr/bin/env python
# -*- coding:utf-8 -*-
from aio_pika import Channel

from amqpdispatcher.message import Message


class AMQPProxy(object):
    _channel: Channel
    _terminal_state: bool
    _msg: Message

    def __init__(self, channel: Channel, msg: Message):
        self._channel = channel
        self._msg = msg
        self._terminal_state = False

    @property
    def tag(self):
        return self._msg.delivery_info['delivery_tag']

    @property
    def has_responded_to_message(self):
        return self._terminal_state

    async def ack(self):
        self._error_if_already_terminated()
        await self._channel.basic_ack(self.tag)

    async def nack(self):
        self._error_if_already_terminated()
        self._channel.basic_nack(self.tag)

    async def reject(self, requeue=True):
        self._error_if_already_terminated()
        self._channel.basic_reject(self.tag, requeue=requeue)

    async def publish(self, exchange, routing_key, headers, body):
        self._channel.basic_publish(exchange, routing_key, body, headers)

    def _error_if_already_terminated(self):
        if self._terminal_state:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True
