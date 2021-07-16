#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from typing import Dict, Any

import yaml

from amqpdispatcher.dispatcher_common import load_consumer
from amqpdispatcher.dispatcher_common import load_module_object
from amqpdispatcher.logging import getLogger

logger = getLogger(__name__)


def validate(config_file: str) -> None:
    config = yaml.safe_load(open(config_file).read())
    valid_handler = validate_startup_handler(config)
    valid_consumers = validate_consumers(config)
    if valid_handler and valid_consumers:
        return
    sys.exit(1)


def validate_startup_handler(config: Dict[str, Any]) -> bool:
    startup_handler_str = config.get("startup_handler")
    if startup_handler_str is None:
        return True

    handler = None
    try:
        handler = load_module_object(startup_handler_str)
    except ImportError as e:
        logger.error("[{0}] Invalid startup_handler: {1}".format(startup_handler_str, e))
        return False
    except AttributeError as e:
        logger.error("[{0}] Invalid startup_handler: {1}".format(startup_handler_str, e))
        return False

    if handler is None:
        logger.error("[{0}] Invalid startup_handler".format(startup_handler_str))
        return False

    return True


def validate_consumers(config: Dict[str, Any]) -> bool:
    consumers = config.get("consumers", None)
    if not consumers:
        logger.error("No consumers specified")
        return False

    is_valid = True
    for consumer in config.get("consumers", []):
        if not is_consumer_valid(consumer):
            is_valid = False
    return is_valid


def is_consumer_valid(consumer: Dict[str, Any]) -> bool:
    is_valid = True
    consumer_str = consumer.get("consumer", None)
    consumer_klass = None
    try:
        consumer_klass = load_consumer(consumer_str)
        if consumer_klass is None:
            logger.error("[{0}] Invalid consumer class".format(consumer_str))
            is_valid = False
    except ImportError as e:
        logger.error("[{0}] Invalid consumer class: {1}".format(consumer_str, e))
        is_valid = False
    except AttributeError as e:
        logger.error("[{0}] Invalid consumer class: {1}".format(consumer_str, e))
        is_valid = False

    queue_name = consumer.get("queue", None)
    if not queue_name:
        logger.error("[{0}] No queue name specified".format(consumer_str))
        is_valid = False

    for key in ["prefetch_count", "consumer_count"]:
        value = consumer.get(key, 1)
        if not isinstance(value, int):
            logger.error(
                "[{0}] {1} must be an integer, found {2}".format(
                    consumer_str, key, value
                )
            )
            is_valid = False

    return is_valid
