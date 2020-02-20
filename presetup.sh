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

# TODO: Automatic push to config file
/etc/vsftpd/vsftpd.conf
listen=YES
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES

anonymous_enable=NO

# Additional configuration
pasv_enable=YES
pasv_min_port=1024
pasv_max_port=1048
pasv_address=[SERVER IP ADRESS]
local_root=/var/app




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
sudo chmod +rw /var/lib/postgresql/data  # TODO: check




# setup SSL sertificate (Certbot)
# https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx

echo "https://certbot.eff.org/lets-encrypt/ubuntuxenial-nginx"
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update


udo apt-get install certbot python-certbot-nginx


certbot register --email me@example.com



sudo certbot --nginx  # This Setup directly nginx sertificate  # TODO: Add to docker
sudo certbot certonly --ngin  x  # Only got certificate


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