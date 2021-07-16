#!/usr/bin/env python
# -*- coding:utf-8 -*-
import asyncio
from logging.config import fileConfig
import os

from amqpdispatcher.dispatcher_common import get_args_from_cli, initialize_dispatcher
from amqpdispatcher.logging import getLogger
from amqpdispatcher.validate import validate

logger = getLogger(__name__)


def main() -> None:
    if os.getenv("LOGGING_FILE_CONFIG"):
        fileConfig(os.getenv("LOGGING_FILE_CONFIG"))

    args = get_args_from_cli()
    if args.validate:
        return validate(args.config)

    logger.info("Connection: aio_pika")

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(initialize_dispatcher(loop))
    try:
        loop.run_forever()
    except Exception:
        loop.close()


if __name__ == "__main__":
    main()
