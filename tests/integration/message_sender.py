import argparse
import asyncio
import sys
from asyncio import AbstractEventLoop

import aio_pika
from aio_pika import Exchange, Channel


async def main(loop: AbstractEventLoop, exchange: str, queue: str, number: int):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )

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

        for i in range(0, number):
            await exchange.publish(aio_pika.Message(body=b"{}"), routing_key=queue)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", default="amq.direct")
    parser.add_argument("--queue", required=True)
    parser.add_argument("--number", default=1, type=int)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, args.exchange, args.queue, args.number))
    loop.close()
