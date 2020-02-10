FROM python:3.7
RUN pip install uwsgi && pip install psycopg2-binary

EXPOSE 8001

#COPY uwsgi.ini /var/conf/uwsgi.ini
#COPY main.py /var/src/main.py
#CMD cat /var/src/main.py

CMD cp -T /var/app/uwsgi.log /var/app/uwsgi.log.old && echo "" > /var/app/uwsgi.log

CMD uwsgi /var/conf/uwsgi.ini --need-app

WORKDIR /var/app/backend/