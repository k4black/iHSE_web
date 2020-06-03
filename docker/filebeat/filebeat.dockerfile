#FROM docker.elastic.co/beats/filebeat:7.7.0
FROM ubuntu:18.04

USER root

RUN apt-get update && \
	apt-get install -y --no-install-recommends curl ca-certificates && \
	rm -rf /var/lib/apt/lists/*

ADD https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.7.0-amd64.deb /filebeat-7.7.0-amd64.deb
RUN dpkg -i filebeat-7.7.0-amd64.deb && \
    rm filebeat-7.7.0-amd64.deb && \
    mv /etc/filebeat/filebeat.yml /etc/filebeat/filebeat_default.yml
#    mv /etc/filebeat/modules.d/nginx.yml.disabled /etc/filebeat/modules.d/nginx_old.yml.disabled
COPY filebeat.yml /etc/filebeat/filebeat.yml
#COPY nginx.yml /etc/filebeat/modules.d/nginx.yml

CMD ["filebeat", "-e"]