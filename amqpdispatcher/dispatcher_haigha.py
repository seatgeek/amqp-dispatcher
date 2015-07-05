#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import socket
import sys

from amqpdispatcher.dispatcher_common import channel_closed_cb
from amqpdispatcher.dispatcher_common import create_and_bind_queues
from amqpdispatcher.dispatcher_common import create_connection_closed_cb
from amqpdispatcher.dispatcher_common import get_args_from_cli
from amqpdispatcher.dispatcher_common import load_consumer
from amqpdispatcher.dispatcher_common import load_module_object
from amqpdispatcher.dispatcher_common import message_pump_greenthread
from amqpdispatcher.dispatcher_common import parse_url
from amqpdispatcher.consumer_pool import ConsumerPool
from haigha.connections.rabbit_connection import RabbitConnection
from yaml import safe_load as load
import gevent
import gevent.queue

format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=format)
logger = logging.getLogger('amqp-dispatcher')


def connect_to_hosts(connector, hosts, **kwargs):
    for host in hosts:
        logger.info('Trying to connect to host: {0}'.format(host))
        try:
            conn = connector(host=host, **kwargs)
            return conn
        except socket.error:
            logger.info('Error connecting to {0}'.format(host))
    logger.error('Could not connect to any hosts')


def setup():
    args = get_args_from_cli()
    config = load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    hosts, user, password, vhost, port = parse_url()
    rabbit_logger = logging.getLogger('amqp-dispatcher.haigha')
    conn = connect_to_hosts(
        RabbitConnection,
        hosts,
        port=port,
        transport='gevent',
        user=user,
        password=password,
        vhost=vhost,
        logger=rabbit_logger
    )
    if conn is None:
        logger.warning("No connection -- returning")
        return

    queues = config.get('queues')
    if queues:
        create_and_bind_queues(conn, queues)

    conn._close_cb = create_connection_closed_cb(conn)

    # Create message channel
    channel = conn.channel()
    channel.add_close_listener(channel_closed_cb)

    for consumer in config['consumers']:
        queue_name = consumer['queue']
        prefetch_count = consumer.get('prefetch_count', 1)
        consumer_str = consumer.get('consumer')
        consumer_count = consumer.get('consumer_count', 1)

        consumer_klass = load_consumer(consumer_str)
        consume_channel = conn.channel()
        consume_channel.basic.qos(prefetch_count=prefetch_count)
        pool = ConsumerPool(
            consume_channel,
            consumer_klass,
            gevent.Greenlet,
            consumer_count
        )

        consume_channel.basic.consume(
            queue=queue_name,
            consumer=pool.handle,
            no_ack=False,
        )
        gevent.sleep()

    message_pump_greenlet = gevent.Greenlet(
        message_pump_greenthread, conn)

    return message_pump_greenlet


def main():
    greenlet = setup()
    if greenlet is not None:
        greenlet.start()
        greenlet.join()
        sys.exit(greenlet.get())


if __name__ == '__main__':
    main()
