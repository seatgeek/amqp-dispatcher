from amqpdispatcher.amqp_proxy import AMQPProxy
from tests.consumers.base_test_consumer import BaseTestConsumer


class ImmediateConsumer(BaseTestConsumer):
    async def consume(self, amqp: AMQPProxy, msg):
        await super(ImmediateConsumer, self).consume(amqp, msg)
        await amqp.ack()


class ImmediateConsumer2(ImmediateConsumer):
    pass
