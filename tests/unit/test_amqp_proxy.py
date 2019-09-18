#!/usr/bin/env python
# -*- coding:utf-8 -*-
from asyncio import Future
from itertools import permutations
import pytest
from mock import MagicMock

from amqpdispatcher.amqp_proxy import AMQPProxy

TERMINALS = ['ack', 'nack', 'reject']


def create_mocks():
    connection = MagicMock(name='connection')
    channel = MagicMock(name='channel')
    message = MagicMock(name='message')
    f = Future()
    f.set_result(None)
    message.raw_message.ack.return_value = f
    message.raw_message.nack.return_value = f
    message.raw_message.reject.return_value = f

    return connection, channel, message


@pytest.mark.asyncio
async def test_terminal_twice_raises_error():
    (connection, channel, message) = create_mocks()
    for terminal in TERMINALS:
        proxy = AMQPProxy(connection, channel, message)
        term_func = getattr(proxy, terminal)
        await term_func()

        with pytest.raises(Exception):
            await term_func()


@pytest.mark.asyncio
async def test_any_two_terminal_functions_raise_error():
    (connection, channel, message) = create_mocks()
    for term_a, term_b in permutations(TERMINALS, 2):
        proxy = AMQPProxy(connection, channel, message)
        term_func_a = getattr(proxy, term_a)
        term_func_b = getattr(proxy, term_b)
        await term_func_a()
        with pytest.raises(Exception):
            await term_func_b()


def test_terminal_state_false_when_starting():
    (connection, channel, message) = create_mocks()
    proxy = AMQPProxy(connection, channel, message)
    assert proxy.has_responded_to_message is False


@pytest.mark.asyncio
async def test_terminal_state_true_after_responding():
    (connection, channel, message) = create_mocks()
    proxy = AMQPProxy(connection, channel, message)
    await proxy.ack()
    assert proxy.has_responded_to_message is True
