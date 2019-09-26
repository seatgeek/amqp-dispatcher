import logging
from asyncio import Future
from typing import Dict, Any, Callable, Optional, Awaitable

import pika
from pika import SelectConnection
from pika.connection import Connection


class Dispatcher:
    _connection: Connection

    def __init__(self, configuration: Dict[Any, Any], url: str):
        self._url = url

    def connect(
        self,
        on_connection_closed: Optional[
            Callable[[SelectConnection, Exception], None]
        ] = None,
    ) -> Awaitable[SelectConnection]:
        logger = logging.getLogger("amqp-dispatcher")
        connect_open = Future()

        def on_connection_open(unused_connection: SelectConnection):
            logger.info("connection opened within connection")
            connect_open.set_result(unused_connection)

        def on_connection_open_error(
            unused_connection: SelectConnection, error: Exception
        ):
            logger.info("connection errored within connection")
            connect_open.set_exception(error)

        connection = pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=on_connection_open,
            on_open_error_callback=on_connection_open_error,
            on_close_callback=on_connection_closed,
        )

        connection.ioloop.start()

        return connect_open
