# This actions should be taken ONLY ONE TIME, when server is setting up



sudo apt-get update
sudo mkdir /var/app/
sudo chmod a-w /var/app/



# ======== SSH user ========
sudo adduser ubuntu-ssh




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

usermod -aG docker user


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




# ======== FTP server ========   # TODO: USE CD user with scp or ssh git pull
echo "Setup FTP server"
echo "@see https://www.digitalocean.com/community/tutorials/how-to-set-up-vsftpd-for-a-user-s-directory-on-ubuntu-16-04"


sudo apt-get -y install vsftpd
sudo adduser ubuntu-ftp
sudo chown ubuntu-ftp:ubuntu-ftp /var/app/
sudo chmod a+w /var/app/

# Config file
#sudo nano /etc/vsftpd.conf

#ip
ip=$(curl ipinfo.io/ip)
echo "  Public IP: $ip"

# /etc/vsftpd/vsftpd.conf or /etc/vsftpd.conf
ftp_conf="/etc/vsftpd.conf"
touch $ftp_conf

echo "
listen=YES
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES

anonymous_enable=NO

# Additional configuration
pasv_enable=YES
pasv_min_port=1024
pasv_max_port=1048
pasv_address=$ip
local_root=/var/app
" >> $ftp_conf




# ======== Softlinks to logs and etc  ========
echo "Setup logs Softlinks"

# TODO: Log softlinks















# setup SSL sertificate (Certbot)
# https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx

echo "https://certbot.eff.org/lets-encrypt/ubuntuxenial-nginx"
sudo apt-get update
sudo apt-get -y install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update

sudo apt-get -y install certbot python-certbot-nginx

certbot register --email me@example.com

sudo certbot --nginx  # This Setup directly nginx sertificate  # TODO: Add to docker
sudo certbot certonly --nginx  # Only got certificate

certbot certonly --dry-run -d example.com -d www.example.com  # TEST get sert
certbot certonly -d example.com -d www.example.com # TRYLY got sert
certbot certonly -d example.com -d www.example.com -d shop.example.com  # Add subdomen

openssl x509 -text -in /etc/letsencrypt/live/example.com/cert.pem # Check sert


sudo certbot renew --dry-run



# Config file for cerbot
/etc/letsencrypt/cli.ini

authenticator = webroot
webroot-path = /var/www/html
post-hook = service nginx reload
text = True




# Config ngix
server {
    server_name www.example.com;
    listen www.example.com:443 ssl; # default_server;
    # выше можно добавить default_server для клиентов без SNI

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 127.0.0.1 8.8.8.8;

    # исключим возврат на http-версию сайта
    add_header Strict-Transport-Security "max-age=31536000";

    # явно "сломаем" все картинки с http://
    add_header Content-Security-Policy "img-src https: data:; upgrade-insecure-requests";

    # далее всё что вы обычно указываете
    #location / {
    #    proxy_pass ...;
    #}
}









# удалит все файлы и папки старше 10 дней. вы можете добавить его в ежедневный cron.
sudo find /tmp -type f -atime +10 -delete


du -h | sort -h