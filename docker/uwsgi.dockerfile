FROM python:3.7
RUN pip install uwsgi && pip install psycopg2-binary && pip install configparser

EXPOSE 8001

#COPY uwsgi.ini /var/conf/uwsgi.ini
#COPY main.py /var/src/main.py
#CMD cat /var/src/main.py


ENV PYTHONPATH "${PYTONPATH}:/var/app/backend/"

WORKDIR /var/app/backend/


CMD touch /var/log/uwsgi.log
CMD cp -T /var/log/uwsgi.log /var/log/uwsgi.log.old && echo "" > /var/log/uwsgi.log

CMD uwsgi /var/conf/uwsgi.ini --need-app
