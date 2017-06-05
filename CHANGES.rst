Changelog
=========

0.9.1 (2017-06-04)
------------------

Fix
~~~

- Install version-level dependencies before global. [Jose Diaz-Gonzalez]

- Pin gevent to 1.1 for python 2.6. [Jose Diaz-Gonzalez]

0.9.0 (2017-06-05)
------------------

- Use client_properties to set the management ui `connection_name` [Jose
  Diaz-Gonzalez]

  The consumer_name is based upon the following bits:

  - the hostname of the server amqp-dispatcher is running on
  - the process id
  - a random string made of only ascii characters

  This can be used to more easily figure out where consumers are in your infrastructure.


0.8.1 (2016-10-31)
------------------

- Use correct grep call for git 2.0. [Jose Diaz-Gonzalez]

- Feat: add editorconfig. [Jose Diaz-Gonzalez]

- Pull down all keys when updating local copy. [Jose Diaz-Gonzalez]

0.8.0 (2016-02-23)
------------------

- Workaround for urlparse bug in Python 2.7.3. [Jose Diaz-Gonzalez]

  Apparently the querystring portion isn't respected, causing the vhost to be set to `/?whatever=querystring&is=set`. This breaks heartbeat parsing support on at least Ubuntu 12.04.


0.7.1 (2016-02-22)
------------------

- Fix handling of heartbeat for pika dispatcher. [Jose Diaz-Gonzalez]

0.7.0 (2016-02-18)
------------------

- Respect heartbeat settings from RABBITMQ_URL environment variable.
  [Jose Diaz-Gonzalez]

  This also reverts 17829d5, which was caused by incorrect documentation of the haigha library. Instead, we properly default to respecting the heartbeat from the client, and also allow users to override this via the RABBITMQ_URL


0.6.0 (2016-02-16)
------------------

- Respect heartbeat settings from server when using the haigha
  dispatcher. [Jose Diaz-Gonzalez]

0.5.1 (2015-12-15)
------------------

- Fix pip install version. [Jose Diaz-Gonzalez]

0.5.0 (2015-12-15)
------------------

- Add a makefile target to run an example runner. [Jose Diaz-Gonzalez]

- Add missing import. [Jose Diaz-Gonzalez]

- Ensure pygments is available. [Jose Diaz-Gonzalez]

- Add more information to the base log format. [Jose Diaz-Gonzalez]

  - Use ISO8601 date format
  - Add the process id
  - Ensure we add the name of the logger
  - Wrap time in brackets

- Add documentation for LOGGING_FILE_CONFIG. [Jose Diaz-Gonzalez]

- Allow configuring logging via file config. [Jose Diaz-Gonzalez]

  Set the LOGGING_FILE_CONFIG env var to specify a logging config file

- Add caching to travis runs. [Jose Diaz-Gonzalez]

0.4.4 (2015-11-25)
------------------

- Properly handle versions of pika connections where nowait is not
  implemented. [Jose Diaz-Gonzalez]

  Blocking connections appear to not implement nowait, so we need to sniff out this feature before tacking on a keyword argument.


- Fix pip install instructions. [Jose Diaz-Gonzalez]

0.4.3 (2015-09-12)
------------------

- Use print instead of logger for error messages. [Jose Diaz-Gonzalez]

  The python logger may be somehow reconfigured by a worker during it's import tests


0.4.1 (2015-09-12)
------------------

- Set current values in setup.py. [Jose Diaz-Gonzalez]

  sorry phil


0.4.0 (2015-09-12)
------------------

- Add flag to allow validating config.yml files. [Jose Diaz-Gonzalez]

- Fix syntax highlighting. [Jose Diaz-Gonzalez]

- Add check for gitchangelog. [Jose Diaz-Gonzalez]

0.3.6 (2015-09-03)
------------------

- Ensure the rst-lint binary is available. [Jose Diaz-Gonzalez]

- Add test badge to readme. [Jose Diaz-Gonzalez]

- Move wheel checking to the top of the file. [Jose Diaz-Gonzalez]

0.3.5 (2015-08-07)
------------------

- Minor updates to exit codes. [Jose Diaz-Gonzalez]

- Hack to workaround pipefail... [Jose Diaz-Gonzalez]

0.3.4 (2015-08-07)
------------------

- Do not use backticks. [Jose Diaz-Gonzalez]

- Lint rst file before continuing. [Jose Diaz-Gonzalez]

- Add support for building python wheels. [Jose Diaz-Gonzalez]

- Ensure the release script fails at the first sign of trouble. [Jose
  Diaz-Gonzalez]

- Fix readme for pypi. [Jose Diaz-Gonzalez]

0.3.3 (2015-08-07)
------------------

- Move examples into single folder. [Jose Diaz-Gonzalez]

0.3.1 (2015-08-07)
------------------

- Fix manifest file. [Jose Diaz-Gonzalez]

- Fix setup.py to point to correct readme file. [Jose Diaz-Gonzalez]

- Add a release script to make releasing versions easier. [Jose Diaz-
  Gonzalez]

- Add a release script to make releasing versions easier. [Jose Diaz-
  Gonzalez]

- Add pika to install_requires. [Jose Diaz-Gonzalez]

v0.3.0 (2015-07-07)
-------------------

- V0.3.0. [Jose Diaz-Gonzalez]

- Ensure we verify connection types in the argparser. [Jose Diaz-
  Gonzalez]

- Peg haigha and pika to tested versions. [Jose Diaz-Gonzalez]

- Add ability to set pika as the backend for amqpdispatcher. [Jose Diaz-
  Gonzalez]

- Add pika implementation of amqp-dispatcher. [Jose Diaz-Gonzalez]

- Add proxy classes for pika channels and connections. [Jose Diaz-
  Gonzalez]

- Add pika requirement. [Jose Diaz-Gonzalez]

- Wrap pika responses in a dummy Message class. [Jose Diaz-Gonzalez]

  pika sends the channel as the first argument, with the message being sent in args.


- Improve python 2.6 compatibility. [Jose Diaz-Gonzalez]

- Create a basic entry point in dispatcher.py. [Jose Diaz-Gonzalez]

- Use setup() method from dispatcher_common in dispatcher_haigha. [Jose
  Diaz-Gonzalez]

- Proxy both channels and connections. [Jose Diaz-Gonzalez]

- Extract all common methods from dispatcher_haigha to
  dispatcher_common. [Jose Diaz-Gonzalez]

  The extracted methods are not tied to haigha and can be reused across multiple backends.


- Set a default port in the specified RABBITMQ_URL env var. [Jose Diaz-
  Gonzalez]

- Move dispatcher.py to dispatcher_haigha.py. [Jose Diaz-Gonzalez]

- Allow overriding the VIRTUALENV_PATH. [Jose Diaz-Gonzalez]

- Add a ConnectionProxy to handle differences between rabbitmq
  libraries. [Jose Diaz-Gonzalez]

  At the moment, this only adds a method to set the close callback of the Haigha Connection class.


- Use a proxied channel inside of AMQPProxy. [Jose Diaz-Gonzalez]

- Add a ChannelProxy to handle differences between rabbitmq libraries.
  [Jose Diaz-Gonzalez]

  At the moment, this only normalizes calls to the `haigha.channel.Channel` `basic` commands.


v0.2.2 (2015-07-05)
-------------------

- V0.2.2. [Jose Diaz-Gonzalez]

- Switch to container-based travis. [Jose Diaz-Gonzalez]

- Separate out test classes. [Jose Diaz-Gonzalez]

  Though they both have to connecting, the tested portions are wholly separate and thus do not need to be kept together


- Minor PEP8 fixes. [Jose Diaz-Gonzalez]

- Add shebang and encoding tag. [Jose Diaz-Gonzalez]

- Move AMQPProxy and ConsumerPool into their own modules. [Jose Diaz-
  Gonzalez]

  This is a minor change in how the modules work and should not affect any external interfaces


v0.2.1 (2015-07-05)
-------------------

- V0.2.1. [Jose Diaz-Gonzalez]

- Pass in port individually. [Jose Diaz-Gonzalez]

  Adding it onto the host appears to have issues when non-standard ports are in use


- Remove support for env vars other than RABBITMQ_URL. [Jose Diaz-
  Gonzalez]

  This commit removes the extra parsing, in an attempt to simplify the codebase. The env var RABBITMQ_URL is sufficient to provide all the configuration necessary for amp-dispatcher.


v0.1.1 (2015-03-31)
-------------------

- V0.1.1. [Jose Diaz-Gonzalez]

- PEP8. [Jose Diaz-Gonzalez]

- This call is basically a syntax error. [Adam Cohen]

- Fixes locked consumers. [Adam Cohen]

v0.1.0 (2015-03-31)
-------------------

- Merge conflict. [Adam Cohen]

- Use pythonic comparison. [Adam Cohen]

- Add support+tests for RABBITMQ_URL environment variable. [Adam Cohen]

- Create queues defined in the amqp_dispatcher yaml at application start
  time. [Adam Cohen]

  This allows a client to dynamically specify which queues it should be listening to without necessitating coordination with the RabbitMQ server. It can be useful during testing scenarios or when attempting to bring up/down queue workers in disparate services.


- Use the python logger instead of print statements. [Adam Cohen]

- Add env variable instructions to README. [Adam Cohen]

- Will logger.exception will log full exception and stack trace, no need
  to pass exception. [Adam Cohen]

- Use pythonic comparison. [Adam Cohen]

- Add support for RABBITMQ_URL and tests for parsing environment. [Adam
  Cohen]

- Add documentation to README. [Adam Cohen]

- Max exclusive parameterizable. [Adam Cohen]

- Create queues defined in the amqp_dispatcher yaml at application start
  time. [Adam Cohen]

- Log things. [Adam Cohen]

- Fixes locked consumers. [Rick Hanlon II]

v0.0.10 (2014-11-07)
--------------------

- V0.0.10. [Jose Diaz-Gonzalez]

- Fix import path for RabbitConnection. [Jose Diaz-Gonzalez]

  In haigha 0.7.1, there is a BC break where the RabbitConnection is no longer imported in haigha.connections.__init__.py

  https://github.com/agoragames/haigha/commit/d2281ee7369a7231aaa7f9a19220f3af93e3fa49

v0.0.9 (2013-06-10)
-------------------

- V0.0.9. [Philip Cristiano]

- Allow non-default vhost with RABBITMQ_VHOST. [chris erway]

- Reqs: I'll assume you're on 2.7. [Philip Cristiano]

- Travis: Fix path to reqs. [Philip Cristiano]

- Travis: Try installing Python version specific reqs. [Philip
  Cristiano]

v0.0.8 (2013-02-17)
-------------------

- V0.0.8 Fix bug when using RABBITMQ_HOST. [Philip Cristiano]

v0.0.7 (2013-02-17)
-------------------

- Include version. [Philip Cristiano]

v0.0.6 (2013-02-17)
-------------------

- V0.0.6. [Philip Cristiano]

- Connect to 1 of a random list of hosts. [Philip Cristiano]

- Use proper exit code for connection error. [Philip Cristiano]

- Yaml: safe_load! [Philip Cristiano]

- Dispatcher: Change {} to {0} for py2.6. [Philip Cristiano]

- Logging: Make NullHandler for py2.6. [Philip Cristiano]

- Req: Add importlib for 2.6. [Philip Cristiano]

- Need argparse for 2.6. [Philip Cristiano]

- Req: Remove unused requirements. [Philip Cristiano]

- Travis: Install libevent. [Philip Cristiano]

- Travis! [Philip Cristiano]

v0.0.5 (2013-01-31)
-------------------

- V0.0.5. [Philip Cristiano]

- Config: Include username and password. [Philip Cristiano]

- Test: Don't reject if acked. [Philip Cristiano]

- Test: Make sure reject/requeue is called when an error occurs. [Philip
  Cristiano]

- Test: Actually call erroring consumer. [Philip Cristiano]

- Test ConsumerPool calls consume and shutdown. [Philip Cristiano]

  Requires gevent in the test, not to bad, needs to be cleaned up though

- Don't use a new class, just use greenlet for now. [Philip Cristiano]

  Less complexity, still trying to make it easier to test consumer pool spawning

- Start process container for gevent. [Philip Cristiano]

- Whitespace fixes. [Philip Cristiano]

- Example startup adds handler to root. [Philip Cristiano]

- Pool: Catch errors from exceptional shutdown. [Philip Cristiano]

- Proxy: Raise error if responding twice. [Philip Cristiano]

- Move module to avoid nose picking it up. [Philip Cristiano]

- Fix example logging. [Philip Cristiano]

- Fix path to examples. [Philip Cristiano]

- Fix startup handling when not defined. [Philip Cristiano]

- Log with logger, not logging. [Philip Cristiano]

- Global startup handler and use logging instead of prints. [Philip
  Cristiano]

v0.0.4 (2013-01-17)
-------------------

- V0.0.4. [Philip Cristiano]

- Config: Add consumer_count. [Philip Cristiano]

- Requirements: Add forgotten requirements. [Philip Cristiano]

- Example: Remove old function. [Philip Cristiano]

- README: some docs. [Philip Cristiano]

v0.0.3 (2013-01-16)
-------------------

- Use parameters when publishing. [Philip Cristiano]

- Setup v 0.0.2. [Philip Cristiano]

- Suitable to be a daemon. [Philip Cristiano]

- Only need to run this once. [Philip Cristiano]

- Remove unused imports. [Philip Cristiano]

- Run concurrently with prefetch and ack messages. [Philip Cristiano]

- First prototype. [Philip Cristiano]

  Trying to work out how to run multiple greenlets simultaneously

- Make: Add upload target. [Philip Cristiano]

- Make: Fix path to Python. [Philip Cristiano]

- Basic project layout. [Philip Cristiano]

- Initial commit. [philipcristiano]


