from amqpdispatcher.logging import getLogger

logger = getLogger(__name__)


def startup():
    logger.info("we started up")
