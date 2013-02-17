#!/usr/bin/env python
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
        keywords = 'amqp',
        url='http://github.com/philipcristiano/amqp-dispatcher',
        author='Philip Cristiano',
        author_email='philipcristiano@gmail.com',
        license='BSD',
        packages=['amqpdispatcher'],
        install_requires=[
            'gevent',
            'haigha',
            'pyyaml',
        ],
        test_suite='tests',
        long_description=read('README.md'),
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
