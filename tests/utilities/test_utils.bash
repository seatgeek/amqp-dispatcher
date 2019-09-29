TEST_GIT_ROOT="$(git rev-parse --show-toplevel)"

# Load from submodule on Travis
if ! command -v "brew" > /dev/null; then
    load "${TEST_GIT_ROOT}/tests/test_helper/bats-support/load.bash"
    load "${TEST_GIT_ROOT}/tests/test_helper/bats-assert/load.bash"
else
# When running locally, use Brew
    TEST_BREW_PREFIX="$(brew --prefix)"
    load "${TEST_BREW_PREFIX}/lib/bats-support/load.bash"
    load "${TEST_BREW_PREFIX}/lib/bats-assert/load.bash"
fi

function setup_sequence() {
  docker-compose kill
}

function teardown_sequence() {
  docker exec amqp-dispatcher_rabbit_1 rabbitmqctl stop_app
  docker exec amqp-dispatcher_rabbit_1 rabbitmqctl force_reset
  docker exec amqp-dispatcher_rabbit_1 rabbitmqctl start_app
  docker-compose kill
}

function get_sorted_columns() {
  echo "$1" | csvcut --columns "$2" | tail -n +2 | sort
}


function get_sorted_excluding_columns() {
  echo "$1" | csvcut --not-columns "$2" | tail -n +2 | sort
}


function clean_csv() {
  echo "$1" | csvcut
}

function clean_and_sort_csv() {
  clean_csv "$1" | csvsort --no-inference --columns "$2"
}
