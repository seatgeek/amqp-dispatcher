import logging


def startup():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)

    ch.setFormatter(formatter)
    ad_logger = logging.getLogger('amqp-dispatcher')
    ad_logger.setLevel(logging.DEBUG)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)
