import asyncio

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.message import Message
from tests.consumers.base_test_consumer import BaseTestConsumer


class ForeverConsumer(BaseTestConsumer):
    async def consume(self, amqp: AMQPProxy, msg: Message) -> None:
        await super(ForeverConsumer, self).consume(amqp, msg)
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        await future


class ForeverConsumer2(ForeverConsumer):
    pass
