import logging
import traceback

logger = logging.getLogger(__name__)


class BaseTestConsumer(object):
    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def __init__(self):
        logger.info("{0} initialized".format(self.class_name))

    async def consume(self, amqp, msg):
        logger.info("{0} receiving message".format(self.class_name))

    async def shutdown(self, exception=None):
        if exception is not None:
            logging.error(traceback.format_exc())
        else:
            logging.info("shutting down {0}".format(self.class_name))

    def __del__(self):
        logger.info("{0} destroyed".format(self.class_name))
