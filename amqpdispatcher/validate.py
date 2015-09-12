#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import sys
import yaml

from amqpdispatcher.dispatcher_common import load_consumer
from amqpdispatcher.dispatcher_common import load_module_object


def validate(config_file):
    logger = logging.getLogger('amqp-dispatcher')
    logger.setLevel(logging.ERROR)
    config = yaml.safe_load(open(config_file).read())
    valid_handler = validate_startup_handler(config)
    valid_consumers = validate_consumers(config)
    if valid_handler and valid_consumers:
        return
    sys.exit(1)


def validate_startup_handler(config):
    startup_handler_str = config.get('startup_handler')
    if startup_handler_str is None:
        return True

    handler = None
    try:
        handler = load_module_object(startup_handler_str)
    except ImportError, e:
        print('[{0}] Invalid startup_handler: {1}'.format(
            startup_handler_str,
            e
        ))
        return False
    except AttributeError, e:
        print('[{0}] Invalid startup_handler: {1}'.format(
            startup_handler_str,
            e
        ))
        return False

    if handler is None:
        print('[{0}] Invalid startup_handler'.format(
            startup_handler_str
        ))
        return False

    return True


def validate_consumers(config):
    consumers = config.get('consumers', None)
    if not consumers:
        print('No consumers specified')
        return False

    is_valid = True
    for consumer in config.get('consumers', []):
        if not is_consumer_valid(consumer):
            is_valid = False
    return is_valid


def is_consumer_valid(consumer):
    is_valid = True
    consumer_str = consumer.get('consumer', None)
    consumer_klass = None
    try:
        consumer_klass = load_consumer(consumer_str)
        if consumer_klass is None:
            print('[{0}] Invalid consumer class'.format(consumer_str))
            is_valid = False
    except ImportError, e:
        print('[{0}] Invalid consumer class: {1}'.format(consumer_str, e))
        is_valid = False
    except AttributeError, e:
        print('[{0}] Invalid consumer class: {1}'.format(consumer_str, e))
        is_valid = False

    queue_name = consumer.get('queue', None)
    if not queue_name:
        print('[{0}] No queue name specified'.format(
            consumer_str
        ))
        is_valid = False

    for key in ['prefetch_count', 'consumer_count']:
        value = consumer.get(key, 1)
        if not isinstance(value, int):
            print('[{0}] {1} must be an integer, found {2}'.format(
                consumer_str,
                key,
                value
            ))
            is_valid = False

    return is_valid
