# AMQP Dispatcher

A daemon to run AMQP consumers


## Running

    RABBITMQ_HOST=rabbitmq.example.com amqp-dispatcher --config amqp-dispatcher-config.yml

## Consumers

Consumers are a class with 2 required methods: `consume` and `shutdown`. AMQP
Dispatcher will not monkey patch the environment, you will have to do that
yourself.

### `consume`

`consume` is called once for each message being handled. It should take 2
parameters, a proxy for AMQP operations (`amqp`) and the message (`msg`).


### `shutdown`

`shutdown` is called before the instance of the consumer is removed. It takes a
single argument `exception` which may be `None`. If your consumer raises an
exception while consuming the `shutdown` method will be called. Once `shutdown`
is finished a new instance of your consumer will be created to replace the one
that raised the exception. If you would like to rate limit instance replacement
you can call `gevent.sleep(X)` to sleep for `X` seconds after a failure.


### Example

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


## Configuration

AMQP Dispatcher will read environment variable for connection information and a
YAML file for worker configuration.

### Environment Variables

`RABBITMQ_HOST` - Host to connect to!
`RABBITMQ_USER` - Username to connect with
`RABBITMQ_PASS` - Password to connect with

At the moment guest:guest are used to connect, just because I have gotten around to changing it.

### Startup Configuration

If you need to perform custom actions (configure your logging, create initial objects) you can add a startup handler.

This is configured in the config yml with the `startup_handler` option.

    startup_handler: amqpdispatcher.example_startup:startup

### Worker configuration

Workers are autoloaded when AMQP Dispatcher starts. This means your worker must
be importable from the environment.

A complete configuration example would look like:

    consumers:
      - consumer: workers.module:Consumer
        consumer_count: 1
        queue: test_queue
        prefetch_count: 2
      - consumer: workers.module_2:Consumer
        consumer_count: 2
        queue: test_queue_2
        prefetch_count: 10


`prefetch_count` is the AMQP `prefetch_count` when consuming. The
`consumer_count` is the number of instances of your consumer to handle messages
from that queue.  Connection pools are highly recommended.
MySQL will require the [MySQL
Connector](http://pypi.python.org/pypi/mysql-connector-python) instead of
`mysqldb` in order for gevent to switch properly.

Pools can be created and attached to the consumer class during the `__init__`. Example with SQLAlchemy

    class Consumer(object):

        session_maker = None

        def __init__(self):
            self.session = None

            if Consumer._engine is None:
                print 'Creating session maker'
                Consumer._engine = create_engine(...)
                Consumer.sessionmaker = sessionmaker(bind=Consumer._engine)

And then a session created during the consume method.

        def consume(self, proxy, msg):
            session = self.sessionmaker()
            # Do something with the session
            session.close()

# Logging

Logging is performed on the logger `amqp-dispatcher`. The RabbitMQ connection
provided by Haigha will log on `amqp-dispatcher.haigha`.
