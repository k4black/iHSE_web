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



This is the source code of the **website** for the education multi-disciplinary **summer camp** 'iHSE' from the Higher School of Economics - Nizhny Novgorod.


## Why do we need a website?

In short, it will make life easier for the camp organizers. 


### The ability of the participant: 

* Schedule  
During the camp, participants attend various lectures, master classes and entertainment events. The site provides an opportunity to view the schedule for each day and information on each event separately.

* Credits  
Participants receive "educational credits" for participation in educational events or active participation in the life of the camp. By the end of the camp, participants must collect a certain number of credits.  
On the personal page, you can view the history of receiving credits and current amount of it.

* Projects  
During the camp, each participant must invent, develop and protect their project (individually or as part of a group). On the "projects" page, you can view all created projects and sign up for them if the participant does not currently have projects. The project is also shown in the personal account page.   

* Enrolls  
There are two types of educational events - lectures and masterclasses. And some masterclasses have a limited number of places to visit and you need to make an enroll in advance. Any participant can enroll for the event from the registration page, if there are enough available places. 

* Account  
The personal page displays the participant's credit history for all days of the camp, as well as the current amount of credits and the credits goal.  
It is also possible to delete the current project, edit or leave it. You can also create a new one if you don't already have one. 

* Feedback  
A page to collect comments on some days. Reviews are collected for events that a person visited on that day, as well as for people who remembered in recent days (top). 


### Opportunities for a Moderator (team Leader)

* Credits  
View and edit the history of getting credits for all camp participants in the form of a table. 

* Profiles (TODO)  
You can view users' pages to see beautiful graphics of their credits.

* Events  
Ability to edit the annotation for events and the maximum number of people in the event. 

* Checkin  
For each educational event, users must register for it (give credits) by scanning the QR codes of participants at the end of the class event. 

* Timelines  
View events in the timeline format. For each location, the events that will take place in it are shown.  
TODO visual editing Capability. 


### Opportunities for a Administrator
All features of the moderator, as well as: 


* Schedule (Calendar)  
Ability to edit\create\copy\delete events. 

* Data base  
Ability to fully edit all parameters in the database. `[DANGEROUSLY]`

* Reports
View **depersonalized** statistics on feedback. 
Both top participants (selected by others) and statistics on events and counselors who conducted them. 

* Statistics  
Statistics on the number of people in each of the units and their division by gender. It also shows the number and percentage of people who have accumulated the required number of credits and the average number of credits. 

* Configuration  
Allows you to configure the number of default credits received for different types of events. As well as set a requirement for the number of credits collected.



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

