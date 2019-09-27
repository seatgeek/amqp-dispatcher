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


function get_sorted_column() {
  echo "$1" | awk '
NR==1 {
    for (i=1; i<=NF; i++) {
        f[$i] = i
    }
}
{ print $(f["'"$2"'"]) }
' | tail -n +2 | sort
}