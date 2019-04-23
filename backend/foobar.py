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



    if env['REQUEST_METHOD'] == 'OPTIONS':
        start_response('200 OK',
                     [('Access-Control-Allow-Origin', '*'),
                      ('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS'),
                      ('Access-Control-Allow-Headers', '*'),
                      ('Allow', 'GET, POST, HEAD, OPTIONS') # TODO: Add content application/json
                      ])

        return



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

    if env['PATH_INFO'] == '/account':
        return get_account(env, start_response, query)

    if env['PATH_INFO'] == '/day':
        return get_day(env, start_response, query)

    if env['PATH_INFO'] == '/feedback':
        return get_feedback(env, start_response, query)

    if env['PATH_INFO'] == '/projects':
        return get_projects(env, start_response, query)


    # TODO: Remove or move in admin panel
    if env['PATH_INFO'] == '/save':
        users_list = users()

        gsheets_save_users(users_list)
        return




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


def get_account(env, start_response, query):
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

        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

        return


    sess = session(sessid)

    if sess is None:  # Wrong cookie

        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

        # TODO: Clear cookie

        return

    # Cookie - ok

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


def get_feedback(env, start_response, query):
    """ Account data HTTP request
    Got day num and return day event for feedback

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Returns:
        data: which will be transmited

    """

    day = query['day']

    # Json account data
    data = {}

    tmp = gsheet_get_feedback(day)  # return (title, [event1, event2, event3] ) or None

    # TODO: SQL
    data['title'] = day + ': ' + tmp[0]
    data['events'] = [ {'title': tmp[1][0]},
                       {'title': tmp[1][1]},
                       {'title': tmp[1][2]}
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
def get_projects(env, start_response, query):
    """ Projects HTTP request
    Send list of projects in json format

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Returns:
        data: which will be transmited

    """


    #tmp = gsheets_get_projects(day)  # return (title, [event1, event2, event3] ) or None


    """
    Json format:
        [
            {
                "title": "Some title",
                "type": "TED",
                "subj": "Math",
                "name": "VAsya and Ilya",
                "desc": "Some project description"
            }
        ]
    """

    # TODO: SQL

    # Json projects data
    data = []

    project1 = {
                   "title": "Some title",
                   "type": "TED",
                   "subj": "Math",
                   "name": "VAsya and Ilya",
                   "desc": "Some project description"
               }

    project2 = {
                   "title": "Some title",
                   "type": "TED",
                   "subj": "Math",
                   "name": "VAsya and Ilya",
                   "desc": "Some project description"
               }

    data.append(project1)
    data.append(project2)



    data = gsheets_get_projects(None)



    json_data = json.dumps(data)


#     print(json_data)

    json_data = json_data.encode('utf-8')


    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data))) ])

    return [json_data]


def get_day(env, start_response, query):
    """ Day schedule data HTTP request
    Get day num and return html

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        return day html by req from query string (if none return today)

    Returns:
        html data: day schedule

    """

    # format is "dd.mm"
    day = query['day']

    data = gsheets_get_day(day)  # getting pseudo-json here
    json_data = json.dumps(data)  # creating real json here
    json_data = json_data.encode('utf-8')

    start_response('200 OK', [
                                  ('Access-Control-Allow-Origin', '*'),
                                  ('Content-type', 'text/plant'),
                                  ('Content-Length', str(len(json_data)))
                             ])

    return [json_data]


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

    if env['PATH_INFO'] == '/login':
        return post_login(env, start_response, query['name'], query['pass'])

    if env['PATH_INFO'] == '/register':
        return post_register(env, start_response, query['name'], query['phone'], query['pass'], query['code'])

    if env['PATH_INFO'] == '/feedback':
        return post_feedback(env, start_response, query)

    if env['PATH_INFO'] == '/project':
        return post_project(env, start_response, query)


def post_login(env, start_response, name, passw):
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


def post_register(env, start_response, name, phone, passw, code):
    """ Register HTTP request
    Create new user if it does not exist and login user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        name: User name - string
        phone: User phone - string
        passw: Password hash - int
        code: special code responsible for the user type and permission to register - string

    Note:
        Send:
            200 Ok: if user exist and session created correnctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:

    """

    print("Registration code: ", code)

    user_type = gsheets_check_code(code)

    print("Registration user type: ", user_type)

    if user_type is not None:
        register(name, passw, user_type, phone, 0)


        print("Registration user name: ", name)

        post_login(env, start_response, name, passw)

    else:
        start_response('403 Forbidden',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ])

    return


def post_feedback(env, start_response, query):
    """ Login HTTP request
    By cookie create feedback for day

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
         None; Only http answer

    """

    day = query['day']

    # Json feedback data

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)
    request_body = request_body.decode("utf-8")

#     print(request_body)

    parced = json.loads(request_body)


    print("Feedback data: ", parced)



    # Parce cookie
    rawdata = env.get('HTTP_COOKIE', '')
    cookie = SimpleCookie()
    cookie.load(rawdata)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    # Get session id or ''
    sessid = bytes.fromhex( cookies.get('sessid', '') )

    sess_obj = session(sessid)

    # If no session
    if False and sess_obj is None:
        start_response('401 Unauthorized',
                           [('Access-Control-Allow-Origin', '*'),
                            ])
        return

    print("Feedback by sess: ", sess_obj)

    user_obj = user(sess_obj[1])

    # If no such user (wrong cookie)
    if False and user_obj is None:

        start_response('401 Unauthorized',
                               [('Access-Control-Allow-Origin', '*'),
                                ])
        return


    print("Feedback by user: ", user_obj)



    if True:   # TODO: If writing ok
        gsheets_save_feedback(user_obj, day, parced)

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


def post_project(env, start_response, query):
    """ Post project HTTP request
    Create new project signed by cookie

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
         None; Only http answer

    """

    print('project')

    # Json project data

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)
    request_body = request_body.decode("utf-8")

#     print(request_body)

    parced = json.loads(request_body)


    print(parced)



    # Parce cookie
    rawdata = env.get('HTTP_COOKIE', '')
    cookie = SimpleCookie()
    cookie.load(rawdata)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    # Get session id or ''
    sessid = bytes.fromhex( cookies.get('sessid', '') )

    sess_obj = session(sessid)

    # If no session
    if False and sess_obj is None:
        start_response('401 Unauthorized',
                           [('Access-Control-Allow-Origin', '*'),
                            ])
        return

    print("Project by sess: ", sess_obj)

    user_obj = user(sess_obj[1])

    # If no such user (wrong cookie)
    if False and user_obj is None:

        start_response('401 Unauthorized',
                               [('Access-Control-Allow-Origin', '*'),
                                ])
        return


    print("Project by user: ", user_obj)



    if user_obj is not None:   # If user exist
        gsheets_save_project(user_obj, parced)

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


""" ---===---==========================================---===--- """
"""                    SQLite database creation                  """
""" ---===---==========================================---===--- """

# TODO: SQL inj


# TODO: place this in sql-specific functions?
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


# Feedback: voite or not
cursor.execute("""CREATE TABLE IF NOT EXISTS  "feedback" (
                    "user_id"	INTEGER NOT NULL PRIMARY KEY,
                    "days"	TEXT,
                    "time"	TEXT DEFAULT(datetime('now','localtime')),
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)


""" ---===---==========================================---===--- """
"""           SQLite database interaction via sqlite3            """
""" ---===---==========================================---===--- """


def seftySql(sql):
    """ Try to run sql code event if db is bisy

    Args:
        sql: sql - string

    Returns:
        None

    """

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


def users():
    # TODO Remove or comment
    cursor.execute("SELECT * FROM users")
    users_list = cursor.fetchall()
    return users_list


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


def gsheets_get_day(day: str) -> list:
    """ Gets timetable from Google Sheets
        and returns it in pseudo-json format

        Args:
            day: calendar day, has to be same as sheet in GSheets - string

        Returns:
            timetable: timetable of the corresponding day in pseudo-json - list
    """
    # TODO waiting for Serova to get real day, not template
    # If modifying these scopes, delete the file token.pickle.
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    day = 'Template'
    # The ID and range of a sample spreadsheet.
    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    spreadsheet_range = day + '!A1:J32'

    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)

    # Call the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    request = sheet.values().get(spreadsheetId=spreadsheet_id,
                                 range=spreadsheet_range)
    result = request.execute()
    values = result.get('values', [])

    # function for removing crlf from human-generated timetable
    def crlf(x):
        y = x.replace('\n', ' - ')
        return y

    # removing \n
    for index, line in enumerate(values[2::], start=2):
        values[index] = list(map(lambda x: crlf(x), line))
    timetable = []  # resulting timetable
    mask = []  # selector for correct selection of GSheets verbose data
    titleplus = 0  # selector for correct differentiation of desc, loc, name
    for line in values[2::]:
        if line[0] != '':
            timetable.append({})
            timetable[-1]['time'] = line[0]
            timetable[-1]['events'] = []
            mask.clear()
            titleplus = 0
            for index, cell in enumerate(line[1::], start=1):
                if cell != '' and cell != '.':
                    mask.append(index)
                    timetable[-1]['events'].append({'title': cell})
        else:
            if titleplus == 0:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['desc'] = line[index]
            elif titleplus == 1:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['host'] = line[index]
            elif titleplus == 2:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['loc'] = line[index]
            titleplus += 1

    return timetable


def gsheets_save_feedback(user_obj, day, feedback_data):
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table name, phone and team

    Args:
        user_obj: User object - (id, type, phone, name, pass, team)
        day: num of the day - string '16.04'
        feedback_data: Python obj of feedback - dictionary
                  {"overall": int,
                   "user1": string,
                   "user2": string,
                   "user3": string,
                   "event1": int,
                   "event2": int,
                   "event3": int,
                   "event1_text": string,
                   "event2_text": string,
                   "event3_text": string
                   }

    Returns:
        state: Sucsess or not - bool

    """

    # TODO: remove after registration is complete
    if user_obj is None:
        user_obj = (21321, 2, '+7 Error', 'ERROR', 666, 99)

    print('User obj:', user_obj)
    print('Feedback data:', feedback_data)

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Feedback!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]
    print(position)
    write_range = 'Feedback!A' + position + ':H' + str(int(position) + 2)

    # writing actual feedback
    data = {'values': [[user_obj[3], user_obj[2], user_obj[5],
                        feedback_data['overall'], feedback_data['user1'], feedback_data['event1'], feedback_data['event2'], feedback_data['event3']],
                       ['', '', '', '', feedback_data['user2'], feedback_data['event1_text'], feedback_data['event2_text'], feedback_data['event3_text']],
                       ['', '', '', '', feedback_data['user3']]],
            'range': write_range
            }
    body = {
        'valueInputOption': 'RAW',
        'data': data
    }
    write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                body=body)
    write_response = write_request.execute()
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))
    print('writing done')

    # updating next writing position
    update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                            range='Feedback!A1',
                                                            valueInputOption='RAW',
                                                            body={'values': [[int(position) + 3]]})
    update_response = update_request.execute()
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))
    print('updating done')

    return True  # TODO: check GSheetsAPI how to track success


def gsheets_check_code(code):
    """ Check registration code in google sheets
    Get user type according this code

    Args:
        code: special code hash which will be responsible for the user type and permission to register - str


    Returns:
        type: type of user - int or None if registration allowed


    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Codes!A5:C9')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])

    reg_allowed = False
    user_type = -1
    for index, code_line in enumerate(read_values, start=5):
        if code_line[0] == code and code_line[2] == '0':
            user_type = int(code_line[1])
            upd_range = 'Codes!C' + str(index)
            update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                                    range=upd_range,
                                                                    valueInputOption='RAW',
                                                                    body={'values': [[1]]})
            update_response = update_request.execute()
            reg_allowed = True
            break


    if reg_allowed:
        return user_type
    else:
        return None


def gsheet_get_feedback(day):
    """ Get description of day for feedback in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        day: num of the day - string '16.04'

    Returns:
        (title, [event1, event2, event3] )                  (TODO: not now: or None if already done)

    """

    return ('Day of the Russia', ['Event 1', 'Other event', 'And the last one'])


def gsheets_get_projects(filter_obj):
    """ Get description of day for feedback in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        filter_obj: filter what we should return - (Name, type, name)   # TODO: Not now

    Returns:
        List of projects obj:
              [ {
                 "title": string,
                 "name": string,
                 "type": string,
                 "desc": string,
                 "anno": string
                 }, .........  ]

             (TODO: not now: or None if no one)


    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting range to read from
    range_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                        range='Projects!A1')
    range_response = range_request.execute()
    range_values = range_response.get('values', [])
    position = range_values[0][0]
    read_range = 'Projects!A4:E' + chr(ord(position)-1)

    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                        range=read_range)
    read_response = read_request.execute()
    read_values = read_response.get('values', [])

    projects = []
    for project in read_values:
        projects.append({})
        projects[-1]['title'] = project[0]
        projects[-1]['type'] = project[1]
        projects[-1]['name'] = project[2]
        projects[-1]['desc'] = project[3]
        projects[-1]['anno'] = project[4]

    return projects

    # return [ {  "title": "TITLE",
    #             "name": "NAME",
    #             "type": "TYPE",
    #             "desc": "DESC" },
    #             {"title": "Title of the pr",
    #              "name": "Name of user",
    #              "type": "Ted",
    #              "desc": "Some description of the project"
    #              } ]


def gsheets_save_users(users_list):
    """ Save list of registred users in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        users_list: User objects - list [ (id, type, phone, name, pass, team), ....]
    Returns:
        none

    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Users!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]

    write_range = 'Users!A' + position + ':F' + position



    for i in range(len(users_list)):
        position += 1

        data = {'values': [[users_list[i][0], users_list[i][1], users_list[i][2], users_list[i][3], users_list[i][4], users_list[i][5]]],
                'range': write_range
                }
        body = {
            'valueInputOption': 'RAW',
            'data': data
        }
        write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body=body)
        write_response = write_request.execute()
        # print('{0} cells updated.'.format(write_response.get('updatedCells')))

    print('Users saved')


def gsheets_save_project(user_obj, project_data):
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        user_obj: User object - (id, type, phone, name, pass, team)
        project_data: Python obj of project - dictionary
                  {"title": string,
                   "name": string,
                   "type": string,
                   "desc": string,
                   "anno": string
                   }

    Returns:
        state: Sucsess or not - bool

    """

    print('User obj:', user_obj)
    print('Project data:', project_data)

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Projects!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]
    print(position)
    write_range = 'Projects!A' + position + ':E' + position

    # writing actual feedback
    data = {'values': [[project_data['title'], project_data['type'], project_data['name'], project_data['desc'], project_data['anno']]],
            'range': write_range
            }
    body = {
        'valueInputOption': 'RAW',
        'data': data
    }
    write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                body=body)
    write_response = write_request.execute()
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))
    print('writing done')

    # updating next writing position
    update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                            range='Projects!A1',
                                                            valueInputOption='RAW',
                                                            body={'values': [[int(position) + 1]]})
    update_response = update_request.execute()
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))
    print('updating done')

    return True  # TODO: check GSheetsAPI how to track success


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
