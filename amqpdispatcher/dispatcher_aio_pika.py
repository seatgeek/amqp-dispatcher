import asyncio
from urllib.parse import urlunparse

import aio_pika
import logging

from amqpdispatcher.dispatcher_common import setup

async def main_aio_pika(loop):
    await setup('pika', loop)