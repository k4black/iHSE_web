# A Static+Dynamic Site using Docker uwsgi and Nginx

This folder contains code for building dynamic website served using 3 separate Docker containers with nginx, uwsgi and postgre. 
Nginx and uwsgi configs are located in `conf` folder. The Docker-compose file contains commands to build a Docker Image.

To build a Docker image from the Dockerfile, run the following command from inside this directory

```sh
$ docker-compose build
```

To run the image in a Docker containers, use the following command
```sh
$ docker-compose up -d
```

This will start serving the static site on port 443. If you visit `https://ihse.tk:443` in your browser, you should be able to see our site!
Run separated docker images `uwsgi_docker` `nginx_docker` `database_docker`.


```sh
$ docker-compose close
```



TODO  