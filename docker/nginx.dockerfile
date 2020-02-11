FROM nginx:alpine

EXPOSE 80
EXPOSE 443

#COPY /usr/conf/default.conf /etc/nginx/conf.d/default.conf
#COPY index.html /usr/share/nginx/html/index.html

#CMD cat /etc/nginx/nginx.conf
#CMD ls /etc/nginx/conf.d/

WORKDIR /var/app/frontend/