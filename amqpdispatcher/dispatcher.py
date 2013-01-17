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
    # Connect to AMQP broker with default connection and authentication
    # settings (assumes broker is on localhost)
    host = os.getenv('RABBITMQ_HOST')
    conn = RabbitConnection(transport='gevent',
                                   host=host,
                                   close_cb=connection_closed_cb,
                                   logger=logging.getLogger())

    # Start message pump
    message_pump_greenlet = gevent.Greenlet(message_pump_greenthread, conn)

    # Create message channel
    channel = conn.channel()
    channel.add_close_listener(channel_closed_cb)

    args = get_args_from_cli()
    config = load(open(args.config).read())

    consumers = [
        ('test_queue', 'amqpdispatcher.example_consumer:consume'),
    ]

    for consumer in config['consumers']:
        queue_name = consumer['queue']
        prefetch_count = consumer.get('prefetch_count', 1)
        consumer_str = consumer.get('consumer')
        consumer_count = consumer.get('consumer_count', 1)

        module_name, obj_name = consumer_str.split(':')
        module = importlib.import_module(module_name)
        consumer_klass = getattr(module, obj_name)
        consume_channel = conn.channel()
        consume_channel.basic.qos(prefetch_count=prefetch_count)
        pool = ConsumerPool(consume_channel, consumer_klass, consumer_count)
        consume_channel.basic.consume(
            queue=queue_name,
            consumer=pool.handle,
            no_ack=False,
        )
        gevent.sleep()

    return message_pump_greenlet


class ConsumerPool(object):
    def __init__(self, channel, klass, size=1):
        self._channel = channel
        self._pool = gevent.queue.Queue()
        self._klass = klass
        for i in range(size):
            self._create()

    def _create(self):
        print 'Creating'
        self._pool.put(self._klass())

    def handle(self, msg):
        def func():
            consumer = self._pool.get()
            amqp_proxy = AMQPProxy(self._channel, msg)

            def put_back(successful_greenlet):
                print 'Success! Putting consumer back'
                self._pool.put(consumer)

            def recreate(failed_greenlet):
                print 'Recreating greenlet because there was a problem'
                try:
                    failed_greenlet.get()
                except Exception as exc:
                    print exc
                    amqp_proxy.reject(requeue=True)
                    consumer.shutdown(exc)
                self._create()

            greenlet = gevent.Greenlet(consumer.consume, amqp_proxy, msg)
            greenlet.link_value(put_back)
            greenlet.link_exception(recreate)
            greenlet.start()

        gevent.spawn(func)

class AMQPProxy(object):

    def __init__(self, channel, msg):
        self._channel = channel
        self._msg = msg

    @property
    def tag(self):
        return self._msg.delivery_info['delivery_tag']

    def ack(self):
        self._channel.basic.ack(self.tag)

    def nack(self):
        self._channel.basic.nack(self.tag)

    def reject(self, requeue=True):
        self._channel.basic.reject(self.tag, requeue=requeue)

    def publish(self, exchange, routing_key, headers, body):
        msg = Message(body, headers)
        self._channel.basic.publish(msg, exchange, routing_key)


def message_pump_greenthread(connection):
    print "Entering Message Pump"
    try:
        while connection is not None:
            # Pump
            connection.read_frames()

            # Yield to other greenlets so they don't starve
            gevent.sleep()
    finally:
        print "Leaving Message Pump"
    return


def main():
    greenlet = setup()
    greenlet.start()
    greenlet.join()


if __name__ == '__main__':
    main()
