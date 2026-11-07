#!/bin/sh
set -eu

docs_repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
docs_worker="$docs_repository_root/tests/playwright/run-docs-language.sh"
docs_languages="en-GB de nl fr zh-Hans es it pl sv"

docs_selected=""
for docs_argument in "$@"; do
    case "$docs_argument" in
        -*) ;;
        *) docs_selected="$docs_argument" ;;
    esac
done
if [ -n "$docs_selected" ]; then
    case " $docs_languages " in
        *" $docs_selected "*) docs_languages="$docs_selected" ;;
        *)
            echo "unknown language code: $docs_selected (use one of: $docs_languages)" >&2
            exit 2
            ;;
    esac
fi

docs_count=0
for docs_language in $docs_languages; do
    docs_count=$((docs_count + 1))
done
docs_processors=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
docs_parallel=$((docs_processors / 4))
if [ "$docs_parallel" -lt 1 ]; then
    docs_parallel=1
fi
if [ "$docs_parallel" -gt "$docs_count" ]; then
    docs_parallel="$docs_count"
fi

export DOCS_REPOSITORY_ROOT="$docs_repository_root"
export DOCS_COMPOSE_FILE="$docs_repository_root/compose.playwright.yaml"
export DOCS_PROJECT_NAME="saj-local-docs-$$"
export PLAYWRIGHT_HOME_ASSISTANT_IMAGE="$DOCS_PROJECT_NAME-home-assistant"
export PLAYWRIGHT_RUNNER_IMAGE="$DOCS_PROJECT_NAME-runner"
export PLAYWRIGHT_RESULT_UID="$(id -u)"
export PLAYWRIGHT_RESULT_GID="$(id -g)"
docs_log_directory=$(mktemp -d)
export DOCS_LOG_DIRECTORY="$docs_log_directory"
docs_xargs_pid=""

docs_cleanup() {
    docs_exit_status=$?
    trap - EXIT HUP INT TERM
    if [ -n "$docs_xargs_pid" ]; then
        kill "$docs_xargs_pid" 2>/dev/null || true
    fi
    for docs_language in $docs_languages; do
        docs_lower=$(printf '%s' "$docs_language" | tr 'A-Z' 'a-z')
        docker compose --project-name "$DOCS_PROJECT_NAME-$docs_lower" \
            --file "$DOCS_COMPOSE_FILE" down --volumes --remove-orphans \
            >/dev/null 2>&1 &
    done
    wait || true
    docker image rm --force "$PLAYWRIGHT_HOME_ASSISTANT_IMAGE" \
        "$PLAYWRIGHT_RUNNER_IMAGE" >/dev/null 2>&1 || true
    rm -rf "$docs_log_directory"
    exit "$docs_exit_status"
}

trap docs_cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$docs_repository_root/docs/images"

docker compose --project-name "$DOCS_PROJECT_NAME-build" \
    --file "$DOCS_COMPOSE_FILE" build homeassistant playwright-docs

printf '%s\n' $docs_languages |
    xargs -P "$docs_parallel" -n 1 sh "$docs_worker" &
docs_xargs_pid=$!
wait "$docs_xargs_pid" || true
docs_xargs_pid=""

docs_failed=0
for docs_language in $docs_languages; do
    docs_status=$(cat "$docs_log_directory/$docs_language.status" 2>/dev/null || echo 1)
    if [ "$docs_status" -eq 0 ]; then
        docs_state=passed
    else
        docs_state=failed
        docs_failed=1
    fi
    echo "=== language $docs_language $docs_state ==="
    cat "$docs_log_directory/$docs_language.log" 2>/dev/null || true
done
exit "$docs_failed"
