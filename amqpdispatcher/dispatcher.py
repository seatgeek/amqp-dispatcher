#!/usr/bin/env python
#-*- coding:utf-8 -*-
import argparse
import importlib
import logging
import os
from yaml import load

import gevent
import gevent.queue
from haigha.connection import Connection as haigha_Connection
from haigha.connections import RabbitConnection
from haigha.message import Message

logger = logging.getLogger('amqp-dispatcher')
logger.addHandler(logging.NullHandler())

def get_args_from_cli():
    parser = argparse.ArgumentParser(description='Run Graphite Pager')
    parser.add_argument('--config', metavar='config', type=str,  default='config.yml', help='path to the config file')

    args = parser.parse_args()
    return args

def channel_closed_cb(ch):
    print "AMQP channel closed; close-info: %s" % (
      ch.close_info,)
    ch = None
    return

def connection_closed_cb():
    print "AMQP broker connection closed; close-info: %s" % (
      connection.close_info,)
    connection = None
    return

def setup():
    args = get_args_from_cli()
    config = load(open(args.config).read())

    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is not None:
        startup_handler = load_module_object(startup_handler_str)
        startup_handler()
        logger.info('Startup handled')

    # Connect to AMQP broker with default connection and authentication
    # settings (assumes broker is on localhost)
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    user = os.getenv('RABBITMQ_USER', 'guest')
    password = os.getenv('RABBITMQ_PASS', 'guest')
    rabbit_logger = logging.getLogger('amqp-dispatcher.haigha')
    logger.info('Connecting to host {}'.format(host))
    conn = RabbitConnection(transport='gevent',
                                   host=host,
                                   user=user,
                                   password=password,
                                   close_cb=connection_closed_cb,
                                   logger=rabbit_logger)

    # Start message pump
    message_pump_greenlet = gevent.Greenlet(message_pump_greenthread, conn)

    # Create message channel
    channel = conn.channel()
    channel.add_close_listener(channel_closed_cb)


    consumers = [
        ('test_queue', 'amqpdispatcher.example_consumer:consume'),
    ]

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

    return message_pump_greenlet

def load_module(module_name):
    return importlib.import_module(module_name)

def load_consumer(consumer_str):
    logger.debug('Loading consumer {}'.format(consumer_str))
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
        logger.debug('Creating consumer instance: {}'.format(self._klass.__name__))
        self._pool.put(self._klass())

    def handle(self, msg):
        def func():
            consumer = self._pool.get()
            amqp_proxy = AMQPProxy(self._channel, msg)

            def put_back(successful_greenlet):
                logger.debug('Successful run, putting consumer back')
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
        if self._terminal_state == True:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True


def message_pump_greenthread(connection):
    logging.debug('Starting message pump')
    try:
        while connection is not None:
            # Pump
            connection.read_frames()

            # Yield to other greenlets so they don't starve
            gevent.sleep()
    finally:
        logging.debug('Leaving message pump')
    return


def main():
    greenlet = setup()
    greenlet.start()
    greenlet.join()


if __name__ == '__main__':
    main()
