import asyncio
import logging
import traceback

from amqpdispatcher.amqp_proxy import AMQPProxy

logger = logging.getLogger(__name__)


class ImmediateConsumer(object):
    def __init__(self):
        logger.info("immediate consumer initialized")

    async def consume(self, amqp: AMQPProxy, msg):
        logger.debug("immediate consumer receiving message")
        await amqp.ack()

    async def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc())
        else:
            logging.debug("Shut down immediate consumer cleanly")
