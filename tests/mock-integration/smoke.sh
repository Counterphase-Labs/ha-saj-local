#!/bin/sh
set -eu

smoke_repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
smoke_image="saj-local-mock-smoke-$$"
smoke_project_name="saj-local-mock-smoke-$$"
smoke_container=""
smoke_state_directory=""
smoke_wait_seconds=60
smoke_panel_check='
import json
import time
import urllib.request

base = "http://127.0.0.1:8080"
deadline = time.monotonic() + 15
while True:
    try:
        page = urllib.request.urlopen(base + "/", timeout=3).read().decode()
        description = json.load(
            urllib.request.urlopen(base + "/api/description", timeout=3)
        )
        registers = json.load(
            urllib.request.urlopen(base + "/api/registers", timeout=3)
        )
        traffic = json.load(urllib.request.urlopen(base + "/api/traffic", timeout=3))
        stylesheet = urllib.request.urlopen(base + "/static/panel.css", timeout=3)
        break
    except OSError:
        if time.monotonic() > deadline:
            raise
        time.sleep(0.5)
assert "<html" in page.lower(), "the page did not load"
assert description["model"]["name"], "the description names no model"
assert registers["blocks"], "the register snapshot has no blocks"
assert "counters" in traffic, "the traffic has no counters"
assert stylesheet.status == 200, "the stylesheet was not served"
'
smoke_save_check='
import json
import urllib.request

base = "http://127.0.0.1:8080"
link = json.load(urllib.request.urlopen(base + "/api/state", timeout=3))["link"]
request = urllib.request.Request(
    base + "/api/link",
    data=json.dumps(link).encode(),
    headers={"Content-Type": "application/json"},
)
urllib.request.urlopen(request, timeout=3)
'

export SAJ_MOCK_HOST_PORT=0
export SAJ_MOCK_H2_HOST_PORT=0
export SAJ_MOCK_PANEL_HOST_PORT=0
export SAJ_MOCK_H2_PANEL_HOST_PORT=0

smoke_cleanup() {
    smoke_exit_status=$?
    trap - EXIT HUP INT TERM
    if [ -n "$smoke_container" ]; then
        docker rm --force "$smoke_container" >/dev/null 2>&1 || true
    fi
    docker compose --project-name "$smoke_project_name" \
        --file "$smoke_repository_root/compose.yaml" down --volumes \
        --remove-orphans --rmi local >/dev/null 2>&1 || true
    docker image rm --force "$smoke_image" >/dev/null 2>&1 || true
    if [ -n "$smoke_state_directory" ]; then
        rm -rf "$smoke_state_directory"
    fi
    exit "$smoke_exit_status"
}

smoke_wait_until_healthy() {
    smoke_target=$1
    smoke_elapsed=0
    while [ "$smoke_elapsed" -lt "$smoke_wait_seconds" ]; do
        smoke_status=$(docker inspect --format '{{.State.Health.Status}}' "$smoke_target")
        if [ "$smoke_status" = "healthy" ]; then
            return 0
        fi
        sleep 1
        smoke_elapsed=$((smoke_elapsed + 1))
    done
    echo "$smoke_target did not become healthy: $smoke_status" >&2
    docker logs "$smoke_target" >&2 || true
    return 1
}

trap smoke_cleanup EXIT HUP INT TERM

smoke_state_directory=$(mktemp -d)
mkdir "$smoke_state_directory/hs3" "$smoke_state_directory/h2"
export SAJ_MOCK_STATE_DIR="$smoke_state_directory"

docker build --quiet --tag "$smoke_image" "$smoke_repository_root/mock" >/dev/null
for smoke_scenario in "$smoke_repository_root"/mock/scenarios/*.yaml; do
    echo "scenario $(basename "$smoke_scenario")"
    smoke_container=$(docker run --detach \
        --health-interval 1s --health-start-period 1s \
        --volume "$smoke_scenario:/config/config.yaml:ro" "$smoke_image")
    smoke_wait_until_healthy "$smoke_container"
    docker exec "$smoke_container" python -c "$smoke_panel_check"
    docker rm --force "$smoke_container" >/dev/null
    smoke_container=""
done

echo "compose services"
docker compose --project-name "$smoke_project_name" \
    --file "$smoke_repository_root/compose.yaml" up --detach --build --wait \
    --no-deps mock mock-h2
for smoke_service in mock mock-h2; do
    docker compose --project-name "$smoke_project_name" \
        --file "$smoke_repository_root/compose.yaml" exec -T "$smoke_service" \
        python -m saj_local_mock healthcheck
    docker compose --project-name "$smoke_project_name" \
        --file "$smoke_repository_root/compose.yaml" exec -T "$smoke_service" \
        python -c "$smoke_panel_check"
done
for smoke_service in mock mock-h2; do
    case "$smoke_service" in
    mock) smoke_state_file="$smoke_state_directory/hs3/state.json" ;;
    mock-h2) smoke_state_file="$smoke_state_directory/h2/state.json" ;;
    esac
    docker compose --project-name "$smoke_project_name" \
        --file "$smoke_repository_root/compose.yaml" exec -T "$smoke_service" \
        python -c "$smoke_save_check"
    smoke_elapsed=0
    while [ ! -f "$smoke_state_file" ]; do
        if [ "$smoke_elapsed" -ge 10 ]; then
            echo "$smoke_service did not save its state to $smoke_state_file" >&2
            docker compose --project-name "$smoke_project_name" \
                --file "$smoke_repository_root/compose.yaml" logs "$smoke_service" >&2 || true
            exit 1
        fi
        sleep 0.5
        smoke_elapsed=$((smoke_elapsed + 1))
    done
done
