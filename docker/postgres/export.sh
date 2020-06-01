#!/usr/bin/env bash

cd /var/app/docker

dt=$(date '+%Y.%m.%d_%H:%M:%S');
echo "Export time $dt"

echo "Password: root"
docker exec -it database_docker pg_dump -h database -p 5432 -d ihse -U postgres -W -f /var/lib/postgresql/exports/$dt.sql
#docker exec -it database_docker pg_dump  --dbname=database://postgres:root@127.0.0.1:5432/ihse -f /var/lib/postgresql/exports/$dt.sql
