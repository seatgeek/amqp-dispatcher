import logging
import random
import traceback

from aio_pika import IncomingMessage

logger = logging.getLogger(__name__)


class Consumer(object):

    def __init__(self):
        logger.info("I've been initiliazed")


    def handle(self, incoming_message: IncomingMessage):
        logger.info("now consuming an incoming message")
        logger.info(incoming_message)

    def consume(self, amqp, msg):
        logger.debug('Consuming message:'.format(msg.body))

        val = random.random()
        amqp.publish('test_exchange', 'dead_rk', {}, 'New body!')
        if val < .2:
            raise ValueError()
        logger.debug('Done sleeping')
        amqp.ack()

    def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc())
        else:
            logging.debug('Shut down worker cleanly')
