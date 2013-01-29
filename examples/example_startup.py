import logging

def startup():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    ad_logger = logging.getLogger('amqp-dispatcher')
    ad_logger.setLevel(logging.DEBUG)
    ad_logger.addHandler(ch)
