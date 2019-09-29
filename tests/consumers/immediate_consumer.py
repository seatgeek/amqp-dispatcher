import logging

from amqpdispatcher.amqp_proxy import AMQPProxy
from tests.consumers.base_test_consumer import BaseTestConsumer

logger = logging.getLogger(__name__)


class ImmediateConsumer(BaseTestConsumer):
    async def consume(self, amqp: AMQPProxy, msg):
        await super(ImmediateConsumer, self).consume()
        await amqp.ack()

class ImmediateConsumer2(ImmediateConsumer):
    pass
