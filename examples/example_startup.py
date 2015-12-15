import logging


def startup():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logformat = "[%(asctime)s] %(name)s [pid:%(process)d] - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(logformat, datefmt=datefmt)

    ch.setFormatter(formatter)
    ad_logger = logging.getLogger('amqp-dispatcher')
    ad_logger.setLevel(logging.DEBUG)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)
