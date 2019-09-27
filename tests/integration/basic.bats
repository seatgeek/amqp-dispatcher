# Load from submodule on Travis
if ! type "brew" > /dev/null; then
    TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"
    load "${TEST_GIT_ROOT}/tests/test_helper/bats-support/load"
    load "${TEST_GIT_ROOT}/tests/test_helper/bats-assert/load"
else
# When running locally, use Brew
    TEST_BREW_PREFIX="$(brew --prefix)"
    load "${TEST_BREW_PREFIX}/lib/bats-support/load.bash"
    load "${TEST_BREW_PREFIX}/lib/bats-assert/load.bash"
fi

@test "Basic dispatcher queue and consumer establishment" {
    docker-compose -f docker-compose.yml -f ./tests/integration/basic-compose.override.yml up -d
    dockerize -wait tcp://localhost:5672 -timeout 25s
    sleep 7

    run docker exec amqp-dispatcher_rabbit_1 rabbitmqctl list_queues
    assert_equal "$status" 0
    assert_equal "${lines[3]}" "test_queue	0"
    assert_equal "${lines[4]}" "second_test_queue	0"
}

teardown() {
    docker-compose kill
}