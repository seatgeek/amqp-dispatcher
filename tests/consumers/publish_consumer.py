import asyncio
import logging

from amqpdispatcher.amqp_proxy import AMQPProxy
from tests.consumers.base_test_consumer import BaseTestConsumer

logger = logging.getLogger()


class PublishConsumer(BaseTestConsumer):
    async def consume(self, amqp: AMQPProxy, msg):
        await super(PublishConsumer, self).consume(amqp, msg)
        await amqp.ack()
        await amqp.publish("amq.direct", "publish_queue", headers={}, body=b"")
