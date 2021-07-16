import asyncio
import traceback

from amqpdispatcher.logging import getLogger

logger = getLogger(__name__)


class SecondaryConsumer(object):
    """
    This is an example of a consumer that does not try to do its own
    acknowledging or rejecting, but just does some work.
    """

    def __init__(self) -> None:
        logger.info("I've been secondarily initialized!")

    async def consume(self, amqp, msg):
        logger.debug("Consuming secondary message:".format(msg.body))
        await asyncio.sleep(10)
        logger.debug("Done secondary sleeping, and working")

    async def shutdown(self, exception=None):
        if exception is not None:
            logger.error(traceback.format_exc())
        else:
            logger.debug("Shut down secondary worker cleanly")
