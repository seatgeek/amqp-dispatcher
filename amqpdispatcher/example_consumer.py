import random

import gevent


class Consumer(object):

    def __init__(self):
        self.init_msg = "I've been initiliazed"

    def consume(self, amqp, msg):
        print 'Consuming message', msg.body
        gevent.sleep(1)
        val = random.random()
        if val > .8:
            print 'publishing'
            amqp.publish('test_exchange', 'test_routing_key', {}, 'New body!')
        if val < .5:
            raise ValueError()
        print 'Done sleeping'
        amqp.ack()

    def shutdown(self, exception=None):
        print 'Shut down'
