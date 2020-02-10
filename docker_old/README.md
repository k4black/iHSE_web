# Introduction to our Docker deployment
## Database
We are using `postgres:12.1`-based custom image with built-in `cron`-based 
automatic backup mechanism.  
To build DB image, `cd` to this folder and run: 
```shell script
docker build . -f database.dockerfile -t postgres_cron:12.1
```
To run the container, execute the following:
```shell script
docker run --rm --name db_pg -d -v /some/folder:/mounted -p 5432:5432 postgres_cron:12.1
```
And a quick peek into all the options above:
* `--rm` kills the container after in will be stopped. 
 Backups wil be preserved, so don't worry.
* `--name db_pg` is an optional stuff for convenience, read the docs if you want.
* `-d` is to detach the container and put it into the background
* `-v ...` maps host folder to container folder. **Note:** for our model,
 the host folder must contain `back` file, which holds the DB backup for initial loading.
 After DB will be loaded from this file, it will be backed up into the 
 `postgres.backup` file. When we'll implement compressing,
 this mechanism's gonna change a bit, but nothing serious
### Further reading
* [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
* [`docker build` reference](https://docs.docker.com/engine/reference/commandline/build/)
* [`docker run` reference](https://docs.docker.com/engine/reference/commandline/run/) 