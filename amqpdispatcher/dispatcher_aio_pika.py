import logging

from amqpdispatcher.dispatcher_common import setup


async def main_aio_pika(loop):
    logger = logging.getLogger('amqp-dispatcher')
    logger.info("main AIO pika")
    await setup('pika', loop)