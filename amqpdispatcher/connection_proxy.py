#!/usr/bin/env python
# -*- coding:utf-8 -*-


def wrap_connection(conn):
    klass = '{0}.{1}'.format(conn.__module__, conn.__class__.__name__)
    if klass == 'haigha.connections.rabbit_connection.RabbitConnection':
        return HaighaConnectionProxy(conn)
    return conn


class ConnectionProxy(object):
    def __init__(self, connection):
        self._connection = connection

    def __getattr__(self, method_name):
        method = getattr(self._connection, method_name, None)
        if method:
            return method
        raise AttributeError(method_name)


class HaighaConnectionProxy(ConnectionProxy):
    def add_on_close_callback(self, callback_method):
        self._connection._close_cb = callback_method
