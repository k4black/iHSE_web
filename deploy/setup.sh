https://stackoverflow.com/questions/7052875/setting-up-ftp-on-amazon-cloud-server

sudo apt-get upgrade
sudo apt-get install vsftpd

/etc/vsftpd/vsftpd.conf
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES

anonymous_enable=NO

# Additional configuration
pasv_enable=YES
pasv_min_port=1024
pasv_max_port=1048
pasv_address=xx-xxx-xxx-xx
local_root=/var/app
