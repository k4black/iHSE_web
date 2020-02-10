# This actions run every deploying of new version

echo "setup file" > /var/tmp/test.txt

echo "Building docker containers."
sudo docker-compose build ./docker/
echo "Stopping old docker containers."
sudo docker-compose down
sudo docker-compose stop
echo "Running docker containers."
sudo docker-compose up
