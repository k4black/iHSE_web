FROM nginx:alpine

EXPOSE 80
EXPOSE 443

RUN rm /etc/nginx/conf.d/default.conf
COPY ihse_local.conf /etc/nginx/conf.d/ihse.conf