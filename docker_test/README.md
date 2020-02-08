# A Static+Dynamic Site using Docker uwsgi and Nginx

TODO  

This repo contains code for building a simple dynamic website served using 2 separate Docker containers with nginx and docker. The code for the site is contained in `index.html`, and the Nginx config is in `default.conf`. The Dockerfile contains commands to build a Docker Image.

To build a Docker image from the Dockerfile, run the following command from inside this directory

```sh
$ docker-compose build
```
This will produce the following output


To run the image in a Docker containers, use the following command
```sh
$ docker-compose up -d
```

Run separated docker images `uwsgi_docker` `nginx_docker` `?database_docker`


```sh
$ docker-compose close
```

This will start serving the static site on port 80. If you visit `http://localhost:80` in your browser, you should be able to see our static site!