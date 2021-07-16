import traceback
from typing import Optional

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.logging import getLogger
from amqpdispatcher.message import Message

logger = getLogger(__name__)


class BaseTestConsumer(object):
    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def __init__(self) -> None:
        logger.info("{0} initialized".format(self.class_name))

    async def consume(self, amqp: AMQPProxy, msg: Message) -> None:
        logger.info("{0} receiving message".format(self.class_name))

    async def shutdown(self, exception: Optional[Exception] = None) -> None:
        if exception is not None:
            logger.error(traceback.format_exc())
        else:
            logger.info("shutting down {0}".format(self.class_name))

    def __del__(self) -> None:
        logger.info("{0} destroyed".format(self.class_name))
