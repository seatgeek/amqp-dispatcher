import asyncio
from urllib.parse import urlunparse

import aio_pika
import logging

from amqpdispatcher.dispatcher_common import setup

def connection_params(user, password, host, port, vhost, heartbeat):
    netloc = None
    if user and password:
        netloc = '{0}:{1}'.format(user, password)
    elif user:
        netloc = user

    if netloc is None:
        netloc = host
    else:
        netloc = '{0}@{1}'.format(netloc, host)
    if port:
        netloc = '{0}:{1}'.format(netloc, port)

    query = 'heartbeat={0}'.format(heartbeat)

    url = urlunparse(('amqp', netloc, vhost, '', query, ''))
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    return params


async def connect_to_hosts(connector, hosts, port, user, password, vhost, heartbeat, full_url, **kwargs):
    logger = logging.getLogger('amqp-dispatcher')

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )



    logger.error('Could not connect to any hosts')

async def main_aio_pika(loop):
    setup('pika', loop)

    queue_name = "test_queue"

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(
            queue_name, auto_delete=True
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)

                    if queue.name in message.body.decode():
                        break


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_aio_pika(loop))
    loop.close()