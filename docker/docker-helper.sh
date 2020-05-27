#!/usr/bin/env bash
set -e

# container is started as root user, and only in docker-entrypoint.sh all su-like stuff is performed
service cron restart

exec /docker-entrypoint.sh "$@"