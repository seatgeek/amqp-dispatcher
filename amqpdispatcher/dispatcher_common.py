#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import gevent
import importlib
import logging
import os
import urlparse

from amqpdispatcher.channel_proxy import wrap_channel
from amqpdispatcher.connection_proxy import wrap_connection


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
    logger = logging.getLogger('amqp-dispatcher')
    logger.info("AMQP channel closed; close-info: {0}".format(ch.close_info))
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

    connection = wrap_connection(connection)
    ch = connection.channel(synchronous=True)
    ch = wrap_channel(ch)
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
    log_message = "Queue {} - presently {} messages and {} consumers connected"
    logger.info(log_message.format(name, message_count, consumer_count))


def bind_queue(connection, queue):
    """binds a queue to the bindings identified in the doc"""
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug("Binding queue {}".format(queue))
    bindings = queue.get('bindings')
    connection = wrap_connection(connection)
    ch = connection.channel(synchronous=True)
    ch = wrap_channel(ch)
    name = queue.get('queue')
    for binding in bindings:
        exchange = binding['exchange']
        key = binding['routing_key']
        logger.info("bind {} to {}:{}".format(name, exchange, key))
        ch.queue_bind(name, exchange, key, nowait=False)


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
