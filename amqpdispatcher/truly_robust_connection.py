import asyncio
import logging
from typing import Callable, Set

from aio_pika import Connection, RobustChannel, Channel
from aio_pika.exceptions import CONNECTION_EXCEPTIONS
from aio_pika.tools import CallbackCollection
from aio_pika.types import TimeoutType
from aiormq.connection import parse_int, parse_bool

from amqpdispatcher.wait_group import WaitGroup

logger = logging.getLogger("amqp-dispatcher")


class TrulyRobustConnection(Connection):
    """Truly Robust connection """
    consumer_completion_group: WaitGroup
    __channels: Set[Channel]

    CHANNEL_CLASS = RobustChannel
    KWARGS_TYPES = (
        ('reconnect_interval', parse_int, '5'),
        ('fail_fast', parse_bool, '1'),
    )

    def __init__(self, url, loop=None, **kwargs):
        super().__init__(
            loop=loop or asyncio.get_event_loop(), url=url, **kwargs
        )

        self.reconnect_interval = self.kwargs['reconnect_interval']
        self.fail_fast = self.kwargs['fail_fast']

        self.consumer_completion_group = WaitGroup()

        self.__channels = set()
        self._on_reconnect_callbacks = CallbackCollection()
        self._reconnect_task = None
        self._closed = False

    @property
    def on_reconnect_callbacks(self) -> CallbackCollection:
        return self._on_reconnect_callbacks

    @property
    def _channels(self) -> dict:
        return {ch.number: ch for ch in self.__channels}

    def _on_connection_close(self, connection, closing, *args, **kwargs):
        logger.warning("connection is closing!")
        self.connection = None

        # Have to remove non initialized channels
        self.__channels = {
            ch for ch in self.__channels if ch.number is not None
        }

        super()._on_connection_close(connection, closing)

        self.loop.call_later(
            self.reconnect_interval,
            lambda: self.loop.create_task(self.reconnect())
        )

    def add_reconnect_callback(self, callback: Callable[[], None]):
        """ Add callback which will be called after reconnect.

        :return: None
        """

        self._on_reconnect_callbacks.add(callback)

    def set_reconnect_task(self, task):
        """ Add callback which will be called after reconnect.

        :return: None
        """
        self._reconnect_task = task

    async def connect(self, timeout: TimeoutType = None):
        while True:
            try:
                return await super().connect(timeout=timeout)
            except CONNECTION_EXCEPTIONS:
                if self.fail_fast:
                    raise

                logger.warning(
                    "First connection attempt failed "
                    "and will be retried after %d seconds",
                    self.reconnect_interval,
                    exc_info=True,
                )

                await asyncio.sleep(self.reconnect_interval)

    async def reconnect(self):
        logger.exception('Reconnection cycle beginning: {0}'.format(self.is_closed))

        # wait for all outstanding consumers to complete
        await self.consumer_completion_group.event.wait()

        # close all existing channels
        for channel in self.__channels:
            await channel.close()

        if self.is_closed:
            return

        try:
            await super().connect()
        except CONNECTION_EXCEPTIONS:
            logger.exception('Connection attempt error')

            self.loop.call_later(
                self.reconnect_interval,
                lambda: self.loop.create_task(self.reconnect())
            )
        else:
            await self._on_reconnect()

    def channel(self, channel_number: int = None,
                publisher_confirms: bool = True,
                on_return_raises=False):

        channel = super().channel(
            channel_number=channel_number,
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises,
        )

        self.__channels.add(channel)

        return channel

    async def _on_reconnect(self):
        for number, channel in self._channels.items():
            try:
                await channel.on_reconnect(self, number)
            except CONNECTION_EXCEPTIONS:
                logger.exception('Open channel failure')
                await self.close()
                return

        self._on_reconnect_callbacks(self)
        if self._reconnect_task:
            await self._reconnect_task()

    @property
    def is_closed(self):
        """ Is this connection is closed """
        return self._closed or super().is_closed

    async def close(self, exc=asyncio.CancelledError):
        if self.is_closed:
            return

        self._closed = True

        if self.connection is None:
            return
        return await super().close(exc)