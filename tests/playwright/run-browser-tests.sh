#!/bin/sh
set -u

mkdir -p playwright-report/home-assistant test-results/home-assistant
playwright_test_status=0
npm run test:browser:home-assistant || playwright_test_status=$?
chown -R "${PLAYWRIGHT_RESULT_UID}:${PLAYWRIGHT_RESULT_GID}" \
    playwright-report/home-assistant test-results/home-assistant
exit "$playwright_test_status"
