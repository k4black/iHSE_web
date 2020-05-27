#!/usr/bin/env bash
set -e

# container is started as root user, and only in docker-entrypoint.sh all su-like stuff is performed
service cron restart

#rm -rf /var/lib/postgresql/data/*
#chmod 755 /docker-entrypoint-initdb.d/
#chmod 644 /docker-entrypoint-initdb.d/example.pgsql

#chmod=D755,F644

exec /docker-entrypoint.sh "$@"