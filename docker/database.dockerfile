FROM postgres:12.1

EXPOSE 5431

CMD sudo -u postgres postgres -D /var/lib/postgresql/data/pgdata
