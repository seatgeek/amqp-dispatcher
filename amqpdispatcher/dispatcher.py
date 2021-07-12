#!/usr/bin/env python
# -*- coding:utf-8 -*-
import asyncio
import logging
import os

from amqpdispatcher.dispatcher_common import get_args_from_cli, initialize_dispatcher
from amqpdispatcher.validate import validate


def main() -> None:
    if os.getenv("LOGGING_FILE_CONFIG"):
        logging.config.fileConfig(os.getenv("LOGGING_FILE_CONFIG"))  # type: ignore
    else:
        logformat = (
            "[%(asctime)s] %(name)s [pid:%(process)d] - %(levelname)s - %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=datefmt)

    args = get_args_from_cli()
    if args.validate:
        return validate(args.config)

    logger = logging.getLogger()
    logger.info("Connection: aio_pika")

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(initialize_dispatcher(loop))
    try:
        loop.run_forever()
    except Exception:
        loop.close()


if __name__ == "__main__":
    main()
