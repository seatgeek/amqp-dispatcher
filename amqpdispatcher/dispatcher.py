#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

from amqpdispatcher.dispatcher_common import get_args_from_cli
from amqpdispatcher.dispatcher_haigha import main as main_haigha
from amqpdispatcher.dispatcher_pika import main as main_pika
from amqpdispatcher.validate import validate


def main():
    format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=format)

    args = get_args_from_cli()
    if args.validate:
        return validate(args.config)

    logger = logging.getLogger('amqp-dispatcher')
    logger.info('Connection: {0}'.format(args.connection))
    if args.connection == 'pika':
        return main_pika()
    return main_haigha()

if __name__ == '__main__':
    main()
