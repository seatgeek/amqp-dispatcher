from unittest import TestCase
import socket

from mock import MagicMock
from mock import patch
import os

from amqpdispatcher.dispatcher import connect_to_hosts
from amqpdispatcher.dispatcher import RabbitConnection
from amqpdispatcher.dispatcher import parse_url


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


def env_mocker(data):
    def f(val, default=None):
        return data.get(val, default)
    return f


class TestConnectionParams(TestCase):

    def test_connection_string_url_single_host(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port = parse_url()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com"])
            self.assertEqual(port, 5672)

    def test_connection_string_url_single_host_with_port(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com:5672/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port = parse_url()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com"])
            self.assertEqual(port, 5672)

    def test_connection_string_url_multiple_host(self):
        rabbitmq_url = "amqp://guest:guest@server1.foo.com,server2.foo.com/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port = parse_url()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), [
                "server1.foo.com",
                "server2.foo.com"
            ])
            self.assertEqual(port, 5672)

    def test_connection_string_url_multiple_host_with_port(self):
        rabbitmq_url = "amqp://guest:guest@server1.foo.com,server2.foo.com:5672/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port = parse_url()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), [
                "server1.foo.com",
                "server2.foo.com"
            ])
            self.assertEqual(port, 5672)
