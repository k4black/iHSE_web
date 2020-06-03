FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ihse.conf /etc/nginx/conf.d/ihse.conf
