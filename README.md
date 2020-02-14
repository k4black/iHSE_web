# iHSE_web

Master:  
![pystyle](https://github.com/k4black/iHSE_web/workflows/pystyle/badge.svg)
![pytests](https://github.com/k4black/iHSE_web/workflows/pytests/badge.svg)
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/master/graph/badge.svg)

Release:  
![pystyle](https://github.com/k4black/iHSE_web/workflows/pystyle/badge.svg?branch=release)
![pytests](https://github.com/k4black/iHSE_web/workflows/pytests/badge.svg?branch=release)
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/release/graph/badge.svg)
![deploy](https://github.com/k4black/iHSE_web/workflows/deploy/badge.svg?branch=release)





TODO


## Branches 

* **`develop`**  
Development branch. No code style and tests. Should be used for everyday internal development process. You can fork some 'feature' branches from here, which have to be merged to this branch in the future. 

* **`master`**  
Master branch. So-stable version of the iHSE website. Every commit will trigger _**testing**_ and _**codestyle**_ checks. 
TODO: Every commit also will run _**integration testing**_ in docker containers with prepared test database. 

* **`release`**  
100% stable branch. Every commit will be _**automatically deployed**_ to the server throught _ftp_ and run `setup.sh` script.
Each release should be taken (forked) from master branch and after hotfixes (if necessary) merged with `release` branch, Moreover, each commit marked with a version tag.

So, internal development flow looks like:
1. Developing in `develop` branch (and _feature_ branches, if necessary)
2. Merging to `master` and performing codestyle and tests corrections
start again or 
3. Do integration testing. Then merge to `release` 
4. Tagging and merging to other branches 

And external development flow (public Pull Requests) looks like:
1. Hahaha, TODO here!



## Structure 
No special website/webserver engine.  
Static pages are provided by `nginx` server and dynamic data (AJAX) goes from `uwsgi` server.
![structure](https://retifrav.github.io/blog/2019/11/03/nginx-uwsgi-python-scripts/images/nginx-uwsgi.png)


### Frontend 
Pure `js` with small inclusions of third-party components (e.g. progress-bar or progress-circle). 

### Backend
Using python `uwsgi` web server for users' interactions. 
Together with `PostgreSQL` database.
TODO: Database is commited (backup) to a cloud server, to faster set it up during deploy process. 


## Docker
Several docker containers witch interact with each other.


## Testing 
TODO

