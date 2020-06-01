#!/usr/bin/env bash
# This actions run every deploying of new version

# echo "setup file" > /var/tmp/test.txt

cd /var/app/docker
#echo "Building docker containers. "
#sudo docker-compose build
echo "Stopping old docker containers. "
#sudo docker-compose down
sudo docker-compose stop
echo "Running docker containers. "
#sudo docker-compose up -d
sudo docker-compose -f ./docker-compose.yml up --build -d