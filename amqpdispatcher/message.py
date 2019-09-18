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
    def raw_message(self):
        return self._raw_message

    @property
    def body(self):
        return self._body

    def __len__(self):
        return len(self._body)

    def __nonzero__(self):
        """Have to define this because length is defined."""
        return True

    def __eq__(self, other):
        if isinstance(other, Message):
            return self._properties == other._properties and self._body == other._body
        return False

    def __str__(self):
        body = self._body.decode("utf-8")
        return ("Message[body: {}, delivery_tag: {}]").format(body, self._delivery_tag)
