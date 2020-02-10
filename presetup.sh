# This actions should be tacken ONLY ONE TIME, when server is setuping


# FTP server
echo "Setup FTP server"


echo "https://www.digitalocean.com/community/tutorials/how-to-set-up-vsftpd-for-a-user-s-directory-on-ubuntu-16-04"


sudo apt-get update
sudo apt-get install vsftpd


sudo adduser ubuntu-ftp

sudo mkdir /var/app/
sudo chown ubuntu-ftp:ubuntu-ftp /var/app/
sudo chmod a-w /var/app/


sudo nano /etc/vsftpd.conf




# Docker
echo "Setup Docker"

sudo apt-get remove docker docker-engine docker.io containerd runc

sudo apt install docker.io

sudo systemctl start docker
sudo systemctl enable docker

$ docker --version





# Docker compose
echo "Setup Docker-compose"

sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

$ docker-compose --version



# database

echo "Setup database"

sudo mkdir /var/lib/postgresql/data
sudo chmod +a /var/lib/postgresql/data  # TODO: check




