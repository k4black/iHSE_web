echo "setup file" > /var/tmp/test.txt
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up
