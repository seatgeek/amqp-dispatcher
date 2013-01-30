from itertools import permutations
from unittest import TestCase

from mock import MagicMock, call
from haigha.channel import Channel

from amqpdispatcher.dispatcher import AMQPProxy


class TestAmqpProxy(TestCase):

    def setUp(self):
        self.channel = MagicMock(name='channel')
        self.msg = MagicMock(name='msg')
        self.terminals = ['ack', 'nack', 'reject']

    def test_terminal_twice_raises_error(self):
        for terminal in self.terminals:
            proxy = AMQPProxy(self.channel, self.msg)
            term_func = getattr(proxy, terminal)
            term_func()
            self.assertRaises(Exception, term_func)

    def test_any_two_terminal_functions_raise_error(self):
        for term_a, term_b in permutations(self.terminals, 2):
            proxy = AMQPProxy(self.channel, self.msg)
            term_func_a = getattr(proxy, term_a)
            term_func_b = getattr(proxy, term_b)
            term_func_a()
            self.assertRaises(Exception, term_func_b)

    def test_terminal_state_false_when_starting(self):
        proxy = AMQPProxy(self.channel, self.msg)
        self.assertFalse(proxy.has_responded_to_message)

    def test_terminal_state_true_after_responding(self):
        proxy = AMQPProxy(self.channel, self.msg)
        proxy.ack()
        self.assertTrue(proxy.has_responded_to_message)
