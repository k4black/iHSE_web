# iHSE_web

Master:  
![pystyle](https://github.com/k4black/iHSE_web/workflows/pystyle/badge.svg)
![pytests](https://github.com/k4black/iHSE_web/workflows/pytests/badge.svg)
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/master/graph/badge.svg)

Release:  
TODO
![pystyle](https://github.com/k4black/iHSE_web/workflows/pystyle/badge.svg)
![pytests](https://github.com/k4black/iHSE_web/workflows/pytests/badge.svg)
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/release/graph/badge.svg)





TODO


## Branches 

* **`develop`**  
Developing branch. No code style and tests checks. Should be used for everyday develop commits. You can fork some 'feature' branches, witch have to be merged to this branch in the future. 

* **`master`**  
Master branch. So-stable version of the `ihse` site. Every commit will trigger _**testing**_ and _**codestyle**_ checks. 
TODO: Every commit also will run _**integration testing**_ in docker containets with prepareg test database. 

* **`release`**  
100% stable branch. Every commit will be _**automatically deployed**_ to the server throught _ftp_ and run `setup.sh` script.
Each release should be taken (fork) from master branch and after hotfixes (if it necessary) merged with `release` branch, Moreover, each commit marked with a version tag.

So, develop flow looks like:
1. Developing in `develop` branch (and _feature_ branches, if necessary)
2. Merge to `master` and do style and passing tests corrections. 
start again or 
3. Do integration testing. Then Merge to `release` 
4. Tagging and merge to other branches 




## Structure 
No specail engine.  
Static pages provided by `nginx` server and than dinymic data, sending throught ajax requests, goes to `uwsgi` server.
![structure](https://retifrav.github.io/blog/2019/11/03/nginx-uwsgi-python-scripts/images/nginx-uwsgi.png)


### Frontend 
Pure `js` with small inclusions of third-party components (e.g. progressbar or progress-circle). 

### Backend
Using python `uwsgi` web server for users' interactions. 
Together with `Posgres SQL` database.
TODO: Database are commited (backup) to a cloud server, to faster set it up during deploy process. 


## Docker
Several docker containers witch interact with each other.


## Testing 
TODO

