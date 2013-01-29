import time

from haigha.connection import Connection
from haigha.message import Message

connection = Connection(
  user='guest', password='guest',
  vhost='/', host='33.33.33.10',
  heartbeat=None, debug=True)

ch = connection.channel()
ch.exchange.declare('test_exchange', 'direct')
ch.queue.declare('test_queue', auto_delete=False)
ch.queue.bind('test_queue', 'test_exchange', 'test_key')
while True:
    ch.basic.publish( Message('body', application_headers={'hello':'world'}),
      'test_exchange', 'test_key' )
    time.sleep(1)
