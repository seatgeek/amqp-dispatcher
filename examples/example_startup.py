import logging


def startup():
    logger = logging.getLogger('amqp-dispatcher')
    logger.info("we  started  up")
