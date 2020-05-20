FROM nginx:1.17

RUN apt-get update && \
	apt-get install -y --no-install-recommends curl ca-certificates && \
	rm -rf /var/lib/apt/lists/*

EXPOSE 80
EXPOSE 443

RUN rm /etc/nginx/conf.d/default.conf
COPY ihse_local.conf /etc/nginx/conf.d/ihse.conf