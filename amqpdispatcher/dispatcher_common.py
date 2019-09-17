#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import asyncio
import types
from asyncio import AbstractEventLoop
from typing import Dict, Optional, Type, Awaitable, Callable, Any
import functools
from typing_extensions import Protocol

import aio_pika
import importlib
import logging
import os
import random
import string
import socket
import yaml

import six
from aio_pika import Queue, Channel, RobustConnection, IncomingMessage, Connection
from six.moves.urllib.parse import urlparse

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.message import Message


class DispatcherConsumer(Protocol):
    async def consume(self, amqp_proxy: AMQPProxy, message: Message) -> None:
        ...

    async def shutdown(self, exception: Optional[Exception] = None) -> None:
        ...


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
    created_queues: Dict[str, Queue] = {}

    for queue in queues:
        created_queue = await create_queue(channel, queue)
        created_queues[queue['queue']] = created_queue
        await bind_queue(created_queue, queue)

    return created_queues


def parse_env():
    """returns tuple containing
    HOSTS, USER, PASSWORD, VHOST, HEARTBEAT
    """
    rabbitmq_url = os.getenv('RABBITMQ_URL',
                             'amqp://guest:guest@localhost:5672/')
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

    heartbeat = 0
    return (hosts, user, password, vhost, port, heartbeat, parsed_url)


def load_module(module_name: str) -> types.ModuleType:
    return importlib.import_module(module_name)


def load_consumer(consumer_str: str) -> Type[DispatcherConsumer]:
    logger = logging.getLogger('amqp-dispatcher')
    logger.debug('Loading consumer {0}'.format(consumer_str))
    return load_module_object(consumer_str)


def load_module_object(module_object_str):
    module_name, obj_name = module_object_str.split(':')
    module = load_module(module_name)
    return getattr(module, obj_name)


async def create_consumption_task(connection: Connection, consumer: Any, created_queues: Dict[str, Any]):
    logger = logging.getLogger('amqp-dispatcher')

    queue_name = consumer['queue']
    prefetch_count = consumer.get('prefetch_count', 1)
    consumer_str = consumer.get('consumer')
    # consumer_count = consumer.get('consumer_count', 1)

    consumer_class = load_consumer(consumer_str)

    consume_channel: Channel = await connection.channel()
    publish_channel: Channel = await connection.channel()

    await consume_channel.set_qos(prefetch_count=prefetch_count)

    queue = created_queues[queue_name]

    async with queue.iterator() as queue_iter:
        consumer_instance = consumer_class()
        async for message in queue_iter:
            # ignore_processed=True allows us to manually ack
            # and reject the message without
            # the context manager making the decisions for us.
            async with message.process(ignore_processed=True):
                processed_message: IncomingMessage = message
                logger.info("a message was received, delivery tag: {0}".format(processed_message.delivery_tag))

                wrapped_message = Message(processed_message)
                amqp_proxy = AMQPProxy(wrapped_message, connection, publish_channel)

                try:
                    logger.info("consuming message")
                    await consumer_instance.consume(amqp_proxy, wrapped_message)

                    if not amqp_proxy.has_responded_to_message:
                        await amqp_proxy.ack()

                except Exception as e:
                    logger.error("consuming message error: {0}".format(e))
                    await consumer_instance.shutdown(e)

                    if not amqp_proxy.has_responded_to_message:
                        await amqp_proxy.reject(requeue=True)


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

    connection: RobustConnection = await aio_pika.connect_robust(
        full_url, loop=loop
    )

    if connection is None:
        logger.warning("No connection -- returning")
        return

    channel = await connection.channel()
    queues = config.get('queues')
    created_queues: Dict[str, Queue] = {}
    if queues:
        created_queues = await create_and_bind_queues(channel, queues)

    connection.add_close_callback(create_connection_closed_cb())

    consumer_tasks = []
    for consumer in config.get('consumers', []):
        consumer_tasks.append(
            create_consumption_task(connection, consumer, created_queues)
        )

    await asyncio.gather(*consumer_tasks)