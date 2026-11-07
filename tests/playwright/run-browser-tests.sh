#!/bin/sh
set -u

mkdir -p playwright-report/home-assistant test-results/home-assistant
exec npm run test:browser:home-assistant
