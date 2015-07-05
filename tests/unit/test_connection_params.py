#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from mock import patch
from unittest import TestCase

from amqpdispatcher.dispatcher_common import parse_url


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
