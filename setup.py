#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from setuptools import setup

import amqpdispatcher


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def run_setup():
    setup(
        name="amqp-dispatcher",
        version=amqpdispatcher.__version__,
        description="A aio_pika daemon to run AMQP consumers",
        keywords="amqp",
        url="http://github.com/seatgeek/amqp-dispatcher",
        author="SeatGeek",
        author_email="hi@seatgeek.com",
        license="BSD",
        packages=["amqpdispatcher"],
        install_requires=["pyyaml", "aio_pika"],
        test_suite="tests",
        long_description=read("README.rst"),
        zip_safe=True,
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Topic :: Communications",
            "Topic :: Internet",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Libraries",
            "Topic :: System :: Networking",
        ],
        entry_points="""
        [console_scripts]
            amqp-dispatcher=amqpdispatcher.dispatcher:main
        """,
    )


if __name__ == "__main__":
    run_setup()
