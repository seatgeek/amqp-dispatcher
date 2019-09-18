#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import asyncio
import types
from asyncio import AbstractEventLoop
from typing import Dict, Optional, Type, Any
from typing_extensions import Protocol

import aio_pika
import importlib
import logging
import os
import random
import string
import yaml

import six
from aio_pika import Queue, Channel, RobustConnection, IncomingMessage, Connection

from amqpdispatcher.amqp_proxy import AMQPProxy
from amqpdispatcher.environment import Environment
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
    logger.info(
        log_message.format(queue.name, queue.declaration_result.message_count, queue.declaration_result.consumer_count))

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


async def create_and_bind_queues(connection: Connection, queues):
    created_queues: Dict[str, Queue] = {}

    for queue in queues:
        # We create one connection for each queue
        channel = await connection.channel()
        created_queue = await create_queue(channel, queue)
        created_queues[queue['queue']] = created_queue
        await bind_queue(created_queue, queue)

    return created_queues


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


async def consumption_coroutine(consumer_pool: asyncio.Queue, amqp_proxy: AMQPProxy, wrapped_message: Message):
    logger = logging.getLogger('amqp-dispatcher')

    # Block until we get a free consumer instance
    consumer_instance = await consumer_pool.get()

    try:
        logger.info("Consumption Coroutine: consuming message")
        await consumer_instance.consume(amqp_proxy, wrapped_message)

        if not amqp_proxy.has_responded_to_message:
            await amqp_proxy.ack()

    except Exception as e:
        logger.error("Consumption Coroutine: consuming message error: {0}".format(e))
        await consumer_instance.shutdown(e)

        if not amqp_proxy.has_responded_to_message:
            await amqp_proxy.reject(requeue=True)

    finally:
        await consumer_pool.put(consumer_instance)


async def create_consumption_task(connection: Connection, consumer: Any, created_queues: Dict[str, Any],
                                  connection_name: str):
    """
    A consumption task fulfills a specification for a consumer entry in the
    consumers section of the YAML. Note that a consumption task may specify that
    multiple consumers be used. The consumer pool is handled by the
    consumer loop.
    :param connection:
    :param consumer:
    :param created_queues:
    :param connection_name:
    :return:
    """
    logger = logging.getLogger('amqp-dispatcher')

    queue_name = consumer['queue']
    prefetch_count = consumer.get('prefetch_count', 1)
    consumer_str = consumer.get('consumer')
    consumer_count = consumer.get('consumer_count', 1)

    consumer_class = load_consumer(consumer_str)

    # Consumers can use the AMQP proxy to publish messages. This
    # is a dedicated channel for that purpose
    publish_channel: Channel = await connection.channel()
    queue: Queue = created_queues[queue_name]

    consumer_pool = asyncio.Queue(maxsize=consumer_count)

    # Create a pool of consumers
    for i in range(0, consumer_count):
        await consumer_pool.put(consumer_class())

    random_generator = random.SystemRandom()
    random_string = ''.join([
        random_generator.choice(string.ascii_lowercase) for _ in range(10)
    ])

    async with queue.iterator(consumer_tag="{0} [{1}] {2}".format(connection_name, consumer_str, random_string)) as queue_iterator:
        async for message in queue_iterator:
            # ignore_processed=True allows us to manually acknowledge
            # and reject messages without the context manager
            # making the decisions for us.
            processed_message: IncomingMessage = message
            logger.info("a message was received with delivery tag: {0}".format(processed_message.delivery_tag))

            wrapped_message = Message(processed_message)
            amqp_proxy = AMQPProxy(wrapped_message, connection, publish_channel)

            # We do not want the processing of a single message to block other available
            # consumers in the pool from being able to process other incoming messages.
            # Therefore, we schedule this without blocking control flow.
            # The consumption coroutine is responsible for putting the
            # consumer instance back on the queue when it is done.
            asyncio.ensure_future(consumption_coroutine(
                consumer_pool,
                amqp_proxy,
                wrapped_message
            ))


async def initialize_dispatcher(loop: AbstractEventLoop):
    logger = logging.getLogger('amqp-dispatcher')

    args = get_args_from_cli()
    config = yaml.safe_load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    environment = Environment.create()

    connection_name = '{0}.{1}'.format(
        environment.nomad_job_name,
        environment.nomad_alloc_id,
    )

    full_url = os.getenv('RABBITMQ_URL',
                         'amqp://guest:guest@localhost:5672/')

    connection: RobustConnection = await aio_pika.connect_robust(
        full_url, loop=loop, client_properties={
            "connection_name": connection_name
        }, connection_name=connection_name
    )

    if connection is None:
        logger.warning("No connection -- returning")
        return

    queues = config.get('queues')
    created_queues: Dict[str, Queue] = {}
    if queues:
        created_queues = await create_and_bind_queues(connection, queues)

    connection.add_close_callback(create_connection_closed_cb())

    consumer_tasks = []
    for consumer in config.get('consumers', []):
        consumer_tasks.append(
            create_consumption_task(connection, consumer, created_queues, connection_name)
        )

    await asyncio.gather(*consumer_tasks)
