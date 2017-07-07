#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from mock import patch
from unittest import TestCase

from amqpdispatcher.dispatcher_common import parse_heartbeat
from amqpdispatcher.dispatcher_common import parse_env


def env_mocker(data):
    def f(val, default=None):
        return data.get(val, default)
    return f


class TestConnectionParams(TestCase):

    def test_connection_string_url_single_host(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com"])
            self.assertEqual(port, 5672)
            self.assertEqual(heartbeat, None)

    def test_connection_string_url_single_host_with_port(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com:5672/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(hosts, ["test.foo.com"])
            self.assertEqual(port, 5672)
            self.assertEqual(heartbeat, None)

    def test_connection_string_url_multiple_host(self):
        rabbitmq_url = "amqp://guest:guest@server1.foo.com,server2.foo.com/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), [
                "server1.foo.com",
                "server2.foo.com"
            ])
            self.assertEqual(port, 5672)
            self.assertEqual(heartbeat, None)

    def test_connection_string_url_multiple_host_with_port(self):
        rabbitmq_url = "amqp://guest:guest@server1.foo.com,server2.foo.com:5672/"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(user, "guest")
            self.assertEqual(password, "guest")
            self.assertEqual(vhost, "/")
            self.assertEqual(sorted(hosts), [
                "server1.foo.com",
                "server2.foo.com"
            ])
            self.assertEqual(port, 5672)
            self.assertEqual(heartbeat, None)
    
    def test_connection_string_heartbeat(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com/?heartbeat=15"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(heartbeat, 15)
    
    def test_connection_string_heartbeat_override(self):
        rabbitmq_url = "amqp://guest:guest@test.foo.com/?heartbeat=15"
        f = env_mocker({"RABBITMQ_URL": rabbitmq_url, "RABBITMQ_HEARTBEAT": 25})
        with patch.object(os, 'getenv', new=f):
            hosts, user, password, vhost, port, heartbeat = parse_env()
            self.assertEqual(heartbeat, 25)

    def test_parse_heartbeat_without_querysting(self):
        self.assertEqual(None, parse_heartbeat(''))
        self.assertEqual(None, parse_heartbeat(None))

    def test_parse_heartbeat_with_querysting(self):
        self.assertEqual(None, parse_heartbeat('query=0'))
        self.assertEqual(0, parse_heartbeat('heartbeat=0'))
        self.assertEqual(15, parse_heartbeat('heartbeat=15'))

    def test_parse_heartbeat_with_none_in_querystring(self):
        self.assertEqual(None, parse_heartbeat('heartbeat=None'))
        self.assertEqual(None, parse_heartbeat('heartbeat='))

    def test_parse_heartbeat_with_multiple_values(self):
        self.assertEqual(None, parse_heartbeat('heartbeat=1&heartbeat=2'))
        self.assertEqual(None, parse_heartbeat('heartbeat=1&heartbeat=2&heartbeat=3'))
