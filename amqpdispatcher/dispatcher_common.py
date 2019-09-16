#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
from asyncio import AbstractEventLoop

import aio_pika
import gevent
import importlib
import inspect
import logging
import os
import random
import string
import socket
import yaml

import six
from aio_pika import Queue, Connection, Channel
from six.moves.urllib.parse import parse_qs, urlparse

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
                        default=('haigha' if six.PY2 else 'pika'),
                        choices=['haigha', 'pika'] if six.PY2 else ['pika'],
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


def create_connection_closed_cb():
    def connection_closed_cb():
        logger = logging.getLogger('amqp-dispatcher')
        logger.info("AMQP broker connection closed; close-info")
    return connection_closed_cb


async def create_queue(channel: Channel, queue) -> Queue:
    """creates a queue synchronously"""
    logger = logging.getLogger('amqp-dispatcher')
    name = queue['queue']
    logger.info("Create queue {0}".format(name))
    durable = bool(queue.get('durable', True))
    auto_delete = bool(queue.get('auto_delete', False))
    exclusive = bool(queue.get('exclusive', False))

    passive = False

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

    queue: Queue = await channel.declare_queue(
        name=name,
        passive=passive,
        exclusive=exclusive,
        durable=durable,
        auto_delete=auto_delete,
        # nowait=nowait,
        arguments=arguments
    )
    log_message = "Queue {0} - {1} messages and {1} consumers connected"
    logger.info(log_message.format(queue.name, queue.declaration_result.message_count, queue.declaration_result.consumer_count))

    return queue


async def bind_queue(created_queue: Queue, queue_spec) -> None:
    """binds a queue to the bindings identified in the doc"""
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug("Binding queue {0}".format(queue_spec))
    bindings = queue_spec.get('bindings')

    name = queue_spec.get('queue')
    for binding in bindings:
        exchange = binding['exchange']
        key = binding['routing_key']
        logger.info("bind {0} to {1}:{2}".format(name, exchange, key))

        await created_queue.bind(exchange, key)


async def create_and_bind_queues(channel: Channel, queues):
    for queue in queues:
        created_queue = await create_queue(channel, queue)
        await bind_queue(created_queue, queue)


def parse_env():
    """returns tuple containing
    HOSTS, USER, PASSWORD, VHOST, HEARTBEAT
    """
    rabbitmq_url = os.getenv('RABBITMQ_URL',
                             'amqp://guest:guest@localhost:5672/')
    hosts = user = password = vhost = None
    port = 5672

    parsed_url = urlparse(rabbitmq_url)
    hosts_string = parsed_url.hostname
    hosts = hosts_string.split(",")
    if parsed_url.port:
        port = int(parsed_url.port)
    user = parsed_url.username
    password = parsed_url.password
    vhost = parsed_url.path
    query = parsed_url.query

    # workaround for bug in 12.04
    if '?' in vhost and query == '':
        vhost, query = vhost.split('?', 1)

    heartbeat = parse_heartbeat(query)
    # Support heartbeat override
    heartbeat_override = os.getenv('RABBITMQ_HEARTBEAT')
    if heartbeat_override:
        heartbeat = int(heartbeat_override)

    return (hosts, user, password, vhost, port, heartbeat, parsed_url)


def parse_heartbeat(query):
    logger = logging.getLogger('amqp-dispatcher')

    default_heartbeat = None
    heartbeat = default_heartbeat
    if query:
        qs = parse_qs(query)
        heartbeat = qs.get('heartbeat', default_heartbeat)
    else:
        logger.debug('No heartbeat specified, using broker defaults')

    if isinstance(heartbeat, (list, tuple)):
        if len(heartbeat) == 0:
            logger.warning('No heartbeat value set, using default')
            heartbeat = default_heartbeat
        elif len(heartbeat) == 1:
            heartbeat = heartbeat[0]
        else:
            logger.warning(
                'Multiple heartbeat values set, using broker default: {0}'
                .format(heartbeat)
            )
            heartbeat = default_heartbeat

    if type(heartbeat) == str and heartbeat.lower() == 'none':
        return None

    if heartbeat is None:
        return heartbeat

    try:
        heartbeat = int(heartbeat)
    except ValueError:
        logger.warning(
            'Unable to cast heartbeat to int, using broker default: {0}'
            .format(heartbeat)
        )
        heartbeat = default_heartbeat

    return heartbeat


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


async def launch_queue(queue: Queue):
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(message.body)

                if queue.name in message.body.decode():
                    break


async def setup(logger_name, loop: AbstractEventLoop):
    logger = logging.getLogger('amqp-dispatcher')

    args = get_args_from_cli()
    config = yaml.safe_load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    random_generator = random.SystemRandom()
    random_string = ''.join([
        random_generator.choice(string.ascii_lowercase) for i in range(10)
    ])
    connection_name = '{0}-{1}-{2}'.format(
        socket.gethostname(),
        os.getpid(),
        random_string,
    )

    full_url = os.getenv('RABBITMQ_URL',
                         'amqp://guest:guest@localhost:5672/')

    connection = await aio_pika.connect_robust(
        full_url, loop=loop
    )

    if connection is None:
        logger.warning("No connection -- returning")
        return

    channel = await connection.channel()
    queues = config.get('queues')
    if queues:
        await create_and_bind_queues(channel, queues)

    connection.add_on_close_callback(create_connection_closed_cb())

    for consumer in config.get('consumers', []):
        queue_name = consumer['queue']
        prefetch_count = consumer.get('prefetch_count', 1)
        consumer_str = consumer.get('consumer')
        consumer_count = consumer.get('consumer_count', 1)

        consumer_klass = load_consumer(consumer_str)
        consume_channel: Channel = await connection.channel()

        consume_channel.basic_consume(
            consumer_callback=pool.handle,
            queue=queue_name,
            no_ack=False,
        )
        gevent.sleep()

    message_pump_greenlet = gevent.Greenlet(
        message_pump_greenthread, conn)

    return message_pump_greenlet
