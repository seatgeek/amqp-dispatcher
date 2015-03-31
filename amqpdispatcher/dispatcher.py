#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import importlib
import logging
import os
import socket
import sys
import urlparse

from haigha.connections.rabbit_connection import RabbitConnection
from haigha.message import Message
from yaml import safe_load as load
import gevent
import gevent.queue

format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=format)
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


def get_connection_params_from_environment():
    """returns tuple containing
    HOSTS, USER, PASSWORD, VHOST
    """
    connection_string = os.getenv('RABBITMQ_URL', None)
    hosts = user = password = vhost = None

    # connection string, all contained
    if connection_string:
        cp = urlparse.urlparse(connection_string)
        hosts_string = cp.hostname
        hosts = hosts_string.split(",")
        if cp.port:
            hosts = [h + ":" + str(cp.port) for h in hosts]
        user = cp.username
        password = cp.password
        vhost = cp.path
        return (hosts, user, password, vhost)

    # find hosts
    hosts_string = os.getenv('RABBITMQ_HOSTS', None)
    if hosts_string:
        hosts = hosts_string.split(",")

    host = os.getenv('RABBITMQ_HOST', None)
    if host:
        hosts = host.split(",")
        if len(hosts) > 1:
            raise Exception("invalid rabbitmq connection info: RABBITMQ_HOST requests a single host, received {}".format(host))

    if hosts is None:
        raise Exception("missing rabbitmq connection info: RABBITMQ_URL, RABBITMQ_HOSTS, or RABBITMQ_HOST is required")

    # find other parameters from env variables
    user = os.getenv('RABBITMQ_USER', 'guest')
    password = os.getenv('RABBITMQ_PASS', 'guest')
    vhost = os.getenv('RABBITMQ_VHOST', '/')
    return hosts, user, password, vhost


def setup():
    args = get_args_from_cli()
    config = load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    hosts, user, password, vhost = get_connection_params_from_environment()
    rabbit_logger = logging.getLogger('amqp-dispatcher.haigha')
    conn = connect_to_hosts(
        RabbitConnection,
        hosts,
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


class ConsumerPool(object):
    def __init__(self, channel, klass, greenlet_maker, size=1):
        self._channel = channel
        self._pool = gevent.queue.Queue()
        self._klass = klass
        self._gm = greenlet_maker
        for i in range(size):
            self._create()

    def _create(self):
        logger.debug('Creating consumer instance: {0}'.format(
            self._klass.__name__
        ))
        self._pool.put(self._klass())

    def handle(self, msg):
        def func():
            consumer = self._pool.get()
            amqp_proxy = AMQPProxy(self._channel, msg)

            def put_back(successful_greenlet):
                logger.debug('Successful run, putting consumer back')
                if not amqp_proxy.has_responded_to_message:
                    amqp_proxy.ack()
                self._pool.put(consumer)

            def recreate(failed_greenlet):
                logger.info('Consume failed, shutting down consumer')
                if not amqp_proxy.has_responded_to_message:
                    amqp_proxy.reject(requeue=True)
                shutdown_greenlet = gevent.Greenlet(
                    consumer.shutdown,
                    failed_greenlet.exception
                )

                def create_wrapper(*args):
                    self._create()
                shutdown_greenlet.link(create_wrapper)
                shutdown_greenlet.start()

            greenlet = self._gm(consumer.consume, amqp_proxy, msg)
            greenlet.link_value(put_back)
            greenlet.link_exception(recreate)
            greenlet.start()
        self._gm(func).start()


class AMQPProxy(object):

    def __init__(self, channel, msg):
        self._channel = channel
        self._msg = msg
        self._terminal_state = False

    @property
    def tag(self):
        return self._msg.delivery_info['delivery_tag']

    @property
    def has_responded_to_message(self):
        return self._terminal_state

    def ack(self):
        self._error_if_already_terminated()
        self._channel.basic.ack(self.tag)

    def nack(self):
        self._error_if_already_terminated()
        self._channel.basic.nack(self.tag)

    def reject(self, requeue=True):
        self._error_if_already_terminated()
        self._channel.basic.reject(self.tag, requeue=requeue)

    def publish(self, exchange, routing_key, headers, body):
        msg = Message(body, headers)
        self._channel.basic.publish(msg, exchange, routing_key)

    def _error_if_already_terminated(self):
        if self._terminal_state:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True


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
