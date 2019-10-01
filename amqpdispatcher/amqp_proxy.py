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

    def __init__(self, connection: Connection, channel: Channel, message: Message):
        self._message = message
        self._publish_channel = channel
        self._connection = connection
        self._terminal_state = False

    @property
    def has_responded_to_message(self) -> bool:
        return self._terminal_state

    async def ack(self) -> None:
        self._error_if_already_terminated()
        await self._message.raw_message.ack()

    async def nack(self) -> None:
        self._error_if_already_terminated()
        await self._message.raw_message.nack()

    async def reject(self, requeue : bool = True) -> None:
        self._error_if_already_terminated()
        await self._message.raw_message.reject(requeue=requeue)

    async def publish(
        self, exchange_name: str, routing_key: str, headers: Dict[Any, Any], body: bytes
    ) -> None:
        exchange = Exchange(
            name=exchange_name,
            connection=self._connection,
            channel=self._publish_channel.channel,
            auto_delete=None,
            durable=None,
            internal=None,
            passive=None
        )

        message = AioPikaMessage(body=body, headers=headers)
        await exchange.publish(message, routing_key)

    def _error_if_already_terminated(self) -> None:
        if self._terminal_state:
            raise Exception("Already responded to message!")
        else:
            self._terminal_state = True
