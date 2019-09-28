TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
load "${TEST_GIT_ROOT}/tests/utilities/test_utils.bash"

setup() {
    docker-compose kill
}

@test "Multiple Queue, Binding Consumer Declarations" {
    NOW_TIMESTAMP=$(date -u +%s)

    docker-compose -f docker-compose.yml -f ./tests/configuration/multi-config-test.compose-override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 15s

    ( docker logs -f amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1 & ) | grep -q "all consumers of class Consumer created"
    ( docker logs -f amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1 & ) | grep -q "all consumers of class SecondaryConsumer created"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_queues --quiet --formatter csv
    QUEUES=$output
    assert_equal "${#lines[@]}" 3

    run clean_and_sort_csv "$QUEUES" "name"
    assert_line --index 0 "name,messages"
    assert_line --index 1 "second_test_queue,0"
    assert_line --index 2 "test_queue,0"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_consumers --quiet --formatter csv
    CONSUMERS=$output
    assert_equal "${#lines[@]}" 3

    run get_sorted_columns "$CONSUMERS" "queue_name,prefetch_count,ack_required"
    assert_line --index 0 "second_test_queue,4,true"
    assert_line --index 1 "test_queue,1,true"

    run get_sorted_columns "$CONSUMERS" "consumer_tag"
    assert_line --partial --index 0 "2000.17"
    assert_line --partial --index 0 "[examples.example_consumer:Consumer]"
    assert_line --partial --index 1 "2000.17"
    assert_line --partial --index 1 "[examples.example_secondary_consumer:SecondaryConsumer]"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_bindings --quiet --formatter csv
    BINDINGS=$output
    # each queue is bound to the default exchange
    assert_equal "${#lines[@]}" 5

    run clean_and_sort_csv "$BINDINGS" "destination_name,routing_key"
#    assert_equal "$output" 14
    assert_line --index 0 "source_name,source_kind,destination_name,destination_kind,routing_key,arguments"
    assert_line --index 1 "amq.direct,exchange,second_test_queue,queue,queue,[]"
    assert_line --index 2 ",exchange,second_test_queue,queue,second_test_queue,[]"
    assert_line --index 3 "amq.direct,exchange,test_queue,queue,queue,[]"
    assert_line --index 4 ",exchange,test_queue,queue,test_queue,[]"
}

teardown() {
    docker exec amqp-dispatcher_rabbit_1 rabbitmqctl stop_app
    docker exec amqp-dispatcher_rabbit_1 rabbitmqctl force_reset
    docker exec amqp-dispatcher_rabbit_1 rabbitmqctl start_app
    docker-compose kill
}