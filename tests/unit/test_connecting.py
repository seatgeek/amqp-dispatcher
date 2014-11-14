from unittest import TestCase
import socket

from mock import MagicMock
from mock import patch
import os

from amqpdispatcher.dispatcher import (
    connect_to_hosts,
    RabbitConnection,
    get_connection_params_from_environment)


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
        f = env_mocker({"RABBITMQ_URL" : "amqp://guest:guest@test.foo.com/"})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com"])

    def test_connection_string_url_single_host_with_port(self):
        f = env_mocker({"RABBITMQ_URL" : "amqp://guest:guest@test.foo.com:5672/"})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com:5672"])

    def test_connection_string_url_multiple_host(self):
        f = env_mocker({"RABBITMQ_URL" : "amqp://guest:guest@server1.foo.com,server2.foo.com/"})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), ["server1.foo.com", "server2.foo.com"])

    def test_connection_string_url_multiple_host_with_port(self):
        f = env_mocker({"RABBITMQ_URL" : "amqp://guest:guest@server1.foo.com,server2.foo.com:5672/"})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), ["server1.foo.com:5672", "server2.foo.com:5672"])

    def test_connection_string_url_bad_param(self):
        f = env_mocker({"RABBITMQ_URL2" : "amqp://guest:guest@server1.foo.com,server2.foo.com/"})
        with patch.object(os, 'getenv', new=f):
            self.assertRaises(Exception, get_connection_params_from_environment)

    def test_connection_string_split_params(self):
        f = env_mocker({
            "RABBITMQ_HOSTS" : "server1.foo.com,server2.foo.com",
            "RABBITMQ_USER" : "guest",
            "RABBITMQ_PASS" : "guest",
            "RABBITMQ_VHOST" : "/",
        })
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), ["server1.foo.com", "server2.foo.com"])

    def test_connection_string_split_params_host(self):
        f = env_mocker({
            "RABBITMQ_HOST" : "server1.foo.com",
            "RABBITMQ_USER" : "guest",
            "RABBITMQ_PASS" : "guest",
            "RABBITMQ_VHOST" : "/",
        })
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), ["server1.foo.com"])

    def test_connection_string_split_params_host_port(self):
        f = env_mocker({
            "RABBITMQ_HOST" : "server1.foo.com:15672",
            "RABBITMQ_USER" : "guest",
            "RABBITMQ_PASS" : "guest",
            "RABBITMQ_VHOST" : "/",
        })
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost = get_connection_params_from_environment()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), ["server1.foo.com:15672"])

    def test_connection_string_split_params_host_invalid_comma(self):
        f = env_mocker({
            "RABBITMQ_HOST" : "server1.foo.com,server2.foo.com",
            "RABBITMQ_USER" : "guest",
            "RABBITMQ_PASS" : "guest",
            "RABBITMQ_VHOST" : "/",
        })

        with patch.object(os, 'getenv', new=f):
            self.assertRaises(Exception, get_connection_params_from_environment)




