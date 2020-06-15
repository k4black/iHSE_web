# A Static+Dynamic Site using Docker uwsgi and Nginx

This folder contains code for building dynamic website served using 3 separate Docker containers with nginx, uwsgi and postgre. 
Nginx and uwsgi configs are located in `conf` folder. The Docker-compose file contains commands to build a Docker Image.

To build a Docker image from the Dockerfile, run the following command from inside this directory
 
 
For run light-weight local testing configuration. (without ELK stack)
```sh
$ docker-compose -f docker-compose-local-light.yml up --build
```

For run full local testing configuration.
```sh
$ docker-compose -f docker-compose-local.yml up --build
```



To run the server configuration of Docker containers, use the following command
```sh
$ docker-compose -f docker-compose.yml up --build -d
```

This will start serving the static site on port 443. If you visit `https://ihse.tk:443` in your browser, you should be able to see our site!



```sh
$ docker-compose close
```



TODO  
