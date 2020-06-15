FROM python:3.7
COPY requirements.txt /tmp/requirements.txt
RUN python3.7 -m pip install --no-cache-dir -r /tmp/requirements.txt

#EXPOSE 8001

RUN mkdir -p /var/conf/
# COPY uwsgi.ini /var/conf/uwsgi.ini
COPY uwsgi.ini /var/conf/

#ADD ihse.ini /var/conf/
COPY ihse.ini /var/conf/ihse/default_ihse.ini
COPY places.list /var/conf/ihse/default_places.list

ENV PYTHONPATH "${PYTHONPATH}:/var/app/backend/"

ENTRYPOINT ["uwsgi"]
CMD ["--ini", "/var/conf/uwsgi.ini", "--need-app"]