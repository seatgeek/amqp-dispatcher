#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import importlib
import logging
import os
import socket
import sys
import urlparse

from amqpdispatcher.consumer_pool import ConsumerPool
from haigha.connections.rabbit_connection import RabbitConnection
from yaml import safe_load as load
import gevent
import gevent.queue

if os.getenv('LOGGING_FILE_CONFIG'):
    logging.config.fileConfig(os.getenv('LOGGING_FILE_CONFIG'))
else:
    format = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.DEBUG, format=format, datefmt=datefmt)

logger = logging.getLogger('amqp-dispatcher')


def get_args_from_cli():
    parser = argparse.ArgumentParser(description='Run Graphite Pager')
    parser.add_argument('--config',
                        metavar='config',
                        type=str,
                        default='config.yml',
                        help='path to the config file')

    args = parser.parse_args()
    return args


def channel_closed_cb(ch):
    logger.info("AMQP channel closed; close-info: %s" % (ch.close_info,))
    ch = None
    return


def create_connection_closed_cb(connection):
    def connection_closed_cb():
        logger.info("AMQP broker connection closed; close-info: %s" % (
            connection.close_info,
        ))
    return connection_closed_cb


def connect_to_hosts(connector, hosts, **kwargs):
    for host in hosts:
        logger.info('Trying to connect to host: {0}'.format(host))
        try:
            conn = connector(host=host, **kwargs)
            return conn
        except socket.error:
            logger.info('Error connecting to {0}'.format(host))
    logger.error('Could not connect to any hosts')


def create_queue(connection, queue):
    """creates a queue synchronously"""
    name = queue['queue']
    logger.info("Create queue {}".format(name))
    durable = bool(queue.get('durable', True))
    auto_delete = bool(queue.get('auto_delete', False))
    exclusive = bool(queue.get('exclusive', False))

    passive = False
    nowait = False

    arguments = {}
    queue_args = [
        'x_dead_letter_exchange',
        'x_dead_letter_routing_key',
        'x_max_length',
        'x_expires',
        'x_message_ttl',
    ]

    for queue_arg in queue_args:
        key = queue_arg.replace('_', '-')
        if queue.get(queue_arg):
            arguments[key] = queue.get(queue_arg)

    ch = connection.channel(synchronous=True)
    ret = ch.queue.declare(
        queue=name,
        passive=passive,
        exclusive=exclusive,
        durable=durable,
        auto_delete=auto_delete,
        nowait=nowait,
        arguments=arguments
    )
    name, message_count, consumer_count = ret
    log_message = "Queue {} - presently {} messages and {} consumers connected"
    logger.info(log_message.format(name, message_count, consumer_count))


def bind_queue(connection, queue):
    """binds a queue to the bindings identified in the doc"""
    bindings = queue.get('bindings')
    ch = connection.channel(synchronous=True)
    name = queue.get('queue')
    for binding in bindings:
        exchange = binding['exchange']
        key = binding['routing_key']
        logger.info("bind {} to {}:{}".format(name, exchange, key))
        ch.queue.bind(name, exchange, key, nowait=False)


def create_and_bind_queues(connection, queues):
    for queue in queues:
        create_queue(connection, queue)
        bind_queue(connection, queue)


def parse_url():
    """returns tuple containing
    HOSTS, USER, PASSWORD, VHOST
    """
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost/')
    hosts = user = password = vhost = None
    port = 5672

    cp = urlparse.urlparse(rabbitmq_url)
    hosts_string = cp.hostname
    hosts = hosts_string.split(",")
    if cp.port:
        port = int(cp.port)
    user = cp.username
    password = cp.password
    vhost = cp.path
    return (hosts, user, password, vhost, port)


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


def load_module(module_name):
    return importlib.import_module(module_name)


def load_consumer(consumer_str):
    logger.debug('Loading consumer {0}'.format(consumer_str))
    return load_module_object(consumer_str)


def load_module_object(module_object_str):
    module_name, obj_name = module_object_str.split(':')
    module = load_module(module_name)
    return getattr(module, obj_name)


def message_pump_greenthread(connection):
    logging.debug('Starting message pump')
    exit_code = 0
    try:
        while connection is not None:
            # Pump
            connection.read_frames()

            # Yield to other greenlets so they don't starve
            gevent.sleep()
    except Exception:
        logger.exception("error in message pump thread")
        exit_code = 1
    finally:
        logging.debug('Leaving message pump')
    return exit_code


def main():
    greenlet = setup()
    if greenlet is not None:
        greenlet.start()
        greenlet.join()
        sys.exit(greenlet.get())


if __name__ == '__main__':
    main()
