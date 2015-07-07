#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket

from mock import MagicMock
from unittest import TestCase

from amqpdispatcher.dispatcher_haigha import connect_to_hosts
from amqpdispatcher.dispatcher_haigha import RabbitConnection


class TestConnectingToHosts(TestCase):

    def test_single_host(self):
        connector = MagicMock(RabbitConnection)
        hosts = ['one']

        conn = connect_to_hosts(connector, hosts, arg='arg')

        connector.assert_called_once_with(host='one', arg='arg')
        self.assertEqual(conn, connector())

    def test_first_host_fails(self):
        def fail_on_one(**kwargs):
            if kwargs.get('host') == 'one':
                raise socket.error('Expected error during test')

        connector = MagicMock(RabbitConnection, side_effect=fail_on_one)
        hosts = ['one', 'two']

        conn = connect_to_hosts(connector, hosts, arg='arg')

        connector.assert_called_with(host='two', arg='arg')
        self.assertEqual(conn, connector())
