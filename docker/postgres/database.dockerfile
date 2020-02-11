FROM postgres:12.1

EXPOSE 5431

USER root
# TODO: archive in case of big files!
# https://www.postgresql.org/docs/9.1/backup-dump.html
COPY docker-helper.sh /docker-helper.sh
RUN mkdir /mounted && \
    echo "if [ \"\$(psql --command=\"select * from users;\" && echo \$? || echo \$?)\" -ne 0 ]; then psql postgres < /mounted/back; else pg_dump postgres > /mounted/postgres.backup; fi;" > /backupdb.sh && chmod 744 /backupdb.sh && \
    echo "* * * * * /backupdb.sh" > /backupdb.cron && chown postgres:postgres /backupdb.sh /backupdb.cron && crontab -u postgres /backupdb.cron && \
    chown -R postgres:postgres /mounted
#    printf "service cron start\npsql postgres < /mounted/back\n" > /cron_helper.sh && chmod 744 /cron_helper.sh && \
#    printf '#!/bin/bash\nset -m\n/docker-entrypoint.sh "$@" &\n/cron_helper.sh\nfg %%1\n' > /helper-entrypoint.sh && chmod 744 /helper-entrypoint.sh
ENTRYPOINT ["/docker-helper.sh"]
CMD ["postgres"]