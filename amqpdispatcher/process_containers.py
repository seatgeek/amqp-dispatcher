"""Manage spawning functions"""

class GeventProcessContainer(object):

    def __init__(self, gevent):
        self.gevent = gevent

    def spawn(self, func):
        self.gevent.spawn(func)
