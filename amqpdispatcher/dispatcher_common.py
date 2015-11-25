#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import gevent
import importlib
import inspect
import logging
import os
import urlparse
import yaml

from amqpdispatcher.channel_proxy import proxy_channel
from amqpdispatcher.connection_proxy import proxy_connection
from amqpdispatcher.consumer_pool import ConsumerPool


def get_args_from_cli():
    parser = argparse.ArgumentParser(description='Run Graphite Pager')
    parser.add_argument('--config',
                        metavar='config',
                        type=str,
                        default='config.yml',
                        help='path to the config file')

    parser.add_argument('--connection',
                        metavar='connection',
                        type=str,
                        default='haigha',
                        choices=['haigha', 'pika'],
                        help='type of connection to use')

    parser.add_argument('--validate',
                        dest='validate',
                        action='store_true',
                        default=False,
                        help='validate the config.yml file')
    args = parser.parse_args()
    return args


def channel_closed_cb(ch, reply_code=None, reply_text=None):
    info = '[{0}] {1}'.format(reply_code, reply_text)
    if reply_text is None:
        info = ch.close_info

    logger = logging.getLogger('amqp-dispatcher')
    logger.info("AMQP channel closed; close-info: {0}".format(info))
    ch = None
    return


def create_connection_closed_cb(connection):
    def connection_closed_cb():
        logger = logging.getLogger('amqp-dispatcher')
        logger.info("AMQP broker connection closed; close-info: %s" % (
            connection.close_info,
        ))
    return connection_closed_cb


def create_queue(connection, queue):
    """creates a queue synchronously"""
    logger = logging.getLogger('amqp-dispatcher')
    name = queue['queue']
    logger.info("Create queue {0}".format(name))
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

    connection = proxy_connection(connection)
    ch = connection.channel(synchronous=True)
    ch = proxy_channel(ch)
    ret = ch.queue_declare(
        queue=name,
        passive=passive,
        exclusive=exclusive,
        durable=durable,
        auto_delete=auto_delete,
        nowait=nowait,
        arguments=arguments
    )
    name, message_count, consumer_count = ret
    log_message = "Queue {0} - {1} messages and {1} consumers connected"
    logger.info(log_message.format(name, message_count, consumer_count))


def bind_queue(connection, queue):
    """binds a queue to the bindings identified in the doc"""
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug("Binding queue {0}".format(queue))
    bindings = queue.get('bindings')
    connection = proxy_connection(connection)
    ch = connection.channel(synchronous=True)
    ch = proxy_channel(ch)
    arg_spec = inspect.getargspec(ch.queue_bind)
    name = queue.get('queue')
    for binding in bindings:
        exchange = binding['exchange']
        key = binding['routing_key']
        logger.info("bind {0} to {1}:{2}".format(name, exchange, key))
        if 'nowait' in arg_spec.args:
            ch.queue_bind(name, exchange, key, nowait=False)
        else:
            ch.queue_bind(name, exchange, key)


def create_and_bind_queues(connection, queues):
    for queue in queues:
        create_queue(connection, queue)
        bind_queue(connection, queue)


def parse_url():
    """returns tuple containing
    HOSTS, USER, PASSWORD, VHOST
    """
    rabbitmq_url = os.getenv('RABBITMQ_URL',
                             'amqp://guest:guest@localhost:5672/')
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


def load_module(module_name):
    return importlib.import_module(module_name)


def load_consumer(consumer_str):
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug('Loading consumer {0}'.format(consumer_str))
    return load_module_object(consumer_str)


def load_module_object(module_object_str):
    module_name, obj_name = module_object_str.split(':')
    module = load_module(module_name)
    return getattr(module, obj_name)


def message_pump_greenthread(connection):
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug('Starting message pump')
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
        logger.debug('Leaving message pump')
    return exit_code


def setup(logger_name, connector, connect_to_hosts):
    logger = logging.getLogger('amqp-dispatcher')

    args = get_args_from_cli()
    config = yaml.safe_load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    hosts, user, password, vhost, port = parse_url()
    rabbit_logger = logging.getLogger(logger_name)
    rabbit_logger.setLevel(logging.INFO)
    conn = connect_to_hosts(
        connector,
        hosts,
        port=port,
        transport='gevent',
        user=user,
        password=password,
        vhost=vhost,
        logger=rabbit_logger,
    )
    if conn is None:
        logger.warning("No connection -- returning")
        return

    queues = config.get('queues')
    if queues:
        create_and_bind_queues(conn, queues)

    conn = proxy_connection(conn)
    conn.add_on_close_callback(create_connection_closed_cb(conn))

    # Create message channel
    channel = conn.channel()
    channel = proxy_channel(channel)
    channel.add_close_listener(channel_closed_cb)

    for consumer in config.get('consumers', []):
        queue_name = consumer['queue']
        prefetch_count = consumer.get('prefetch_count', 1)
        consumer_str = consumer.get('consumer')
        consumer_count = consumer.get('consumer_count', 1)

        consumer_klass = load_consumer(consumer_str)
        consume_channel = conn.channel()
        consume_channel = proxy_channel(consume_channel)
        consume_channel.basic_qos(prefetch_count=prefetch_count)
        pool = ConsumerPool(
            consume_channel,
            consumer_klass,
            gevent.Greenlet,
            consumer_count
        )

        consume_channel.basic_consume(
            consumer_callback=pool.handle,
            queue=queue_name,
            no_ack=False,
        )
        gevent.sleep()

    message_pump_greenlet = gevent.Greenlet(
        message_pump_greenthread, conn)

    return message_pump_greenlet
