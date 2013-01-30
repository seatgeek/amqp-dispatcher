"""Test that the container calls gevent correctly and that it works"""
from unittest import TestCase

import gevent
import gevent.event

from amqpdispatcher.process_containers import *
import amqpdispatcher.process_containers

class TestGeventProcessContainer(TestCase):

    def setUp(self):
        self.container = GeventProcessContainer(gevent)

    def test_spawn_runs_function(self):
        result, caller = create_async_result_and_caller()
        self.container.spawn(caller)
        result.get(timeout=.1)


def noop():
    pass


def create_async_result_and_caller():
    result = gevent.event.AsyncResult()
    def caller(*args, **kwargs):
        result.set((args, kwargs))
    return result, caller
