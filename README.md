# iHSE_web

Master:  
![pystyle](https://github.com/k4black/iHSE_web/workflows/pystyle/badge.svg)
![pytests](https://github.com/k4black/iHSE_web/workflows/pytests/badge.svg)
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/master/graph/badge.svg)

Release:  
TODO  
![codecov](https://codecov.io/gh/k4black/iHSE_web/branch/release/graph/badge.svg)





TODO


## Branches 

* **`develop`**  
Developing branch. No style and code checks. For everyday commits. You can fork some branch  

* **`master`**  
Master branch. So-stable version of the `ihse` site. Every commit will trigger _**testing**_ and _**codestyle**_ checks.

* **`release`**  
100% stable branch. Every commit will be _**automatically deployed**_ to the server.
Each release should be taken (fork) from master branch and after hotfixes (if it necessary) commit marked with a version tag.

So, develop flow looks like:
1. Developing in `develop` branch
2. Merge to `master` and do style and tests corrections. 
start again or 
3. Merge to `release` and do integration testing 
4. Tagging and merge to other branches 




## Structure 
No specail engine.  
Static pages provided by `nginx` server and than dinymic data sending throught ajax requerst to `uwsgi` server.


### Frontend 
Pure `js` with small inclusions of third-party components (e.g. progressbar). 

### Backend
Using python `uwsgi` web server for users' interactions. 



## Docker
Several docker containers witch interact with each other.


## Testing 
TODO

