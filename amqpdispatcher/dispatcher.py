#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

from amqpdispatcher.dispatcher_haigha import main as main_haigha


def main():
    format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=format)
    return main_haigha()

if __name__ == '__main__':
    main()
