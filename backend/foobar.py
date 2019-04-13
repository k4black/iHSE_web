import urllib.parse
import sqlite3

from http.cookies import SimpleCookie


# TODO: Delete accounts user/user and admin/admin


print('!!!! RUN PYTHON INIT !!!!')

conn = sqlite3.connect("/home/ubuntu/main.sqlite", check_same_thread = False)
conn.execute("PRAGMA journal_mode=WAL")   # https://www.sqlite.org/wal.html
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
                    "id"	BLOB NOT NULL PRIMARY KEY UNIQUE DEFAULT (randomblob(16)),
                    "user_id"	INTEGER,
                    "user_type"	INTEGER,
                    "user_agent"	TEXT,
                    "last_ip"	TEXT,
                    "time"	TEXT,
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)








import time

def seftySql(sql):
    timeout = 10

    for x in range(0, timeout):
        try:
            with conn:
                conn.execute(sql)
                conn.commit()
        except:
            time.sleep(1)
            pass
        finally:
            break
    else:
        with conn:
            conn.execute(sql)
            conn.commit()



# Get session by id, None is no such session
def session(id):
    cursor.execute("SELECT * FROM sessions WHERE id=?", (id))
    sessions = cursor.fetchall()

    if len(sessions) == 0:    # No such session
        return None
    else:
        return sessions[0]


# Get user by id, None is no such user
def user(id):
    cursor.execute("SELECT * FROM user WHERE id=?", (id))
    users = cursor.fetchall()

    if len(users) == 0:    # No such session
        return None
    else:
        return users[0]


# Login form, None if not possible
def login(name, passw, agent, ip, time='0'):
    cursor.execute("SELECT * FROM users WHERE name=? AND pass=?", (name, passw))
    users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None

    user = users[0]
    print('User login: ', user)

    cursor.execute("""INSERT INTO sessions(user_id, user_type, user_agent, last_ip, time)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM sessions WHERE user_id=? AND user_agent=?)""",
                   (user[0], user[1], agent, ip, time, user[0], agent))
    conn.commit()

    print(cursor.lastrowid)

    cursor.execute("SELECT * FROM sessions WHERE user_id=? AND user_agent=?", (user[0], agent))
    # cursor.execute("SELECT * FROM sessions ORDER BY employee_id DESC LIMIT 1", ())
    result = cursor.fetchone()
    
    print('Loggined', result)
    return result


# Register (No verification)
def register(name, passw, type, phone, team):
    print('Register:', name, passw)

    # cursor.execute("INSERT INTO users(user_type, phone, name, pass, team) VALUES(?, ?, ?, ?, ?)", ('USER_TYPE', 'PHONE', 'NAME', 'PASS', 'TEAM'))
    cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
                   (type, phone, name, passw, team, name, passw))
    conn.commit()



register('user', 6445723, 0, '+7 915', 0)
register('Hasd Trra', 23344112, 0, '+7 512', 0)
register('ddds Ddsa', 33232455, 0, '+7 333', 1)
register('aiuy Ddsa', 44542234, 0, '+7 234', 1)
register('AArruyaa Ddsa', 345455, 1, '+7 745', 1)
register('AAaa ryui', 23344234523112, 0, '+7 624', 0)
register('AAruiria', 563563265, 0, '+7 146', 0)


print( login('Name', 22222331, 'Gggg', '0:0:0:0') )
a = login('user', 6445723, 'AgentUserAgent', '0:0:0:0')
print(a[0])
print(a[0].hex() )
print( login('AAaa ryui', 23344234523112, 'Agent', '0:0:0:0') )


import json



def req_account(env, start_response, query):
    #rawdata = 'Cookie: devicePixelRatio=1; ident=exists; __utma=13103r6942.2918; __utmc=13103656942; __utmz=13105942.1.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); mp_3cb27825a6612988r46d00tinct_id%22%3A%201752338%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.pion_created_at%22%3A%20%222015-08-03%22%2C%22platform%22%3A%20%22web%22%2C%%22%3A%20%%22%7D; t_session=BAh7DUkiD3Nlc3NpbWVfZV9uYW1lBjsARkkiH1BhY2lmaWMgVGltZSAoVVMgJiBDYW5hZGEpBjsAVEkiFXNpZ25pbl9wZXJzb25faWQGOwBGaQMSvRpJIhRsYXN0X2xvZ2luX2RhdGUGOwBGVTogQWN0aXZlU3VwcG9ydDo6VGltZVdpdGhab25lWwhJdToJVGltZQ2T3RzAAABA7QY6CXpvbmVJIghVVEMGOwBUSSIfUGFjaWZpZWRfZGFzaGJvYXJkX21lc3NhZ2UGOwBGVA%3D%3D--6ce6ef4bd6bc1a469164b6740e7571c754b31cca'
    rawdata = env.get('HTTP_COOKIE', '')
    cookie = SimpleCookie()
    cookie.load(rawdata)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value


    print(cookies)


    data = {}

    sessid = bytes.fromhex( cookies.get('sessid', '') )



    if sessid == b'':

        data['name'] = 'Guest'
        data['phone'] = ''
        data['type'] = 0
        data['group'] = 0
        json_data = json.dumps(data)

    else:
        sess = session(sessid)

        if sess is None:
            data['name'] = 'Guest No sess'
            data['phone'] = ''
            data['type'] = 0
            data['group'] = 0
            json_data = json.dumps(data)

            # Clear cookie

        else:
            usr = user( sess[1] )  # get user by user id

            data['name'] = usr[3]
            data['phone'] = usr[2]
            data['type'] = usr[1]
            data['group'] = usr[5]
            json_data = json.dumps(data)


    print(json_data)

    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data))) ])

    return [json_data]


# GET requare
def get(env, start_response, query):

    if env['PATH_INFO'] == '/account':
        return req_account(env, start_response, query);



    message_return = b"<p>Hello from uWSGI!</p>"

    s = ""
    for i in env.keys():
        s = s + str(i) + ":" + str(env[i]) + "\n"

    message_env = ("<p>" + s + "</p>")
    message_env = message_env.encode('utf-8')

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)
    request_body = ("<p>" + request_body.decode("utf-8")  + "</p>").encode('utf-8')



    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    ('Content-Length', str(len(message_return) + len(message_env) + len(request_body)))
                    ])
    return [message_return, message_env, request_body]


# Login http request
def req_login(env, start_response, name, passw):

    res = login(name, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'])

    # '302 Found'
    if res is not None:
        print(res, type(res))
        sessid = res[0].hex()
        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),
                        ('Access-Control-Allow-Credentials', 'true'),
                        #('Content-type', 'text/html'),
#                         ('Set-Cookie', 'sessid=' + sessid + '; Domain=ihse.tk; HttpOnly; Max-Age=31536000; Path=/'),
                        ('Set-Cookie', 'sessid=' + sessid + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=31536000;'),
                        #('Set-Cookie', 'theme=light'),
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

# >>> b'\xde\xad\xbe\xef'.hex()
# 'deadbeef'
#
# >>> bytes.fromhex('deadbeef')
# b'\xde\xad\xbe\xef'


# Chech reg sequrity code
def checkRegCode(code):
    return True


# Register http request
def req_register(env, start_response, name, passw, code):

    if checkRegCode(code):
        register(name, passw, 0, '+7', 0)

        req_login(env, start_response, name, passw)

    else:
        start_response('403 Forbidden',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ])

    return


# POST requare
def post(env, start_response, query):

    if env['PATH_INFO'] == '/login':
        return req_login(env, start_response, query['name'], query['pass']);

    if env['PATH_INFO'] == '/register':
        return req_register(env, start_response, query['name'], query['pass'], query['code']);



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

    print(env.get('HTTP_COOKIE', 'NOTHING'))
#     urllib.parse.urlparse('https://someurl.com/with/query_string?a=1&b=2&b=3').query
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




