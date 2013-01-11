
import gevent

def consume(*args, **kwargs):
    print 'Consuming message', args, kwargs
    gevent.sleep(3)
    print 'Done sleeping'

