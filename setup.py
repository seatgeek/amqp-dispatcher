#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from setuptools import setup

import amqpdispatcher


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def run_setup():
    setup(
        name='amqp-dispatcher',
        version=amqpdispatcher.__version__,
        description='A daemon gevent to run AMQP consumers',
        keywords='amqp',
        url='http://github.com/opschops/amqp-dispatcher',
        author='Jose Diaz-Gonzalez',
        author_email='opschops@josediazgonzalez.com',
        license='BSD',
        packages=['amqpdispatcher'],
        install_requires=[
            'gevent',
            'haigha',
            'pyyaml',
            'pika',
        ],
        test_suite='tests',
        long_description=read('README.rst'),
        zip_safe=True,
        classifiers=[
        ],
        entry_points="""
        [console_scripts]
            amqp-dispatcher=amqpdispatcher.dispatcher:main
        """,
    )

if __name__ == '__main__':
    run_setup()
