#!/bin/sh
set -eu

playwright_repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
playwright_compose_file="$playwright_repository_root/compose.playwright.yaml"
playwright_project_name="saj-local-playwright-$$"
playwright_result_directory="$playwright_repository_root/frontend/test-results/home-assistant"

playwright_cleanup() {
    playwright_exit_status=$?
    trap - EXIT HUP INT TERM
    if [ "$playwright_exit_status" -ne 0 ]; then
        docker compose --project-name "$playwright_project_name" \
            --file "$playwright_compose_file" logs --no-color homeassistant \
            >"$playwright_result_directory/home-assistant.log" 2>&1 || true
    fi
    docker compose --project-name "$playwright_project_name" \
        --file "$playwright_compose_file" down --volumes --remove-orphans \
        --rmi local || true
    exit "$playwright_exit_status"
}

trap playwright_cleanup EXIT HUP INT TERM
mkdir -p "$playwright_result_directory" \
    "$playwright_repository_root/frontend/playwright-report/home-assistant"
export PLAYWRIGHT_RESULT_UID="$(id -u)"
export PLAYWRIGHT_RESULT_GID="$(id -g)"
docker compose --project-name "$playwright_project_name" \
    --file "$playwright_compose_file" build
docker compose --project-name "$playwright_project_name" \
    --file "$playwright_compose_file" up --detach --wait homeassistant modbus-mock modbus-mock-h2
docker compose --project-name "$playwright_project_name" \
    --file "$playwright_compose_file" run --rm playwright
