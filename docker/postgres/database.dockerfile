FROM postgres:12.1

EXPOSE 5431

USER root
# TODO: archive in case of big files!
# https://www.postgresql.org/docs/9.1/backup-dump.html
COPY docker-helper.sh /docker-helper.sh

RUN chown -R postgres:postgres /docker-entrypoint-initdb.d/

RUN mkdir /mounted && \
    echo "if [ \"\$(psql --command=\"select * from users;\" && echo \$? || echo \$?)\" -ne 0 ]; then psql postgres < /mounted/back; else pg_dump postgres > /mounted/postgres.backup; fi;" > /backupdb.sh && chmod 744 /backupdb.sh && \
    echo "0 * * * * /backupdb.sh" > /backupdb.cron && chown postgres:postgres /backupdb.sh /backupdb.cron && crontab -u postgres /backupdb.cron && \
    chown -R postgres:postgres /mounted
ENTRYPOINT ["/docker-helper.sh"]
CMD ["postgres"]