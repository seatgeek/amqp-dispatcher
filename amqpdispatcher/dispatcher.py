#!/usr/bin/env python
#-*- coding:utf-8 -*-
import importlib
import logging

import gevent

from haigha.connection import Connection as haigha_Connection
from haigha.message import Message

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
    conn = haigha_Connection(transport='gevent',
                                   host='33.33.33.10',
                                   close_cb=connection_closed_cb,
                                   logger=logging.getLogger())

    # Start message pump
    message_pump_greenlet = gevent.Greenlet(message_pump_greenthread, conn)

    # Create message channel
    channel = conn.channel()
    channel.add_close_listener(channel_closed_cb)

    # Create and configure message exchange and queue
    channel.exchange.declare('test_exchange', 'direct')
    channel.queue.declare('test_queue', auto_delete=False)
    channel.queue.bind('test_queue', 'test_exchange', 'test_routing_key')
    consumers = [
        ('test_queue', 'amqpdispatcher.example_consumer:consume'),
        ('test_queue', 'amqpdispatcher.example_consumer:consume'),
    ]

    def create_consume_wrapper(channel, func):
        def wrapper(msg):
            def ack():
                tag = msg.delivery_info['delivery_tag']
                channel.basic.ack(tag)
                print 'Acked'
            gevent.spawn(func, ack, msg)
        return wrapper

    for queue_name, consumer_str in consumers:
        module_name, func_name = consumer_str.split(':')
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        consume_channel = conn.channel()
        consume_channel.basic.qos(prefetch_count=2)
        callback = create_consume_wrapper(consume_channel, func)
        consume_channel.basic.consume(
            queue=queue_name,
            consumer=callback,
            no_ack=False,
        )
        print 'Channel!'
        gevent.sleep()


    # Publish a message on the channel
    msg = Message('body', application_headers={'hello':'world'})
    print "Publising message: %s" % (msg,)
    channel.basic.publish(msg, 'test_exchange', 'test_routing_key')
    channel.basic.publish(msg, 'test_exchange', 'test_routing_key')
    channel.basic.publish(msg, 'test_exchange', 'test_routing_key')
    channel.basic.publish(msg, 'test_exchange', 'test_routing_key')
    return conn, channel, message_pump_greenlet



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


def handle_incoming_messages(msg):
    print
    print "Received message: %s" % (msg,)
    print

    # Initiate graceful closing of the channel
    channel.basic.cancel(consumer=handle_incoming_messages)
    channel.close()
    return



conn, channel, greenlet = setup()
greenlet.start()
greenlet.join()
