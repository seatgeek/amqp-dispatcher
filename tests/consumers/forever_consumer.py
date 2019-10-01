import asyncio
import logging

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.message import Message
from tests.consumers.base_test_consumer import BaseTestConsumer

logger = logging.getLogger(__name__)


class ForeverConsumer(BaseTestConsumer):
    async def consume(self, amqp: AMQPProxy, msg: Message) -> None:
        await super(ForeverConsumer, self).consume(amqp, msg)
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        await future


class ForeverConsumer2(ForeverConsumer):
    pass
