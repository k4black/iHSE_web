cp -T /home/ubuntu/uwsgi.log /home/ubuntu/uwsgi.log.old
echo "" > /home/ubuntu/uwsgi.log
sudo nginx
sudo uwsgi /home/ubuntu/iHSE_web/backend/uwsgi.ini
