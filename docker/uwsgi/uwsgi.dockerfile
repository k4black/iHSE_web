FROM python:3.7
COPY requirements.txt /tmp/requirements.txt
RUN python3.7 -m pip install --no-cache-dir -r /tmp/requirements.txt

#EXPOSE 8001

RUN mkdir -p /var/conf/
# COPY uwsgi.ini /var/conf/uwsgi.ini
ADD uwsgi.ini /var/conf/

ENV PYTHONPATH "${PYTHONPATH}:/var/app/backend/"

#WORKDIR /var/app/backend/

CMD touch /var/log/uwsgi/uwsgi.log
CMD cp -T /var/log/uwsgi/uwsgi.log /var/log/uwsgi/uwsgi.log.old && echo "" > /var/log/uwsgi/uwsgi.log

ENTRYPOINT ["uwsgi"]
CMD ["--ini", "/var/conf/uwsgi.ini", "--need-app"]