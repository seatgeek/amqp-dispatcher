
import gevent

def consume(ack, msg):
    print 'Consuming message', msg.body
    gevent.sleep(3)
    print 'Done sleeping'
    ack()
