#!/usr/bin/env bash
# This actions should be taken ONLY ONE TIME, when server is setting up



sudo apt-get update
sudo mkdir /var/app/
sudo chmod a+w /var/app/

#ip
ip=$(curl ipinfo.io/ip)
echo "Public IP: $ip"


sudo touch /etc/sudoers.d/90-cloudimg-ubuntu
sudo echo "aychedee ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/90-cloudimg-ubuntu


# ======== SSH user ========
echo "First use: <ssh-keygen -y -f ~/.ssh/ihse.pem>"
sudo adduser --disabled-password --gecos "" ubuntu-ssh

sudo mkdir /home/ubuntu-ssh/.ssh/
sudo cp /home/ubuntu/.ssh/authorized_keys /home/ubuntu-ssh/.ssh/authorized_keys
sudo chown ubuntu-ssh:ubuntu-ssh /home/ubuntu-ssh/.ssh/
sudo chown ubuntu-ssh:ubuntu-ssh /home/ubuntu-ssh/.ssh/authorized_keys
sudo chmod 700 /home/ubuntu-ssh/.ssh/
sudo chmod 600 /home/ubuntu-ssh/.ssh/authorized_keys


echo "@see https://askubuntu.com/questions/192050/how-to-run-sudo-command-with-no-password"
sudo nano /home/ubuntu-ssh/.ssh/authorized_keys
sudo usermod -aG sudo ubuntu-ssh
sudo usermod -aG admin ubuntu-ssh




sudo chown ubuntu-ssh:ubuntu-ssh /var/app/



# ======== Docker setup ========
echo "Setup Docker"
echo "@see https://habr.com/ru/post/445448/"
# nginx+cerbot in docker


# Docker
echo "  docker"

sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get -y install docker.io

# Docker autorun
sudo systemctl enable docker
sudo systemctl start docker

echo "  docker installed with version: $(docker --version)"

sudo usermod -aG docker ubuntu
sudo usermod -aG docker ubuntu-ssh


# Docker compose
echo "  docker-compose"

sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

echo "  docker-compose installed with version: $(docker-compose --version)"




# ======== Database folders setup ========
echo "Setup database folders"

sudo mkdir /var/lib/postgresql/data
sudo chmod +rw /var/lib/postgresql/data  # TODO: check




# ======== Softlinks to logs and etc  ========
echo "Setup logs Softlinks"

# TODO: Log softlinks








# удалит все файлы и папки старше 10 дней. вы можете добавить его в ежедневный cron.
sudo find /tmp -type f -atime +10 -delete
du -h | sort -h



