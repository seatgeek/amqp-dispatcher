#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import socket
import sys

import six

from amqpdispatcher.dispatcher_common import setup
if six.PY2:
    from haigha.connections.rabbit_connection import RabbitConnection
else:
    # haigha is not yet python 3 compatible.
    RabbitConnection = None


def connect_to_hosts(connector, hosts, **kwargs):
    logger = logging.getLogger('amqp-dispatcher')

    for host in hosts:
        logger.info('Trying to connect to host: {0}'.format(host))
        try:
            return connector(host=host, **kwargs)
        except socket.error:
            logger.info('Error connecting to {0}'.format(host))
    logger.error('Could not connect to any hosts')


def main():
    if six.PY3:
        raise NotImplementedError(
            'haigha currently does not support python 3, please use pika.'
        )

    greenlet = setup('amqp-dispatcher.haigha',
                     RabbitConnection,
                     connect_to_hosts)
    if greenlet is not None:
        greenlet.start()
        greenlet.join()
        sys.exit(greenlet.get())


if __name__ == '__main__':
    main()
