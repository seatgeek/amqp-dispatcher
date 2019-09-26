import asyncio
import logging
import random
import traceback


logger = logging.getLogger(__name__)


class Consumer(object):
    def __init__(self):
        logger.info("I've been primarily initialized!")

    async def consume(self, amqp, msg):
        logger.debug("Consuming primary message:".format(msg.body))

        val = random.random()
        await amqp.publish("amq.direct", "dead_rk", {}, b"New body!")
        # if val < .2:
        #     raise ValueError()
        await asyncio.sleep(3)
        logger.debug(
            "Done primary sleeping {0}".format(amqp._msg.raw_message.delivery_tag)
        )
        await amqp.ack()

    async def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc())
        else:
            logging.debug("Shut down primary worker cleanly")

    def __del__(self):
        logger.info("cleaning up this consumer")
