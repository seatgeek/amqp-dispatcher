TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
load "${TEST_GIT_ROOT}/tests/utilities/test_utils.bash"

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
@test "Proxy given to AMQP consumers can republish" {
    NOW_TIMESTAMP=$(date -u +%s)

    docker-compose -f docker-compose.yml -f ./tests/integration/proxy-test.compose-override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 15s

    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "all consumers of class PublishConsumer created"
    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "all consumers of class ForeverConsumer created"

    # Send five messages to the main_proxy_queue
    python ./tests/integration/message_sender.py --queue main_proxy_queue --number 5

    # Make sure the messages have been received 5 times
    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1)
    PUBLISH_CONSUMER_RECEIVED_MESSAGE=$(echo "$LOGS_SINCE" | grep -c "PublishConsumer receiving message")
    assert_equal "$PUBLISH_CONSUMER_RECEIVED_MESSAGE" 5

    # The publish consumer publishes
    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "ForeverConsumer receiving message"

    LOGS_SINCE=$(docker logs amqp-dispatcher_dispatcher_1 --since "$RECONNECT_MARK_TIMESTAMP" 2>&1)
    FOREVER_CONSUMER_RECEIVING_MESSAGE=$(echo "$LOGS_SINCE" | grep -c "ForeverConsumer receiving message")
    assert_equal "$FOREVER_CONSUMER_RECEIVING_MESSAGE" 5
}

teardown() {
    teardown_sequence
}
