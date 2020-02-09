
import psycopg2

# conn = psycopg2.connect('dbname=root user=root password=root',port=5432)
conn = psycopg2.connect(database="root", user="root", password="root", host="database_docker", port="5432")

cursor = conn.cursor()


def application(environ, start_response):
    start_response('200 damn', [('Content-Type', 'text/html')])
    return [(f"Ololo! YOu want to {environ['PATH_INFO']}").encode("utf-8")]
