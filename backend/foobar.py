import urllib.parse
import sqlite3

conn = sqlite3.connect("/home/ubuntu/main.sqlite")
cursor = conn.cursor()

# Users
cursor.execute("""CREATE TABLE IF NOT EXISTS  "users" (
                  	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                  	"user_type"	INTEGER,
                  	"phone"	TEXT,
                  	"name"	TEXT,
                    "pass"	INTEGER,
                  	"team"	INTEGER
                  );
               """)

# Sessions
cursor.execute("""CREATE TABLE IF NOT EXISTS  "sessions" (
                  	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                  	"user_id"	INTEGER,
                  	"user_agent"	TEXT,
                  	"last_ip"	TEXT,
                  	"time"	TEXT,
                  	FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)


cursor.execute("INSERT INTO users(user_type, phone, name, pass, team) VALUES(0, '+7122', 'A. Aagrh!', 11111, 0)")
cursor.execute("INSERT INTO users(user_type, phone, name, pass, team) VALUES(0, '+3221', 'B. TRdds!', 22222, 2)")
cursor.execute("INSERT INTO users(user_type, phone, name, pass, team) VALUES(1, '+7756', 'C. Yyts!', 55555, 0)")
conn.commit()

users = (
    (0, '+7 912', 'Audi', 52642, 1),
    (0, '+7 234', 'Mercedes', 57127, 0),
    (1, '+7 123', 'Skoda', 9000, 1),
    (0, '+7 332', 'Volvo', 29000, 0),
    (0, '+7 444', 'Bentley', 350000, 2),
    (1, '+7 666', 'Hummer', 41400, 0),
    (0, '+7 123', 'Volkswagen', 21600, 0)
)
cursor.executemany("INSERT INTO users(user_type, phone, name, pass, team) VALUES(?, ?, ?, ?, ?)", users)
conn.commit()


cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                  SELECT 0, '+7122', 'Audi', 11111, 0
                  WHERE NOT EXISTS(SELECT 1 FROM users WHERE pass=22221 OR name='Audi');""")


cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                  SELECT 0, '+7122', 'Rrra', 11111, 0
                  WHERE NOT EXISTS(SELECT 1 FROM users WHERE pass=52642 OR name='Rrra');""")


cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                  SELECT 0, '+7122', 'Rrra', 11111, 0
                  WHERE NOT EXISTS(SELECT 1 FROM users WHERE pass=22121 OR name='TTT');""")
conn.commit()




cursor.execute("INSERT INTO sessions(id, user_id, user_agent, last_ip, time) VALUES(16666, 6, 'AGENT', '5.5.5.5', '231.22')")
conn.commit()






# GET requare
def get(env, start_response, query):
    message_return = b"<p>Hello from uWSGI!</p>"

    s = ""
    for i in env.keys():
        s = s + str(i) + ":" + str(env[i]) + "\n"

    message_env = ("<p>" + s + "</p>")
    message_env = message_env.encode('utf-8')



    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    # ('Content-Length', str(len(message_return) + len(message_env)))
                    ])
    return [message_return, message_env, ("<p>" + request_body + "</p>").encode('utf-8')]



def login(env, start_response, name, passw):
# '302 Found'
    if True:
        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ('Set-Cookie', 'sessid=123; HttpOnly; Max-Age=31536000; Path=/'),
                        #('Location', env['HTTP_REFERER']),
                        #('Location', 'http://ihse.tk/login.html')
                        # ('Content-Length', str(len(message_return) + len(message_env)))
                        ])

    else:
        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ])


    return


# POST requare
def post(env, start_response, query):
#    print(query)
#    print(query['name'], query['pass'])

    if env['PATH_INFO'] == '/login':
        return login(env, start_response, query['name'], query['pass']);



'''
Resource - iHSE.tk/path/resource?param1=value1&param2=value2


REQUEST_METHOD: GET
PATH_INFO: /path/resource
REQUEST_URI: /path/resource?param1=value1&param2=value2
QUERY_STRING: param1=value1&param2=value2
SERVER_PROTOCOL: HTTP/1.1
SCRIPT_NAME:
SERVER_NAME: ip-172-31-36-110
SERVER_PORT: 50000
REMOTE_ADDR: USER_IP
HTTP_HOST: ihse.tk:50000
HTTP_CONNECTION: keep-alive
HTTP_PRAGMA: no-cache
HTTP_CACHE_CONTROL: no-cache
HTTP_ORIGIN: http: //ihse.tk
HTTP_USER_AGENT: USER_AGENT
HTTP_DNT: 1
HTTP_ACCEPT: */*
HTTP_REFERER: http: //ihse.tk/
HTTP_ACCEPT_ENCODING: gzip, deflate
HTTP_ACCEPT_LANGUAGE: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
wsgi.input: <uwsgi._Input object at 0x7f0ef198c810>
wsgi.file_wrapper: <built-in function uwsgi_sendfile>
wsgi.version: (1, 0)
wsgi.errors: <_io.TextIOWrapper name=2 mode='w' encoding='UTF-8'>
wsgi.run_once: False
wsgi.multithread: True
wsgi.multiprocess: True
wsgi.url_scheme: http
uwsgi.version: b'2.0.15-debian'
uwsgi.core: 1
uwsgi.node: b'ip-172-31-36-110'

'''
def application(env, start_response):

    urllib.parse.urlparse('https://someurl.com/with/query_string?a=1&b=2&b=3').query
        #a=1&b=2&b=3

    #urllib.parse.parse_qs('a=1&b=2&b=3');
        #{'a': ['1'], 'b': ['2','3']}

    #urllib.parse.parse_qsl('a=1&b=2&b=3')
        #[('a', '1'), ('b', '2'), ('b', '3')]

    query = dict( urllib.parse.parse_qsl( env['QUERY_STRING'] ) )
#     query = dict( urllib3.util.parse_url( env['QUERY_STRING'] ) )
        #{'a': '1', 'b': '3'}

    if env['REQUEST_METHOD'] == 'GET':
        return get(env, start_response, query)


    if env['REQUEST_METHOD'] == 'POST':
        return post(env, start_response, query)

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)



