FROM python:3.7
RUN pip install uwsgi

EXPOSE 8001

#COPY uwsgi.ini /var/conf/uwsgi.ini
#COPY main.py /var/src/main.py
#CMD cat /var/src/main.py

CMD uwsgi /var/conf/uwsgi.ini --wsgi-file /var/app/backend/main.py --need-app

WORKDIR /var/app/backend/