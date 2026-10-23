#!/bin/sh
set -eu

docs_repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
docs_compose_file="$docs_repository_root/compose.playwright.yaml"
docs_project_name="saj-local-docs-$$"
docs_result_directory="$docs_repository_root/frontend/test-results/docs"

docs_cleanup() {
    docs_exit_status=$?
    trap - EXIT HUP INT TERM
    if [ "$docs_exit_status" -ne 0 ]; then
        docker compose --project-name "$docs_project_name" \
            --file "$docs_compose_file" logs --no-color homeassistant \
            >"$docs_result_directory/home-assistant.log" 2>&1 || true
    fi
    docker compose --project-name "$docs_project_name" \
        --file "$docs_compose_file" down --volumes --remove-orphans \
        --rmi local || true
    exit "$docs_exit_status"
}

trap docs_cleanup EXIT HUP INT TERM
mkdir -p "$docs_result_directory" \
    "$docs_repository_root/frontend/playwright-report/docs" \
    "$docs_repository_root/docs/images"
export PLAYWRIGHT_RESULT_UID="$(id -u)"
export PLAYWRIGHT_RESULT_GID="$(id -g)"
docker compose --project-name "$docs_project_name" \
    --file "$docs_compose_file" build homeassistant playwright-docs
docker compose --project-name "$docs_project_name" \
    --file "$docs_compose_file" up --detach --wait homeassistant mock-docs mock-h2
docker compose --project-name "$docs_project_name" \
    --file "$docs_compose_file" run --rm playwright-docs
