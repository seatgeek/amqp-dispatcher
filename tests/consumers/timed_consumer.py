import asyncio

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.logging import getLogger
from tests.consumers.base_test_consumer import BaseTestConsumer

logger = getLogger(__name__)


class TimedConsumer(BaseTestConsumer):
    @property
    def waiting_time(self) -> int:
        return 5

    async def consume(self, amqp: AMQPProxy, msg):
        await super(TimedConsumer, self).consume(amqp, msg)
        await asyncio.sleep(self.waiting_time)
        logger.info("{0} finished work on message".format(self.class_name))
        await amqp.ack()
        logger.info("{0} acked message".format(self.class_name))
