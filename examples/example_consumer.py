import logging
import random
import traceback

import gevent

logger = logging.getLogger(__name__)


class Consumer(object):

    def __init__(self):
        logger.info("I've been initiliazed")

    def consume(self, amqp, msg):
        logger.debug('Consuming message:'.format(msg.body))

        gevent.sleep(1)
        val = random.random()
        amqp.publish('test_exchange', 'dead_rk', {}, 'New body!')
        if val < .2:
            raise ValueError()
        logger.debug('Done sleeping')
        amqp.ack()

    def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc(exception))
        else:
            logging.debug('Shut down worker cleanly')
