from aio_pika import IncomingMessage
from aiormq.types import DeliveredMessage
from pamqp import ContentHeader
from pamqp.specification import Basic

from amqpdispatcher.message import Message


def test_incoming_message_to_message():
    raw_message = IncomingMessage(
        message=DeliveredMessage(
            delivery=Basic.Deliver(
                consumer_tag="ctag",
                delivery_tag="dtag",
                redelivered=True,
                exchange="exc",
                routing_key="rkey",
            ),
            header=ContentHeader(),
            body=b"",
            channel=None,
        )
    )

    message = Message(raw_message=raw_message)

    assert message.delivery_info["consumer_tag"], "ctag"
    assert message.delivery_info["delivery_tag"], "dtag"
    assert message.delivery_info["redelivered"], True
    assert message.delivery_info["exchange"], "exc"
    assert message.delivery_info["routing_key"], "rkey"
