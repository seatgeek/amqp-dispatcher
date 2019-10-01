from typing import Any

from aio_pika import IncomingMessage


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
        return ("Message[body: {}, delivery_tag: {}]").format(
            self._body, self._raw_message.delivery_tag
        )
