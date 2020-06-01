#!/usr/bin/env bash
##!/bin/bash - doesn't set the minimal environment
#set -e
#
## container is started as root user, and only in docker-entrypoint.sh all su-like stuff is performed
#service cron restart
#
#exec /docker-entrypoint.sh "$@"


#The $EUID environment variable holds the current user's UID. Root's UID is 0. Use something like this in your script:

#_term() {
#    echo "got SIGTERM"
#    kill -TERM "$child"
#}

#printf "EUID is $EUID\n"
#printf "UID is $UID\n"

#trap _term SIGTERM


function help {
    echo "usage: docker-helper.sh start/stop [-l local] [-d demonized]"
}



# Check command  
command=$1;  shift ;
if [ ! "$command" = "start" ] &&  [ ! "$command" = "stop" ] ; then
    echo "Unknown command $command."
    help
    exit 3
fi


# Parse command line args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -l|--local) local=true ;;
        -d|--demonized) demonized=true ;;
        -h|--help) help; exit 0 ;;
        *) echo "Unknown argument $1."; help; exit 3 ;;
    esac
    shift
done




if [ "$EUID" -ne 0 ]
  then echo "Please run as root/sudo"
  exit 0
fi

conf_file="./docker-compose.yml"
if [ "$local" = true ] ; then
    conf_file="./docker-compose-local.yml"
fi

if [ "$command" = "start" ]
    then echo "starting..."
    if [ -d "../local_run" ]
        then echo "local_run exists, setting permissions..."
        chown -R 1000:0 ../local_run/logstash
        chown -R 1000:0 ../local_run/elasticsearch
        chown -R 999:999 ../local_run/postgres
        chown -R 0:0 ../local_run/nginx
        chown -R 0:0 ../local_run/uwsgi
        echo "permission set"
    fi
    if [ ! -d "../local_run" ]
        then echo "local_run doesn't exist, creating..."
        mkdir -p ../local_run/logstash/data
        mkdir -p ../local_run/elasticsearch/data
        mkdir -p ../local_run/elasticsearch/logs
        mkdir -p ../local_run/postgres/pgdata
        mkdir -p ../local_run/postgres/exports
        mkdir -p ../local_run/nginx/logs
        mkdir -p ../local_run/uwsgi/logs
        echo "local_run created, setting permissions..."
        chown -R 1000:0 ../local_run/logstash
        chown -R 1000:0 ../local_run/elasticsearch
        chown -R 999:999 ../local_run/postgres
        chown -R 0:0 ../local_run/nginx
        chown -R 0:0 ../local_run/uwsgi
        echo "permission set"
    fi
    echo "starting Compose..."

    if [ "$demonized" = true ] ; then
        docker-compose -f "$conf_file" up -d
        echo "demonized."
    else
        docker-compose -f "$conf_file" up
    fi
fi

if [ "$command" = "stop" ]
    then echo "stopping..."
#    if [ "$local" = true ] ; then
    docker-compose -f "$conf_file" stop
#    fi
    echo "gracefully stopped all containers"
    echo "local_run contains all mounted data, manage permissions there according to your needs"
fi;