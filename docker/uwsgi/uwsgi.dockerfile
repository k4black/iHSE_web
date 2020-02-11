FROM python:3.7
COPY requirements.txt /tmp/requirements.txt
RUN python3.7 -m pip install --no-cache-dir -r /tmp/requirements.txt

#EXPOSE 8001

COPY uwsgi.ini /var/conf/uwsgi.ini
#COPY main.py /var/src/main.py
#CMD cat /var/src/main.py

ENV PYTHONPATH "${PYTHONPATH}:/var/app/backend/"

#WORKDIR /var/app/backend/

CMD touch /var/log/uwsgi.log
CMD cp -T /var/log/uwsgi.log /var/log/uwsgi.log.old && echo "" > /var/log/uwsgi.log

ENTRYPOINT ["uwsgi"]
CMD ["/var/conf/uwsgi.ini", "--need-app"]