TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
load "${TEST_GIT_ROOT}/tests/utilities/test_utils.bash"

setup() {
    setup_sequence
}

@test "Basic Queue, Binding Consumer Declarations" {
    NOW_TIMESTAMP=$(date -u +%s)

    docker-compose -f docker-compose.yml -f ./tests/configuration/basic-config-test.compose-override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 15s

    ( log_wait_from "$NOW_TIMESTAMP" ) | grep -q "all consumers of class Consumer created"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_queues --quiet --formatter csv
    QUEUES=$output
    assert_equal "${#lines[@]}" 2

    run clean_csv "$QUEUES"
    assert_line --index 0 "name,messages"
    assert_line --index 1 "test_queue,0"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_consumers --quiet --formatter csv
    CONSUMERS=$output
    assert_equal "${#lines[@]}" 2

    run get_sorted_columns "$CONSUMERS" "queue_name,prefetch_count,ack_required"
    assert_line --index 0 "test_queue,2,true"

    run get_sorted_columns "$CONSUMERS" "consumer_tag"
    assert_line --partial --index 0 "2000.17"
    assert_line --partial --index 0 "[examples.example_consumer:Consumer]"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_bindings --quiet --formatter csv
    BINDINGS=$output
    # each queue is bound to the default exchange
    assert_equal "${#lines[@]}" 3

    run clean_and_sort_csv "$BINDINGS" "source_name,destination_name"
    assert_line --index 0 "source_name,source_kind,destination_name,destination_kind,routing_key,arguments"
    assert_line --index 1 "amq.direct,exchange,test_queue,queue,queue,[]"
    assert_line --index 2 ",exchange,test_queue,queue,test_queue,[]"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_channels --quiet --formatter csv number user prefetch_count
    CHANNELS=$output
    # each queue is bound to the default exchange
    assert_equal "${#lines[@]}" 3

    run clean_csv "$CHANNELS"
    assert_line --index 0 "number,user,prefetch_count"
    assert_line --index 1 "1,guest,0"
    assert_line --index 2 "2,guest,2"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_connections --quiet --formatter csv user state
    BINDINGS=$output
    # each queue is bound to the default exchange
    assert_equal "${#lines[@]}" 2

    run clean_csv "$BINDINGS"
    assert_line --index 0 "user,state"
    assert_line --index 1 "guest,running"
}

teardown() {
    teardown_sequence
}