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

# One language code from the arguments selects that language; options are not
# used by the run. Without a code every language runs, English first.
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

for docs_language in $docs_languages; do
    # Fresh containers for each language, so no state carries over.
    docker compose --project-name "$docs_project_name" \
        --file "$docs_compose_file" down --volumes --remove-orphans || true
    docker compose --project-name "$docs_project_name" \
        --file "$docs_compose_file" up --detach --wait homeassistant mock-docs mock-h2
    DOCS_LOCALE="$docs_language" docker compose --project-name "$docs_project_name" \
        --file "$docs_compose_file" run --rm playwright-docs
done
