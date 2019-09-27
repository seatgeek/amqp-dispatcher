TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
load "${TEST_GIT_ROOT}/tests/utilities/test_utils.bash"


@test "Basic dispatcher queue and consumer establishment" {
    NOW_TIMESTAMP=$(date -u +%s)

    docker-compose -f docker-compose.yml -f ./tests/integration/basic-compose.override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 15s

    ( docker logs -f amqp-dispatcher_dispatcher_1 --since "$NOW_TIMESTAMP" 2>&1 & ) | grep -q "primarily initialized"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_queues --quiet
    QUEUES=$output
    assert_equal "${#lines[@]}" 3

    run get_sorted_column "$QUEUES" "name"
    assert_line --index 0 "second_test_queue"
    assert_line --index 1 "test_queue"

    run get_sorted_column "$QUEUES" "messages"
    assert_line --index 0 "0"
    assert_line --index 1 "0"

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_consumers --quiet
    CONSUMERS=$output
    assert_equal "${#lines[@]}" 2

    run get_sorted_column "$CONSUMERS" "queue_name"
    assert_line --index 0 "test_queue"

    run get_sorted_column "$CONSUMERS" "prefetch_count"
    assert_line --index 0 "2"

    run get_sorted_column "$CONSUMERS" "ack_required"
    assert_line --index 0 "true"
    assert_equal "${#lines[@]}" 1

    run get_sorted_column "$CONSUMERS" "consumer_tag"
    assert_line --partial --index 0 "2000.17"
    assert_line --partial --index 0 "[examples.example_consumer:Consumer]"
}

teardown() {
    docker-compose kill
}