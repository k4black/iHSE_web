FROM logstash:7.7.0
USER root
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
RUN chown 1000:0 /usr/share/logstash/pipeline/logstash.conf
#RUN logstash-plugin install logstash-filter-dissect
USER 1000
