#!/usr/bin/env python
# -*- coding:utf-8 -*-
import asyncio
import logging
import os

from amqpdispatcher.dispatcher_common import get_args_from_cli, initialize_dispatcher
from amqpdispatcher.validate import validate


def main():
    if os.getenv("LOGGING_FILE_CONFIG"):
        logging.config.fileConfig(os.getenv("LOGGING_FILE_CONFIG"))
    else:
        logformat = (
            "[%(asctime)s] %(name)s [pid:%(process)d] - %(levelname)s - %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=datefmt)

    args = get_args_from_cli()
    if args.validate:
        return validate(args.config)

    logger = logging.getLogger("amqp-dispatcher")
    logger.info("Connection: {0}".format(args.connection))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_dispatcher(loop))
    loop.close()


if __name__ == "__main__":
    main()
