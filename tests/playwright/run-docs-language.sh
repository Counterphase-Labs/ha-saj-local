#!/bin/sh
set -u

docs_language="$1"
docs_folder="$(printf '%s' "$docs_language" | tr 'A-Z' 'a-z')"
docs_project="$DOCS_PROJECT_NAME-$docs_folder"
docs_result_directory="$DOCS_REPOSITORY_ROOT/frontend/test-results/docs/$docs_folder"
docs_log="$DOCS_LOG_DIRECTORY/$docs_language.log"

docs_compose() {
    docker compose --project-name "$docs_project" \
        --file "$DOCS_COMPOSE_FILE" "$@"
}

mkdir -p "$docs_result_directory" \
    "$DOCS_REPOSITORY_ROOT/frontend/playwright-report/docs/$docs_folder"
export DOCS_LOCALE="$docs_language"
{
    docs_compose up --detach --wait homeassistant mock-docs mock-h2 &&
        docs_compose run --rm -T playwright-docs
} >"$docs_log" 2>&1
docs_status=$?
if [ "$docs_status" -ne 0 ]; then
    docs_compose logs --no-color homeassistant \
        >"$docs_result_directory/home-assistant.log" 2>&1 || true
fi
docs_compose down --volumes --remove-orphans >/dev/null 2>&1 || true
echo "$docs_status" >"$DOCS_LOG_DIRECTORY/$docs_language.status"
