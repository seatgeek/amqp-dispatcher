from typing import Any, Optional

from aio_pika import IncomingMessage
from typing_extensions import TypedDict


class DeliveryInfo(TypedDict):
    consumer_tag: Optional[Any]  # str
    delivery_tag: Optional[Any]  # int
    redelivered: Optional[Any]  # bool
    exchange: str
    routing_key: str


class Message(object):

    """
    Represents an AMQP message.
    """

    def __init__(self, raw_message: IncomingMessage):
        """
        :param delivery_info: pass only if messages was received via
          basic.deliver or basic.get_ok; MUST be None otherwise; default: None
        :param return_info: pass only if message was returned via basic.return;
          MUST be None otherwise; default: None
        """
        body = raw_message.body
        if not isinstance(body, (bytes, bytearray)):
            raise TypeError("Invalid message content type {0}".format(type(body)))

        self._raw_message = raw_message
        self._body = body.decode("utf-8")

    @property
    def raw_message(self) -> IncomingMessage:
        return self._raw_message

    @property
    def delivery_info(self) -> DeliveryInfo:
        return DeliveryInfo(
            {
                "consumer_tag": self._raw_message.consumer_tag,
                "delivery_tag": self._raw_message.delivery_tag,
                "redelivered": self._raw_message.redelivered,
                "exchange": self._raw_message.exchange,
                "routing_key": self.raw_message.routing_key,
            }
        )

    @property
    def body(self) -> str:
        return self._body

    def __len__(self) -> int:
        return len(self._body)

    def __nonzero__(self) -> bool:
        """Have to define this because length is defined."""
        return True

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Message):
            return self._body == other._body
        return False

    def __str__(self) -> str:
        return "Message[body: {}, delivery_info: {}, delivery_tag: {}]".format(
            self._body, self.delivery_info, self._raw_message.delivery_tag
        )
