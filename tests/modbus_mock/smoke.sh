#!/bin/sh
set -eu

smoke_repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
smoke_image="saj-modbus-mock-smoke-$$"
smoke_project_name="saj-modbus-mock-smoke-$$"
smoke_container=""
smoke_wait_seconds=60

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

docker build --quiet --tag "$smoke_image" "$smoke_repository_root/modbus_mock" >/dev/null
for smoke_scenario in "$smoke_repository_root"/modbus_mock/scenarios/*.yaml; do
    echo "scenario $(basename "$smoke_scenario")"
    smoke_container=$(docker run --detach \
        --health-interval 1s --health-start-period 1s \
        --volume "$smoke_scenario:/config/config.yaml:ro" "$smoke_image")
    smoke_wait_until_healthy "$smoke_container"
    docker rm --force "$smoke_container" >/dev/null
    smoke_container=""
done

echo "compose services"
docker compose --project-name "$smoke_project_name" \
    --file "$smoke_repository_root/compose.yaml" up --detach --build --wait \
    --no-deps modbus-mock modbus-mock-h2
for smoke_service in modbus-mock modbus-mock-h2; do
    docker compose --project-name "$smoke_project_name" \
        --file "$smoke_repository_root/compose.yaml" exec -T "$smoke_service" \
        python -m saj_modbus_mock healthcheck
done
