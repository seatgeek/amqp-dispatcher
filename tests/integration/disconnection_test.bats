TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
load "${TEST_GIT_ROOT}/tests/utilities/test_utils.bash"

function toggle_rabbit() {
  docker exec amqp-dispatcher_toxiproxy_1 /go/bin/toxiproxy-cli toggle rabbit_1
}

setup() {
    setup_sequence
}

#  Test to Write
# N messages sent
#    - trigger disconnect
#    - consumers finish work on task
#    - consumers unable to ack message
#    - consumers get destroyed (no memory leak)
#    - trigger reconnect
#    - consumers consume message
#    - consumers finish work on task
#    - consumers able to ack message
@test "Reconnection behavior assumes idempotence of consumers" {
    NOW_TIMESTAMP=$(date -u +%s)

    docker-compose -f docker-compose.yml -f ./tests/integration/disconnection-test.compose-override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 15s

    # This is regular initialization stuff. Wait for amqp-dispatcher to
    # create the consumers
    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "all consumers of class TimedConsumer created"

    # Send five messages to the disco_queue
    python ./tests/integration/message_sender.py --queue disco_queue --number 5

    # Make sure the messages have been received 5 times
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_WORK_FINISHED=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer receiving message")
    assert_equal "$TIMED_CONSUMER_WORK_FINISHED" 5

    # Now disconnect the server.
    toggle_rabbit

    # ensure_future goes on in the background during the forever asyncio loop even if
    # we were to cancel the consumption task future on reconnect
    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "TimedConsumer finished work on message"

    # The five workers should finish all their tasks at about the same time, certainly closer
    # together than it would take to get the docker logs.
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_WORK_COMPLETED=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer finished work on message")
    assert_equal "$TIMED_CONSUMER_WORK_COMPLETED" 5

    # Ensure that the consumers are garbage collected so there is
    # no memory leak from consumers hanging around
    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "TimedConsumer destroyed"

    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_DESTROYED=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer destroyed")
    assert_equal "$TIMED_CONSUMER_DESTROYED" 5

    # We set this mark so that we can ensure that the events we are checking
    # for take place only after the reconnect
    RECONNECT_MARK_TIMESTAMP=$(date -u +%s)
    # Reconnect
    toggle_rabbit
    # Wait until the reconnection phase is successful
    ( log_wait_from "$RECONNECT_MARK_TIMESTAMP" ) | grep -q "reconnection phase: success"
    # and the consumers are created
    ( log_wait_from "$RECONNECT_MARK_TIMESTAMP" ) | grep -q "all consumers of class TimedConsumer created"

    # Now check for redelivery of the message to the new consumers
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$RECONNECT_MARK_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_RECEIVING_MESSAGE=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer receiving message")
    assert_equal "$TIMED_CONSUMER_RECEIVING_MESSAGE" 5

    # The new consumers, in the absence of a disconnection, will finish
    # their work...
    ( log_wait_from "$RECONNECT_MARK_TIMESTAMP" ) | grep -q "TimedConsumer finished work on message"
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$RECONNECT_MARK_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_WORK_FINISHED=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer finished work on message")
    assert_equal "$TIMED_CONSUMER_WORK_FINISHED" 5

    # ..and note a successfully acknowledged message
    ( log_wait_from "$RECONNECT_MARK_TIMESTAMP" ) | grep -q "TimedConsumer acked message"
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$RECONNECT_MARK_TIMESTAMP" 2>&1)
    TIMED_CONSUMER_ACKED_MESSAGE=$(echo "$LOGS_SINCE" | grep -c "TimedConsumer acked message")
    assert_equal "$TIMED_CONSUMER_ACKED_MESSAGE" 5
}

teardown() {
    teardown_sequence
}
