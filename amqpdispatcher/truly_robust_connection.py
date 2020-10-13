import asyncio
import logging
from asyncio import AbstractEventLoop, Future
from typing import Callable, Set, Optional, Dict, Any, Type, Awaitable

import aiormq
from aio_pika import Connection, RobustChannel
from aio_pika.exceptions import CONNECTION_EXCEPTIONS
from aio_pika.tools import CallbackCollection
from aio_pika.types import TimeoutType

from amqpdispatcher.wait_group import WaitGroup

logger = logging.getLogger(__name__)


class TrulyRobustConnection(Connection):
    """Truly Robust connection """

    connection: Optional[aiormq.connection.Connection]  # type: ignore
    consumer_completion_group: WaitGroup
    _reconnect_attempt: int
    _running_task: Optional[Future]
    _on_reconnect_callbacks: CallbackCollection
    _consumption_task: Optional[Callable[[], Awaitable[None]]]
    __channels: Set[RobustChannel]

    CHANNEL_CLASS = RobustChannel

    def __init__(
        self,
        url: str,
        loop: Optional[AbstractEventLoop] = None,
        fail_fast: bool = False,
    ) -> None:
        super().__init__(loop=loop or asyncio.get_event_loop(), url=url)

        self.fail_fast = fail_fast
        self.consumer_completion_group = WaitGroup()

        self.__channels = set()
        self._on_reconnect_callbacks = CallbackCollection(self)
        self._consumption_task = None
        self._running_task = None
        self._closed = False
        self._reconnect_attempt = 1

    @property
    def on_reconnect_callbacks(self) -> CallbackCollection:
        return self._on_reconnect_callbacks

    @property
    def _channels(self) -> Dict[int, RobustChannel]:
        return {ch.number: ch for ch in self.__channels}

    @property
    def reconnect_interval(self) -> float:
        return min(2, 0.05 * pow(2, self._reconnect_attempt))  # type: ignore

    def _on_connection_close(
        self, connection: Any, closing: Any, *args: Any, **kwargs: Any
    ) -> None:
        logger.info("connection phase: connection closing")
        self.connection = None

        # Have to remove non initialized channels
        self.__channels = {ch for ch in self.__channels if ch.number is not None}

        super()._on_connection_close(connection, closing)

        self.loop.call_later(
            self.reconnect_interval, lambda: self.loop.create_task(self.reconnect())
        )

    def add_reconnect_callback(self, callback: Callable[[], None]) -> None:
        """ Add callback which will be called after reconnect.

        :return: None
        """

        self._on_reconnect_callbacks.add(callback)

    def set_and_schedule_consumption_task(
        self, consumption_task: Callable[[], Awaitable[None]]
    ) -> None:
        """
        Sets a consumption task for this connection and schedules
        it to run.
        :return: None
        """
        self._consumption_task = consumption_task
        if self._consumption_task:
            self._running_task = asyncio.ensure_future(self._consumption_task())

    async def connect(self, timeout: Optional[TimeoutType] = None) -> None:
        while True:
            logger.info("connection phase: awaiting task completion")
            try:
                return await super().connect(timeout=timeout)  # type: ignore
            except CONNECTION_EXCEPTIONS:
                if self.fail_fast:
                    raise

                logger.warning(
                    "connection phase: first connection attempt failed "
                    "and will be retried after %d seconds",
                    self.reconnect_interval,
                    exc_info=True,
                )

                await asyncio.sleep(self.reconnect_interval)

    async def reconnect(self) -> None:
        logger.info("reconnection phase: awaiting task completion")

        # If we wanted to wait for all outstanding consumers to
        # complete before reconnecting, we can await
        # the wait group found in self.consumer_completion_group.event.wait(). But
        # this is not strictly necessary, since asyncio.ensure_future, which
        # dispatches the consumption_coroutine, does not get cancelled
        # through the normal cancellation process for futures, and so
        # will continue until its asynchronous operations are completed.
        if self._running_task:
            logger.info("reconnection phase: cancelling running task")
            self._running_task.cancel()
            self._running_task = None

        # close all existing channels
        for channel in self.__channels:
            await channel.close()
        self.__channels = set()

        if self.is_closed:
            return

        logger.info("reconnection phase: reconnecting")
        try:
            await super().connect()
        except CONNECTION_EXCEPTIONS:
            logger.exception("reconnection phase: connect attempt error")
            self._reconnect_attempt += 1

            self.loop.call_later(
                self.reconnect_interval, lambda: self.loop.create_task(self.reconnect())
            )
        else:
            # reset exponential backoff
            self._reconnect_attempt = 1
            await self._on_reconnect()

    def channel(
        self,
        channel_number: Optional[int] = None,
        publisher_confirms: bool = True,
        on_return_raises: bool = False,
    ) -> RobustChannel:
        channel: RobustChannel = super().channel(  # type: ignore
            channel_number=channel_number,  # type: ignore
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises,
        )

        self.__channels.add(channel)

        return channel

    async def _on_reconnect(self) -> None:
        for number, channel in self._channels.items():
            try:
                await channel.on_reconnect(self, number)
            except CONNECTION_EXCEPTIONS:
                logger.exception("reconnection phase: open channel failure")
                await self.close()
                return

        self._on_reconnect_callbacks(self)
        if self._consumption_task:
            self._running_task = asyncio.ensure_future(self._consumption_task())
        logger.info("reconnection phase: success")

    @property
    def is_closed(self) -> bool:
        """ Is this connection is closed """
        return self._closed or super().is_closed

    async def close(self, exc: Type[Exception] = asyncio.CancelledError) -> Any:
        if self.is_closed:
            return

        self._closed = True

        if self.connection is None:
            return

        return await super().close(exc)
