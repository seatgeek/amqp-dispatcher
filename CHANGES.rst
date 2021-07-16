Changelog
=========

1.3.0 (2021-07-16)
------------------
------------
- This is no longer true. [Phil Tang]
- Fix the logger situation. [Phil Tang]


1.2.2 (2021-07-13)
------------------
- Release version 1.2.2. [Phil Tang]
- More of this. [Phil Tang]
- Passing an arg here prevents any logs from happening. [Phil Tang]


1.2.1 (2020-10-15)
------------------
- Merge pull request #42 from seatgeek/jwd-fail-on-consumer-load-errors.
  [José Lorenzo Rodríguez]

  log and exit if amqp-dispatcher fails to load consumer
- Release 1.2.1. [Jesper Wendel Devantier]
- Ignore hidden files. [Jesper Wendel Devantier]
- Library uses type annotations - requires 3.x. [Jesper Wendel
  Devantier]
- Black. [Jesper Wendel Devantier]
- Log and exit if amqp-dispatcher fails to load consumer. [Jesper Wendel
  Devantier]

  Ensure that failure to load a given consumer results in a visible
  error.

  Made in response to errors observed in production where loading a
  consumer may fail silently and which is only visible through
  observing that no consumers are registered to a queue in RMQ.
- Release version 1.2.0. [Nicholas Briganti]
- Update __init__.py. [NicholasABriganti]


1.1.0 (2020-05-07)
------------------
- Release version 1.1.0. [Nicholas Briganti]
- Release version 1.1.0. [Nicholas Briganti]
- Release version 1.1.0. [Nicholas Briganti]
- Release version 1.1.0. [Nicholas Briganti]
- Merge branch 'master' of github.com:seatgeek/amqp-dispatcher.
  [Nicholas Briganti]
- Update __init__.py. [NicholasABriganti]
- Release version 1.2.0. [Nicholas Briganti]
- Release version 1.2.0. [Nicholas Briganti]
- Update __init__.py. [NicholasABriganti]
- Merge pull request #39 from seatgeek/nb-quorum-queues.
  [NicholasABriganti]

  Adding x-queue-type
- Cleanup. [Nicholas Briganti]
- Adding x-queue-type. [Nicholas Briganti]
- Merge pull request #40 from seatgeek/pin-version. [Gareth T]

  Pin aio-pika version.
- Pin aio-pika version. [Gareth Tan]
- Merge pull request #38 from flyrev/master. [Gareth T]

  Add separate steps in for copying requirements.txt and running pip install
- Add separate steps in Dockerfile for copying requirements.txt and
  installing requirements, for better cache utilization. [Christian
  Neverdal]

  See https://www.aptible.com/documentation/deploy/tutorials/faq/dockerfile-caching/pip-dockerfile-caching.html


1.0.0 (2019-10-03)
------------------
- Merge pull request #37 from seatgeek/pika-only. [Gareth T]

  Asynchronous Python 3 AMQP Dispatcher
- Add formatting. [Gareth Tan]
- Merge branch 'pika-only' of github.com:seatgeek/amqp-dispatcher into
  pika-only. [Gareth Tan]
- Remove no-wait since aio_pika cannot handle it. [Gareth Tan]
- Reformat. [Gareth Tan]
- Bump version. [Gareth Tan]
- Restore delivery_info and add test. [Gareth Tan]
- Remove unused import. [Gareth Tan]
- Remove connection argument. [Gareth Tan]
- Remove random generation. [Gareth Tan]
- Relax and specify more requirement versions. [Gareth Tan]
- Revamp setup.py. [Gareth Tan]
- Make type signature more specific. [Gareth Tan]
- Install mypy. [Gareth Tan]
- Fix kwargs. [Gareth Tan]
- Fix types. [Gareth Tan]
- Fix formatting. [Gareth Tan]
- Fix types. [Gareth Tan]
- Refine ignores. [Gareth Tan]
- Start on fixes. [Gareth Tan]
- Add mypy and settings. [Gareth Tan]
- Format with Black. [Gareth Tan]
- Add Black enforcement. [Gareth Tan]
- Fix comments. [Gareth Tan]
- Add proxy test. [Gareth Tan]
- Fix comment. [Gareth Tan]
- Add disconnection test and make logging for the TrulyRobustConsumer
  more consistent. [Gareth Tan]
- Improve comments and naming. [Gareth Tan]
- Use tasks to manage futures. [Gareth Tan]
- Express in terms of ensure_future. [Gareth Tan]
- Remove connection wrapper. [Gareth Tan]
- Several comment improvements. [Gareth Tan]
- Add further consumer test. [Gareth Tan]
- Further cleanup. [Gareth Tan]
- Add to travis. [Gareth Tan]
- Improve message sender interface. [Gareth Tan]
- Add consumer tests. [Gareth Tan]
- Attempt new sort order. [Gareth Tan]
- Revert "Normalize sort." [Gareth Tan]

  This reverts commit 25a08f9256cf37a15fe962768795e546e261f3af.
- Normalize sort. [Gareth Tan]
- Improve tests. [Gareth Tan]
- Fix directory. [Gareth Tan]
- Add AMQP-dispatcher configuration tests. [Gareth Tan]
- Some refactoring. [Gareth Tan]
- Add proper waiting and array length check. [Gareth Tan]
- Add flag. [Gareth Tan]
- Use standard flag. [Gareth Tan]
- Increase robustness. [Gareth Tan]
- Specify container names. [Gareth Tan]
- Debug. [Gareth Tan]
- Add longer sleep test. [Gareth Tan]
- Fix automatic extension idiosyncracy. [Gareth Tan]
- Fix assert library loading. [Gareth Tan]
- Optimize Travis tests. [Gareth Tan]
- Sudo tar. [Gareth Tan]
- Move to Xenial. [Gareth Tan]
- Add version. [Gareth Tan]
- Fix install. [Gareth Tan]
- Remove dockerize. [Gareth Tan]
- Create base and override files. [Gareth Tan]
- Add daemon. [Gareth Tan]
- Prepare for testing with Docker. [Gareth Tan]
- Format files with Black. [Gareth Tan]
- Fix logger name. [Gareth Tan]
- Set initial state. [Gareth Tan]
- Improve consumer example. [Gareth Tan]
- Create truly robust connection. [Gareth Tan]
- Add toxiproxy configuration for testing. [Gareth Tan]
- Remove further unused tests. [Gareth Tan]
- Reformat all code to Black standard. [Gareth Tan]
- Add dependency on Black. [Gareth Tan]
- Fix AMQP proxy tests. [Gareth Tan]
- Make some difference in dispatcher config. [Gareth Tan]
- Optimize channels. [Gareth Tan]
- Clarify naming. [Gareth Tan]
- Move to non-blocking loop. [Gareth Tan]
- Random string logging. [Gareth Tan]
- Improve logging. [Gareth Tan]
- Remove spaces. [Gareth Tan]
- Clean up unused classes and dispatchers. [Gareth Tan]
- Add ability to publish from AMQP proxy. [Gareth Tan]
- Set up AMQP consumer. [Gareth Tan]
- Continue on removing other dispatchers. [Gareth Tan]
- Work on converting to aio pika. [Gareth Tan]
- Add ability to build examples in a Docker container. [Gareth Tan]


0.12.1 (2019-05-16)
-------------------
- Release version 0.12.1. [Geoff Johnson]
- Merge pull request #35 from seatgeek/rafalstapinski-patch-1. [Rafal
  Stapinski]

  bump __version__ to 0.12.0
- Update __init__.py. [Rafal Stapinski]
- Bump __version__ to 0.12.1. [Rafal Stapinski]


0.12.0 (2019-05-13)
-------------------
- Merge pull request #33 from seatgeek/rs-update-boilerplate. [Rafal
  Stapinski]

  Update readme and setup
- Update readme and setup. [Rafal Stapinski]
- Merge pull request #32 from seatgeek/rs-python-3-string-escape. [Rafal
  Stapinski]

  Change message __str__ function
- Remove 2.6 from travis. [Rafal Stapinski]
- Update message __str__ for python 2 and 3. [Rafal Stapinski]
- Utf-8 escape. [Rafal Stapinski]
- String_escape -> unicode_escape. [Rafal Stapinski]


0.11.0 (2019-01-22)
-------------------
- Release version 0.11.0. [Jose Diaz-Gonzalez]
- Merge pull request #30 from b-r-oleary/bro-python-3. [Jose Diaz-
  Gonzalez]

  Add python 3 compatibility
- Remove nosyd from python 3.6 requirements. [Brendon Oleary]
- Change the connection options depending on python version. [Brendon
  Oleary]
- Replace the unicode encoding check for python 2. [Brendon Oleary]
- Attempt to obtain python 3.6 compatibility. [Brendon Oleary]
- Merge pull request #28 from opschops/docs. [Jose Diaz-Gonzalez]

  readme: Update URL for installation
- Readme: Update URL for installation. [Philip Cristiano]


0.10.0 (2017-07-07)
-------------------
- Release version 0.10.0. [Jose Diaz-Gonzalez]
- Merge pull request #27 from ekelleyv/heartbeat-env-var. [Jose Diaz-
  Gonzalez]

  Add support for RABBITMQ_HEARTBEAT environment variable
- Add heartbeat env var. [Ed Kelley]


0.9.1 (2017-06-05)
------------------

Fix
~~~
- Install version-level dependencies before global. [Jose Diaz-Gonzalez]
- Pin gevent to 1.1 for python 2.6. [Jose Diaz-Gonzalez]

Other
~~~~~
- Release version 0.9.1. [Jose Diaz-Gonzalez]
- Merge pull request #25 from opschops/py26. [Jose Diaz-Gonzalez]

  fix: pin gevent to 1.1 for python 2.6


0.9.0 (2017-06-05)
------------------
- Release version 0.9.0. [Jose Diaz-Gonzalez]
- Merge pull request #24 from opschops/consumer-name. [Jose Diaz-
  Gonzalez]

  Use client_properties to set the management ui `connection_name`
- Use client_properties to set the management ui `connection_name` [Jose
  Diaz-Gonzalez]

  The consumer_name is based upon the following bits:

  - the hostname of the server amqp-dispatcher is running on
  - the process id
  - a random string made of only ascii characters

  This can be used to more easily figure out where consumers are in your infrastructure.


0.8.1 (2016-10-31)
------------------
- Release version 0.8.1. [Jose Diaz-Gonzalez]
- Use correct grep call for git 2.0. [Jose Diaz-Gonzalez]
- Feat: add editorconfig. [Jose Diaz-Gonzalez]
- Pull down all keys when updating local copy. [Jose Diaz-Gonzalez]
- Update release script a bit. [Jose Diaz-Gonzalez]


0.8.0 (2016-02-23)
------------------
- Release version 0.8.0. [Jose Diaz-Gonzalez]
- Workaround for urlparse bug in Python 2.7.3. [Jose Diaz-Gonzalez]

  Apparently the querystring portion isn't respected, causing the vhost to be set to `/?whatever=querystring&is=set`. This breaks heartbeat parsing support on at least Ubuntu 12.04.


0.7.1 (2016-02-22)
------------------
- Release version 0.7.1. [Jose Diaz-Gonzalez]
- Fix handling of heartbeat for pika dispatcher. [Jose Diaz-Gonzalez]


0.7.0 (2016-02-18)
------------------
- Release version 0.7.0. [Jose Diaz-Gonzalez]
- Respect heartbeat settings from RABBITMQ_URL environment variable.
  [Jose Diaz-Gonzalez]

  This also reverts 17829d5, which was caused by incorrect documentation of the haigha library. Instead, we properly default to respecting the heartbeat from the client, and also allow users to override this via the RABBITMQ_URL


0.6.0 (2016-02-16)
------------------
- Release version 0.6.0. [Jose Diaz-Gonzalez]
- Merge pull request #23 from opschops/haigha-heartbeat. [Jose Diaz-
  Gonzalez]

  Respect heartbeat settings from server when using the haigha dispatcher
- Respect heartbeat settings from server when using the haigha
  dispatcher. [Jose Diaz-Gonzalez]


0.5.1 (2015-12-15)
------------------
- Release version 0.5.1. [Jose Diaz-Gonzalez]
- Update release script. [Jose Diaz-Gonzalez]
- Fix pip install version. [Jose Diaz-Gonzalez]


0.5.0 (2015-12-15)
------------------
- Release version 0.5.0. [Jose Diaz-Gonzalez]
- Add a makefile target to run an example runner. [Jose Diaz-Gonzalez]
- Update log formatter to match what is used by amqp-dispatcher logger.
  [Jose Diaz-Gonzalez]
- Add missing import. [Jose Diaz-Gonzalez]
- Ensure pygments is available. [Jose Diaz-Gonzalez]
- Merge pull request #22 from opschops/jdg-logging. [Jose Diaz-Gonzalez]

  Updated logging mechanisms
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
- Release version 0.4.4. [Jose Diaz-Gonzalez]
- Properly handle versions of pika connections where nowait is not
  implemented. [Jose Diaz-Gonzalez]

  Blocking connections appear to not implement nowait, so we need to sniff out this feature before tacking on a keyword argument.
- Fix pip install instructions. [Jose Diaz-Gonzalez]


0.4.3 (2015-09-12)
------------------
- Release version 0.4.3. [Jose Diaz-Gonzalez]
- Use print instead of logger for error messages. [Jose Diaz-Gonzalez]

  The python logger may be somehow reconfigured by a worker during it's import tests


0.4.2 (2015-09-12)
------------------
- Release version 0.4.2. [Jose Diaz-Gonzalez]


0.4.1 (2015-09-12)
------------------
- Release version 0.4.1. [Jose Diaz-Gonzalez]
- Set current values in setup.py. [Jose Diaz-Gonzalez]

  sorry phil


0.4.0 (2015-09-12)
------------------
- Release version 0.4.0. [Jose Diaz-Gonzalez]
- Add flag to allow validating config.yml files. [Jose Diaz-Gonzalez]
- Fix syntax highlighting. [Jose Diaz-Gonzalez]
- Add check for gitchangelog. [Jose Diaz-Gonzalez]


0.3.7 (2015-09-03)
------------------
- Release version 0.3.7. [Jose Diaz-Gonzalez]
- Update badge in readme. [Jose Diaz-Gonzalez]


0.3.6 (2015-09-03)
------------------
- Release version 0.3.6. [Jose Diaz-Gonzalez]
- Ensure the rst-lint binary is available. [Jose Diaz-Gonzalez]
- Add test badge to readme. [Jose Diaz-Gonzalez]
- Move wheel checking to the top of the file. [Jose Diaz-Gonzalez]


0.3.5 (2015-08-07)
------------------
- Release version 0.3.5. [Jose Diaz-Gonzalez]
- Minor updates to exit codes. [Jose Diaz-Gonzalez]
- Hack to workaround pipefail... [Jose Diaz-Gonzalez]


0.3.4 (2015-08-07)
------------------
- Release version 0.3.4. [Jose Diaz-Gonzalez]
- Do not use backticks. [Jose Diaz-Gonzalez]
- Lint rst file before continuing. [Jose Diaz-Gonzalez]
- Add support for building python wheels. [Jose Diaz-Gonzalez]
- Ensure the release script fails at the first sign of trouble. [Jose
  Diaz-Gonzalez]
- Fix readme for pypi. [Jose Diaz-Gonzalez]


0.3.3 (2015-08-07)
------------------
- Release version 0.3.3. [Jose Diaz-Gonzalez]
- Move examples into single folder. [Jose Diaz-Gonzalez]


0.3.2 (2015-08-07)
------------------
- Release version 0.3.2. [Jose Diaz-Gonzalez]


0.3.1 (2015-08-07)
------------------
- Release version 0.3.1. [Jose Diaz-Gonzalez]
- Fix manifest file. [Jose Diaz-Gonzalez]
- Fix setup.py to point to correct readme file. [Jose Diaz-Gonzalez]
- Add a release script to make releasing versions easier. [Jose Diaz-
  Gonzalez]
- Add a release script to make releasing versions easier. [Jose Diaz-
  Gonzalez]
- Update and rename README.md to README.rst. [Jose Diaz-Gonzalez]
- Add pika to install_requires. [Jose Diaz-Gonzalez]
- Update README.md. [Jose Diaz-Gonzalez]
- Update README.md. [Jose Diaz-Gonzalez]
- V0.3.0. [Jose Diaz-Gonzalez]
- Merge pull request #21 from philipcristiano/haigha-dispatcher. [Jose
  Diaz-Gonzalez]

  Haigha Dispatcher
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
- V0.2.2. [Jose Diaz-Gonzalez]
- Merge pull request #20 from philipcristiano/refactor-classes. [Jose
  Diaz-Gonzalez]

  Refactor classes
- Switch to container-based travis. [Jose Diaz-Gonzalez]
- Separate out test classes. [Jose Diaz-Gonzalez]

  Though they both have to connecting, the tested portions are wholly separate and thus do not need to be kept together
- Minor PEP8 fixes. [Jose Diaz-Gonzalez]
- Add shebang and encoding tag. [Jose Diaz-Gonzalez]
- Move AMQPProxy and ConsumerPool into their own modules. [Jose Diaz-
  Gonzalez]

  This is a minor change in how the modules work and should not affect any external interfaces
- V0.2.1. [Jose Diaz-Gonzalez]
- Merge pull request #18 from seatgeek/simplify-connecting-to-rabbitmq.
  [Jose Diaz-Gonzalez]

  Remove support for env vars other than RABBITMQ_URL
- Pass in port individually. [Jose Diaz-Gonzalez]

  Adding it onto the host appears to have issues when non-standard ports are in use
- Remove support for env vars other than RABBITMQ_URL. [Jose Diaz-
  Gonzalez]

  This commit removes the extra parsing, in an attempt to simplify the codebase. The env var RABBITMQ_URL is sufficient to provide all the configuration necessary for amp-dispatcher.
- V0.1.1. [Jose Diaz-Gonzalez]
- Merge pull request #17 from seatgeek/master. [Jose Diaz-Gonzalez]

  PEP8
- PEP8. [Jose Diaz-Gonzalez]
- Merge pull request #1 from seatgeek/create-queues. [Adam Cohen]

  Create queues
- This call is basically a syntax error. [Adam Cohen]
- Fixes locked consumers. [Adam Cohen]
- Merge pull request #15 from seatgeek/create-queues. [Jose Diaz-
  Gonzalez]

  Create queues
- Merge conflict. [Adam Cohen]
- Use pythonic comparison. [Adam Cohen]
- Add support+tests for RABBITMQ_URL environment variable. [Adam Cohen]
- Create queues defined in the amqp_dispatcher yaml at application start
  time. [Adam Cohen]

  This allows a client to dynamically specify which queues it should be listening to without necessitating coordination with the RabbitMQ server. It can be useful during testing scenarios or when attempting to bring up/down queue workers in disparate services.
- Use the python logger instead of print statements. [Adam Cohen]
- Add env variable instructions to README. [Adam Cohen]
- Update version to 0.1.0. [Adam Cohen]
- Will logger.exception will log full exception and stack trace, no need
  to pass exception. [Adam Cohen]
- Use pythonic comparison. [Adam Cohen]
- Add support for RABBITMQ_URL and tests for parsing environment. [Adam
  Cohen]
- Add documentation to README. [Adam Cohen]
- Max exclusive parameterizable. [Adam Cohen]
- Create queues defined in the amqp_dispatcher yaml at application start
  time. [Adam Cohen]
- Merge branch 'master' of github.com:seatgeek/amqp-dispatcher. [Adam
  Cohen]
- Log things. [Adam Cohen]
- Merge pull request #14 from rickhanlonii/rh-fix-acks. [Jose Diaz-
  Gonzalez]

  Fixes locked consumers
- Fixes locked consumers. [Rick Hanlon II]
- V0.0.10. [Jose Diaz-Gonzalez]
- Merge pull request #13 from seatgeek/master. [Philip Cristiano]

  Fix import path for RabbitConnection
- Fix import path for RabbitConnection. [Jose Diaz-Gonzalez]

  In haigha 0.7.1, there is a BC break where the RabbitConnection is no longer imported in haigha.connections.__init__.py

  https://github.com/agoragames/haigha/commit/d2281ee7369a7231aaa7f9a19220f3af93e3fa49
- V0.0.9. [Philip Cristiano]
- Merge pull request #10 from cce/master. [Philip Cristiano]

  Add configurable vhost support
- Update README to mention RABBITMQ_VHOST. [chris erway]
- Allow non-default vhost with RABBITMQ_VHOST. [chris erway]
- Merge pull request #7 from zackkitzmiller/patch-1. [Philip Cristiano]

  Update spacing on README
- Update spacing on README. [Zack Kitzmiller]
- Update README.md. [Philip Cristiano]

  Actually comma separate
- Reqs: I'll assume you're on 2.7. [Philip Cristiano]
- Travis: Fix path to reqs. [Philip Cristiano]
- Travis: Try installing Python version specific reqs. [Philip
  Cristiano]
- V0.0.8 Fix bug when using RABBITMQ_HOST. [Philip Cristiano]
- Include version. [Philip Cristiano]
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
- V0.0.4. [Philip Cristiano]
- Config: Add consumer_count. [Philip Cristiano]
- Requirements: Add forgotten requirements. [Philip Cristiano]
- Example: Remove old function. [Philip Cristiano]
- README: some docs. [Philip Cristiano]
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


