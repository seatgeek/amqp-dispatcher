import logging
import sys


def getLogger(name, level=logging.DEBUG, fmt=None, datefmt=None):
    fmt = fmt or "[%(asctime)s] %(name)s [pid:%(process)d] - %(levelname)s - %(message)s"
    datefmt = datefmt or "%Y-%m-%d %H:%M:%S"

    std_out_handler = logging.StreamHandler(sys.stdout)
    std_out_handler.setLevel(level)
    std_out_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    logger = logging.getLogger(name)
    logger.addHandler(std_out_handler)
    return logger
