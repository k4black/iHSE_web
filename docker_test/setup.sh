
https://www.digitalocean.com/community/tutorials/how-to-set-up-vsftpd-for-a-user-s-directory-on-ubuntu-16-04

sudo apt-get update
sudo apt-get install vsftpd


sudo adduser ubuntu-ftp

sudo mkdir /var/app/
sudo chown ubuntu-ftp:ubuntu-ftp /var/app/
sudo chmod a-w /var/app/


sudo nano /etc/vsftpd.conf



