import urllib.parse
import sqlite3
from http.cookies import SimpleCookie
import time
import json
# 👇👇👇 imports for GSheetsAPI 👇👇👇
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# TODO: Delete accounts user/user and admin/admin


""" ---===---==========================================---===--- """
"""                    uWSGI main input function                 """
""" ---===---==========================================---===--- """


def application(env, start_response):
    """ uWSGI entry point
    Manages HTTP request and calls specific functions for [GET, POST]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place

    Returns:
        data: which will be transmitted
    """

    query = dict(urllib.parse.parse_qsl(env['QUERY_STRING']))

    if env['REQUEST_METHOD'] == 'GET':
        return get(env, start_response, query)

    if env['REQUEST_METHOD'] == 'POST':
        return post(env, start_response, query)


""" ---===---==========================================---===--- """
"""                   Main http interaction logic                """
""" ---===---==========================================---===--- """


def get(env, start_response, query):
    """ GET HTTP request
    Will manage and call specific function [account, registration]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict

    Returns:
        data: which will be transmited

    """
    print('GET')

    if env['PATH_INFO'] == '/account':
        return req_account(env, start_response, query)

    if env['PATH_INFO'] == '/day':
        return req_day(env, start_response, query)

    if env['PATH_INFO'] == '/feedback':
        return req_feedback_day(env, start_response, query)






    # TMP for TESTing
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


def req_account(env, start_response, query):
    """ Account data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        If there is no cookie or it is incorrect - it returns guest profile

    Returns:
        data: which will be transmited

    """

    # Parce cookie
    rawdata = env.get('HTTP_COOKIE', '')
    cookie = SimpleCookie()
    cookie.load(rawdata)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value


#     print(cookies)

    # Json account data
    data = {}

    # Get session id or ''
    sessid = bytes.fromhex( cookies.get('sessid', '') )



    if sessid == b'':  # No cookie

        data['name'] = 'Guest'
        data['phone'] = ''
        data['type'] = 0
        data['group'] = 0
        json_data = json.dumps(data)

    else:
        sess = session(sessid)

        if sess is None:  # Wrong cookie
            data['name'] = 'Guest No sess'
            data['phone'] = ''
            data['type'] = 0
            data['group'] = 0
            json_data = json.dumps(data)

            # TODO: Clear cookie

        else:   # Cookie - ok
            usr = user( sess[1] )  # get user by user id

            data['name'] = usr[3]
            data['phone'] = usr[2]
            data['type'] = usr[1]
            data['group'] = usr[5]
            json_data = json.dumps(data)


#     print(json_data)

    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data))) ])

    return [json_data]


def req_feedback_day(env, start_response, query):
    """ Account data HTTP request
    Got day num and return day event for feedback

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Returns:
        data: which will be transmited

    """

#     print(cookies)

    # Json account data
    data = {}

    # TODO: SQL
    data['title'] = '15.04: Day of the Russia'
    data['events'] = [ {'title': 'Event 1'},
                       {'title': 'Other event'},
                       {'title': 'Some event'}
                     ]

    json_data = json.dumps(data)


#     print(json_data)

    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data))) ])

    return [json_data]


# TODO: Max
def req_day(env, start_response, query):
    """ Day sheudle data HTTP request
    Get day num and return html

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        return day html by req from query string (if none return today)

    Returns:
        html data: day sheudle

    """


    # In format - 11.06
    day = query['day']



    # TODO: If some field (Name, desc, loc) is empty - hide it

    # Event is - Event title, description, location and host name
    event = """<table class="event">
                   <th>{}</th>
                   <tr>
                       <td>Desc:</td>
                       <td>{}</td>
                   </tr>

                   <tr>
                       <td>Loc:</td>
                       <td>{}</td>
                   </tr>

                   <tr>
                       <td>Name:</td>
                       <td>{}</td>
                   </tr>
               </table>""".format("Title", "Some descripton of the event too long", "Location", "Named Dmitry")


    # Time consist of several events  and time label
    time = """<div class="time">
                  <div class="bar"></div>

                  <div class="events">

                      <div>{}</div>

                      {}

                      {}

                      <hr class="border_line">

                  </div>

              </div>""".format("15:00 - 16:15", event, event)

    # Day is several times
    day = """<div class="day">

                 {}

                 {}

             </div>""".format(time, time)


    # TODO: Optimize (NO SPACE)
    html_data = day

    html_data = str(gsheets_get_day())

    html_data = html_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'text/html'),
                    ('Content-Length', str(len(html_data))) ])

    return [html_data]


def post(env, start_response, query):
    """ POST HTTP request
    Will manage and call specific function [login, register]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Returns:
         None; Only http answer

    """
    print('POST')

    if env['PATH_INFO'] == '/login':
        return req_login(env, start_response, query['name'], query['pass'])

    if env['PATH_INFO'] == '/register':
        return req_register(env, start_response, query['name'], query['pass'], query['code'])

    if env['PATH_INFO'] == '/feedback':
        return req_feedback(env, start_response, query)


def req_login(env, start_response, name, passw):
    """ Login HTTP request
    Create new session if it does not exist and send cookie sessid

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if user exist and session created correnctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:
         None; Only http answer

    """

    # Get session obj or None
    res = login(name, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'])

    # TODO: redirection by '302 Found'
    if res is not None:
#         print(res, type(res))

        sessid = res[0].hex()  # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                        ('Set-Cookie', 'sessid=' + sessid + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=31536000;'),
                        #('Location', 'http://ihse.tk/login.html')
                        ])

    else:
        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


def req_register(env, start_response, name, passw, code):
    """ Register HTTP request
    Create new user if it does not exist and login user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        name: User name - string
        passw: Password hash - int
        code: special code hash wich will be responsible for the user type and permission to register - int

    Note:
        Send:
            200 Ok: if user exist and session created correnctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:

    """

    if checkRegCode(code):
        register(name, passw, 0, '+7', 0)

        req_login(env, start_response, name, passw)

    else:
        start_response('403 Forbidden',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ])

    return


def req_feedback(env, start_response, query):
    """ Login HTTP request
    By cookie create feedback for day

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            405 Method Not Allowed: already got it

    Returns:
         None; Only http answer

    """

    print('feedback POST')

    day = query['day']

    print(day)

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    print(request_body_size)

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)

    print(request_body)

    request_body = request_body.decode("utf-8")

    print(request_body)


    if True:

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                        #('Location', 'http://ihse.tk/login.html')
                        ])

    else:
        start_response('405 Method Not Allowed',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


# TODO: Max
def checkRegCode(code):
    """ Check register code

    Args:
        code: special code hash wich will be responsible for the user type and permission to register - int


    Returns:
        flag: registration allowed or not - bool

    """

    return True


""" ---===---==========================================---===--- """
"""                    SQLite database creation                  """
""" ---===---==========================================---===--- """


# TODO: place this in sql-specific functions
conn = sqlite3.connect("/home/ubuntu/bd/main.sqlite", check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")  # https://www.sqlite.org/wal.html
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


""" ---===---==========================================---===--- """
"""           SQLite database interaction via sqlite3            """
""" ---===---==========================================---===--- """


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


def session(id):
    """ Get session obj by id

    Args:
        id: session id from bd

    Returns:
        session obj: (id, user_id, user_type, user_agent, last_ip, time)
                     or None if there is no such session

    """

    cursor.execute("SELECT * FROM sessions WHERE id=?", (id, ) )
    sessions = cursor.fetchall()

    if len(sessions) == 0:    # No such session
        return None
    else:
        return sessions[0]


def user(id):
    """ Get user obj by id

    Args:
        id: user id from bd

    Returns:
        user obj: (id, user_type, phone, name, pass, team)
                     or None if there is no such user

    """

    cursor.execute("SELECT * FROM users WHERE id=?", (id, ))
    users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None
    else:
        return users[0]


def register(name, passw, type, phone, team):
    """ Register new user
    There is no verification - create anywhere

    Args:
        name: User name - string
        passw: Password hash - int
        type: User type - int  [GUEST, USER, ADMIN]
        phone: phone - string
        team: number of group - int

    Note:
        user id is automatically generated

    Returns:
        user id: - int (because it is for internal use only)

    """

#     print('Register:', name, passw)

    # cursor.execute("INSERT INTO users(user_type, phone, name, pass, team) VALUES(?, ?, ?, ?, ?)", ('USER_TYPE', 'PHONE', 'NAME', 'PASS', 'TEAM'))
    # Register new user if there is no user with name and pass
    cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
                   (type, phone, name, passw, team, name, passw))
    conn.commit()


def login(name, passw, agent, ip, time='0'):
    """ Login user
    Create new session if it does not exist and return sess id

    Args:
        name: User name - string
        passw: Password hash - int
        agent: User agent - string
        ip: ip - string
        time: time of session creation

    Note:
        session id is automatically generated

    Returns:
        session id: string of hex
                    b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8

    """

    # Check user with name and pass exist and got it
    cursor.execute("SELECT * FROM users WHERE name=? AND pass=?", (name, passw))
    users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None

    user = users[0]
#     print('User: ', user)


    # Create new session if there is no session with user_id and user_agent
    cursor.execute("""INSERT INTO sessions(user_id, user_type, user_agent, last_ip, time)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM sessions WHERE user_id=? AND user_agent=?)""",
                   (user[0], user[1], agent, ip, time, user[0], agent))
    conn.commit()


    # Get session corresponding to user_id and user_agent
    cursor.execute("SELECT * FROM sessions WHERE user_id=? AND user_agent=?", (user[0], agent))
    result = cursor.fetchone()

#     print('Loggined: ', result)
    return result


""" ---===---==========================================---===--- """
"""           Google Sheets interaction via GSheetsAPI           """
""" ---===---==========================================---===--- """


def gsheets_get_day() -> list:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '18DH6SNfsIlJiFxz50zOxoMIzdL3wS4iH70I_YYOFm2Y'
    SAMPLE_RANGE_NAME = 'Sheet1!A1:C17'

    """
        Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/home/ubuntu/iHSE_web/backend/token.pickle'):
        with open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("credentials present")
            flow = InstalledAppFlow.from_client_secrets_file('/home/ubuntu/iHSE_web/backend/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('/home/ubuntu/iHSE_web/backend/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    return values







""" TEST """
# register('user', 6445723, 0, '+7 915', 0)
# register('Hasd Trra', 23344112, 0, '+7 512', 0)
# register('ddds Ddsa', 33232455, 0, '+7 333', 1)
# register('aiuy Ddsa', 44542234, 0, '+7 234', 1)
# register('AArruyaa Ddsa', 345455, 1, '+7 745', 1)
# register('AAaa ryui', 23344234523112, 0, '+7 624', 0)
# register('AAruiria', 563563265, 0, '+7 146', 0)
#
#
# print( login('Name', 22222331, 'Gggg', '0:0:0:0') )
# a = login('user', 6445723, 'AgentUserAgent', '0:0:0:0')
# print(a[0])
# print(a[0].hex() )
# print( login('AAaa ryui', 23344234523112, 'Agent', '0:0:0:0') )


"""
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
"""
