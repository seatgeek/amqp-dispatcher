import asyncio
import sys
from asyncio import AbstractEventLoop

import aio_pika
from aio_pika import Exchange, Channel


async def main(loop: AbstractEventLoop, exchange: str, queue: str):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop)

    async with connection:
        channel: Channel = await connection.channel()

        exchange = Exchange(
            name=exchange,
            connection=connection,
            channel=channel.channel,
            auto_delete=None,
            durable=None,
            internal=None,
            passive=None,
        )
        await exchange.publish(
            aio_pika.Message(
                body=b'{}'
            ),
            routing_key=queue
        )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please provide an exchange and a queue.")
        exit(1)

    exchange = sys.argv[1]
    queue = sys.argv[2]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, exchange, queue))
    loop.close()