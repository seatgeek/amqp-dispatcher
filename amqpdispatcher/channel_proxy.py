#!/usr/bin/env python
# -*- coding:utf-8 -*-

import inspect

from haigha.message import Message


def proxy_channel(channel):
    klass = '{0}.{1}'.format(channel.__module__, channel.__class__.__name__)
    if klass == 'pika.adapters.blocking_connection.BlockingChannel':
        return PikaChannelProxy(channel)
    if klass == 'pika.channel.Channel':
        return PikaChannelProxy(channel)
    if klass == 'haigha.channel.Channel':
        return HaighaChannelProxy(channel)
    return channel


class ChannelProxy(object):
    def __init__(self, channel):
        self._channel = channel

    def __getattr__(self, method_name):
        method = getattr(self._channel, method_name, None)
        if method:
            return method
        raise AttributeError(method_name)


class PikaChannelProxy(ChannelProxy):
    def add_close_listener(self, callback):
        pass

    def queue_declare(self, callback=None, queue='', passive=False,
                      durable=False, exclusive=False, auto_delete=False,
                      nowait=False, arguments=None, ticket=None):
        kwargs = {
            'queue': queue,
            'passive': passive,
            'durable': durable,
            'exclusive': exclusive,
            'auto_delete': auto_delete,
            'arguments': arguments
        }

        arg_spec = inspect.getargspec(self._channel.queue_declare)
        if 'nowait' in arg_spec.args:
            kwargs['nowait'] = nowait

        ret = self._channel.queue_declare(**kwargs)
        name = ret.method.queue
        message_count = ret.method.message_count
        consumer_count = ret.method.consumer_count
        return name, message_count, consumer_count


class HaighaChannelProxy(ChannelProxy):
    def basic_ack(self, delivery_tag=0, multiple=False):
        return self._channel.basic.ack(delivery_tag=delivery_tag,
                                       multiple=multiple)

    def basic_nack(self, delivery_tag=None, multiple=False, requeue=True):
        return self._channel.basic.nack(delivery_tag=delivery_tag,
                                        requeue=requeue)

    def basic_publish(self, exchange, routing_key, body,
                      properties=None, mandatory=False, immediate=False,
                      ticket=None):
        msg = Message(body, properties)
        return self._channel.basic.publish(msg,
                                           exchange=exchange,
                                           routing_key=routing_key,
                                           mandatory=mandatory,
                                           immediate=immediate,
                                           ticket=None)

    def basic_reject(self, delivery_tag=None, requeue=True):
        return self._channel.basic.reject(delivery_tag=delivery_tag,
                                          requeue=requeue)

    def basic_qos(self, prefetch_size=0, prefetch_count=0, all_channels=False):
        return self._channel.basic.qos(prefetch_size=prefetch_size,
                                       prefetch_count=prefetch_count,
                                       is_global=all_channels)

    def basic_consume(self,
                      consumer_callback,
                      queue='',
                      no_ack=False,
                      exclusive=False,
                      consumer_tag=None,
                      arguments=None):
        if arguments is None:
            arguments = {}

        no_local = arguments.get('no_local', False)
        nowait = arguments.get('nowait', True)
        ticket = arguments.get('ticket', None)
        cb = arguments.get('cb', None)
        if consumer_tag is None:
            consumer_tag = ''
        return self._channel.basic.consume(consumer=consumer_callback,
                                           queue=queue,
                                           no_ack=no_ack,
                                           exclusive=exclusive,
                                           consumer_tag=consumer_tag,
                                           no_local=no_local,
                                           nowait=nowait,
                                           ticket=ticket,
                                           cb=cb)

    def queue_declare(self, callback=None, queue='', passive=False,
                      durable=False, exclusive=False, auto_delete=False,
                      nowait=False, arguments=None, ticket=None):
        if arguments is None:
            arguments = {}

        return self._channel.queue.declare(queue=queue,
                                           passive=passive,
                                           durable=durable,
                                           exclusive=exclusive,
                                           auto_delete=auto_delete,
                                           nowait=nowait,
                                           arguments=arguments,
                                           ticket=ticket,
                                           cb=callback)

    def queue_bind(self, queue, exchange, routing_key=None, nowait=False,
                   arguments=None, ticket=None, callback=None):
        if routing_key is None:
            routing_key = ''
        if arguments is None:
            arguments = {}

        return self._channel.queue.bind(queue,
                                        exchange,
                                        routing_key=routing_key,
                                        nowait=nowait,
                                        arguments=arguments,
                                        ticket=ticket,
                                        cb=callback)
