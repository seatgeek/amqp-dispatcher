#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Dict, Any

from aio_pika import Channel, Exchange, Connection
from aio_pika import Message as AioPikaMessage

from amqpdispatcher.message import Message


class AMQPProxy(object):
    _connection: Connection
    _publish_channel: Channel
    _terminal_state: bool
    _message: Message
    _exchanges: Dict[str, Exchange]

    def __init__(self, connection: Connection, channel: Channel, message: Message):
        self._message = message
        self._publish_channel = channel
        self._connection = connection
        self._terminal_state = False
        self._exchanges = {}

    @property
    def has_responded_to_message(self):
        return self._terminal_state

    async def ack(self):
        self._error_if_already_terminated()
        print(self._message.raw_message)
        await self._message.raw_message.ack()

    async def nack(self):
        self._error_if_already_terminated()
        await self._message.raw_message.nack()

    async def reject(self, requeue=True):
        self._error_if_already_terminated()
        await self._message.raw_message.reject(requeue=requeue)

    async def publish(
        self, exchange: str, routing_key: str, headers: Dict[Any, Any], body: bytes
    ):
        if self._exchanges.get(exchange):
            exchange = self._exchanges.get(exchange)
        else:
            exchange = Exchange(
                name=exchange,
                connection=self._connection,
                channel=self._publish_channel.channel,
                auto_delete=None,
                durable=None,
                internal=None,
                passive=None,
            )

        message = AioPikaMessage(body=body, headers=headers)
        await exchange.publish(message, routing_key)

    def _error_if_already_terminated(self):
        if self._terminal_state:
            raise Exception("Already responded to message!")
        else:
            self._terminal_state = True
