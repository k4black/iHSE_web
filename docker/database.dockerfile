FROM postgres:12.1
CMD sudo -u postgres postgres -D /var/lib/postgresql/data/pgdata
