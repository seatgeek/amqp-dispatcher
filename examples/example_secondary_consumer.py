import logging
import random
import traceback


logger = logging.getLogger(__name__)


class SecondaryConsumer(object):

    def __init__(self):
        logger.info("I've been secondarily initialized!")

    async def consume(self, amqp, msg):
        logger.debug('Consuming secondary message:'.format(msg.body))

        val = random.random()
        await amqp.publish('amq.direct', 'dead_rk', {}, b'New body!')
        if val < .2:
            raise ValueError()
        logger.debug('Done sleeping')
        await amqp.ack()

    async def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc())
        else:
            logging.debug('Shut down secondary worker cleanly')
