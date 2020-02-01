#!/usr/bin/env bash
set -e

#if [ "$1" = 'toolchain' ]; then
#    if [ "$(id -u)" = '0' ]; then
#        service ssh restart;
#        passwd toolchain;
#    fi;
#    exec gosu toolchain /bin/bash;
#else
#    exec "$@";
#fi;

service cron restart

exec /docker-entrypoint.sh "$@"