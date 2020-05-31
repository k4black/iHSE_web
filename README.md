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


## Table of Contents
- [Why do we need a website?](#why-do-we-need-a-website)
  - [Opportunities for a Participant](#opportunities-for-a-participant)
  - [Opportunities for a Moderator](#opportunities-for-a-moderator)
  - [Opportunities for a Administrator](#opportunities-for-a-administrator)
- [Branches](#branches)
- [Structure](#structure)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [Docker](#docker)
- [Logging](#logging)
- [Testing](#testing)
 


## Why do we need a website?

In short, it will make life easier for the camp organizers. 


### Opportunities for a Participant:
(common camp participant)  

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


### Opportunities for a Moderator:
(team Leader)

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


### Opportunities for a Administrator:
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

* Logging  
Access to logs, some charts, dashboards and statistics in Kibana HTTP GUI.



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
@see docker/readme.md



## Logging
Using `ELK` stack + `Beats` services. 
![logging](https://www.elastic.co/static/images/elk/elk-stack-elkb-diagram.svg)

System collect all logs from nginx, uwsgi and postgres database.

ELK stack can be shortly described as linear stack:
* **Logs**: Server logs that need to be analyzed are identified
* **Beats**: Server logs that need to be analyzed are identified
* **Logstash**: Collect logs and events data. It even parses and transforms data
    * 5000 - TCP input
* **ElasticSearch**: The transformed data from Logstash is Store, Search, and indexed.
    * 9200 - HTTP
    * 9300 - TCP transport
* **Kibana**: Kibana uses Elasticsearch DB to Explore, Visualize, and Share
    * 5601 - HTTP 

![logging](https://www.guru99.com/images/tensorflow/082918_1504_ELKStackTut2.png)


Full logging stat available on `ihse.tk:5601`.






## Testing 
TODO

