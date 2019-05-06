import urllib.parse
from http.cookies import SimpleCookie
import json

# Sqlite import
from backend import sql
# GSheetsAPI imports
from backend import gsheets


# Threading for sync
from threading import Timer

# Timeout of all objects
TIMEOUT = 30  # In seconds TODO: Couple of hours

print('init')


def foo():
    print('sync')

    start_thread()


def start_thread():
    th = Timer(TIMEOUT, foo, [])
    th.setDaemon(True)
    th.start()


start_thread()


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

    # Parse query string
    query = dict(urllib.parse.parse_qsl(env['QUERY_STRING']))


    # Parse cookie
    raw_json = env.get('HTTP_COOKIE', '')
    cookie_obj = SimpleCookie()
    cookie_obj.load(raw_json)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookie = {}
    for key, morsel in cookie_obj.items():
        cookie[key] = morsel.value


    if env['REQUEST_METHOD'] == 'GET':
        return get(env, start_response, query, cookie)

    if env['REQUEST_METHOD'] == 'POST':
        return post(env, start_response, query, cookie)

    if env['REQUEST_METHOD'] == 'OPTIONS':
        start_response('200 OK',
                     [('Access-Control-Allow-Origin', '*'),
                      ('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS'),
                      ('Access-Control-Allow-Headers', '*'),
                      ('Allow', 'GET, POST, HEAD, OPTIONS')  # TODO: Add content application/json
                      ])

        return


""" ---===---==========================================---===--- """
"""          Auxiliary functions for processing requests         """
""" ---===---==========================================---===--- """


def get_user_by_response(start_response, cookie):
    """ Manage get user operation

    Args:
        start_response: HTTP response headers place
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send 401 Unauthorized - if no such user

    Returns:
        user_obj or None if wrong session id

    """

    # Get session id or ''
    sessid = bytes.fromhex(cookie.get('sessid', ''))  # Get session id from cookie

    if sessid == b'':  # No cookie
        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        ])
        return None

    sess = sql.get_session(sessid)  # Get session object

    if sess is None:  # No such session - wrong cookie
        start_response('401 Unauthorized',
                       [    # Because in js there is xhttp.withCredentials = true;
                            ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                            # To receive cookie
                            ('Access-Control-Allow-Credentials', 'true'),
                            # Clear user sessid cookie
                            ('Set-Cookie', 'sessid=none; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                        ])
        return None

    user_obj = sql.get_user(sess[1])  # Get user by user id

    if user_obj is None:  # No such user - wrong cookie or smth wrong
        start_response('401 Unauthorized',
                       [    # Because in js there is xhttp.withCredentials = true;
                            ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                            # To receive cookie
                            ('Access-Control-Allow-Credentials', 'true'),
                            # Clear user sessid cookie
                            ('Set-Cookie', 'sessid=none; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                        ])
        return None

    return user_obj


def get_json_by_response(env):
    """ Get and parse json from request

    Args:
        env: HTTP request environment - dict

    Returns:
        parsed_json or None if wrong json

    """

    # The environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)
    request_body = request_body.decode("utf-8")

    return json.loads(request_body)


""" ---===---==========================================---===--- """
"""                   Main http interaction logic                """
""" ---===---==========================================---===--- """


def get(env, start_response, query, cookie):
    """ GET HTTP request
    Will manage and call specific function [account, registration]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict
        cookie: http cookie parameters - dict (may be empty)

    Returns:
        data: which will be transmitted

    """

    if env['PATH_INFO'] == '/account':
        return get_account(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/user':
        return get_user(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/names':
        return get_names(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/day':
        return get_day(env, start_response, query)

    if env['PATH_INFO'] == '/feedback':
        return get_feedback(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/event':
        return get_event(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/projects':
        return get_projects(env, start_response, query)


    # Manage admin actions
    if env['PATH_INFO'][:6] == '/admin':
        return admin_panel(env, start_response, query, cookie)




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
    except ValueError:
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)
    request_body = ("<p>" + request_body.decode("utf-8") + "</p>").encode('utf-8')


    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    ('Content-Length', str(len(message_return) + len(message_env) + len(request_body)))
                    ])

    return [message_return, message_env, request_body]


def admin_panel(env, start_response, query, cookie):
    """ Manage admin HTTP request
    Will check session id and permissions

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        If there is no cookie or it is incorrect -

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None or user_obj[1] < 1:  # No User or no Permissions
        return


    if env['PATH_INFO'] == '/admin_save':

        users_list = sql.get_users()
        gsheets.save_users(users_list)

        start_response('200 OK',
                       [('Access-Control-Allow-Origin', '*')
                        ])
        return []

    if env['PATH_INFO'] == '/admin_load':

        users_list = gsheets.get_users()
        sql.load_users(users_list)

        event_list = gsheets.get_events()
        sql.load_events(event_list)

        start_response('200 OK',
                       [('Access-Control-Allow-Origin', '*')
                        ])
        return []

    if env['PATH_INFO'] == '/admin_update':

        gsheets.update_events()

        start_response('200 OK',
                       [('Access-Control-Allow-Origin', '*')
                        ])
        return []

    if env['PATH_INFO'] == '/admin_codes':

        gsheets.generate_codes(20, 10, 2)

        start_response('200 OK',
                       [('Access-Control-Allow-Origin', '*')
                        ])
        return []


def get_user(env, start_response, query, cookie):
    """ User data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    # Json account data
    data = {}

    data['name'] = user_obj[3]
    data['phone'] = user_obj[2]
    data['type'] = user_obj[1]
    data['group'] = user_obj[5]
    data['calendar'] = True
    data['feedback'] = False
    data['projects'] = True  # TODO: Notifacation

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]


def get_names(env, start_response, query, cookie):
    """ Send names data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    # Names
    data = [ i[3] for i in sql.get_users() ]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]


def get_account(env, start_response, query, cookie):
    """ Account data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    # Json account data
    data = {}

    data['name'] = user_obj[3]
    data['phone'] = user_obj[2]
    data['type'] = user_obj[1]
    data['group'] = user_obj[5]

    data['credits'] = 120  # TODO: User credits
    data['total'] = 300

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]



def get_event(env, start_response, query, cookie):
    """ Event data HTTP request
    Get event description by event id

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    event = gsheets.get_event(query['id'])

    # Json event data
    data = {}

    data['title'] = event[1]
    data['time'] = event[2]
    data['date'] = event[3]
    data['loc'] = event[4]
    data['host'] = event[5]
    data['desc'] = event[6]

    data['count'] = 12   # TODO: Count in sql bd
    data['total'] = event[9]


    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
#                    [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
#                     ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]


def get_feedback(env, start_response, query, cookie):
    """ Account data HTTP request
    Got day num and return day event for feedback

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Returns:
        data: which will be transmitted

    """

    day = query['day']

    tmp = gsheets.get_feedback(day)  # return (title, [event1, event2, event3] ) or None

    # TODO: SQL
    data = {}

    data['title'] = day + ': ' + tmp[0]
    data['events'] = [ {'title': tmp[1][0]},
                       {'title': tmp[1][1]},
                       {'title': tmp[1][2]}
                     ]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', 'http://ihse.tk'),  # Because in js there is xhttp.withCredentials = true;
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]


def get_projects(env, start_response, query):
    """ Projects HTTP request
    Send list of projects in json format

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)

    Returns:
        data: which will be transmitted

    """

    """
    Json format:
        [
            {
                "title": "Some title",
                "type": "TED",
                "subj": "Math",
                "name": "VAsya and Ilya",
                "desc": "Some project description"
            }, 
            ...
        ]
    """

    # TODO: SQL

    # Json projects data
    # data = []
    #
    # project1 = {
    #                "title": "Some title",
    #                "type": "TED",
    #                "subj": "Math",
    #                "name": "VAsya and Ilya",
    #                "desc": "Some project description"
    #            }
    #
    # project2 = {
    #                "title": "Some title",
    #                "type": "TED",
    #                "subj": "Math",
    #                "name": "VAsya and Ilya",
    #                "desc": "Some project description"
    #            }
    #
    # data.append(project1)
    # data.append(project2)

    data = gsheets.get_projects(None)

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                    ])

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

    data = gsheets.get_day(day)  # getting pseudo-json here

    json_data = json.dumps(data)  # creating real json here
    json_data = json_data.encode('utf-8')

    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/plant'),
                    ('Content-Length', str(len(json_data)))
                    ])

    return [json_data]


def post(env, start_response, query, cookie):
    """ POST HTTP request
    Will manage and call specific function [login, register]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Returns:
         None; Only http answer

    """

    if env['PATH_INFO'] == '/login':
        return post_login(env, start_response, query['phone'], query['pass'])

    if env['PATH_INFO'] == '/register':
        return post_register(env, start_response, query['name'], query['phone'], query['pass'], query['code'])

    if env['PATH_INFO'] == '/feedback':
        return post_feedback(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/project':
        return post_project(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/logout':
        return post_logout(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/credits':
        return post_credits(env, start_response, query, cookie)

    if env['PATH_INFO'] == '/enroll':
        return post_enroll(env, start_response, query, cookie)


def post_login(env, start_response, phone, passw):
    """ Login HTTP request
    Create new session if it does not exist and send cookie sessid

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        phone: User phone - string
        passw: Password hash - int

    Note:
        Send:
            200 Ok: if user exist and session created correctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:
         None; Only http answer

    """

    # Get session obj or None
    res = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'])

    # TODO: redirection by '302 Found'
    if res is not None:

        # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
        sessid = res[0].hex()

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),  # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),  # To receive cookie
                        ('Set-Cookie', 'sessid=' + sessid + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=31536000;'),
                        #('Location', 'http://ihse.tk/login.html')
                        ])

    else:
        start_response('401 Unauthorized',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


def post_logout(env, start_response, query, cookie):
    """ Logout HTTP request
    Delete current session and send clear cookie sessid

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if session deleted and cookie with sess id cleared
            401 Unauthorized: if wrong name of pass

    Returns:
         None; Only http answer

    """

    # Get session id or ''
    sessid = bytes.fromhex( cookie.get('sessid', '') )

    if sql.logout(sessid):

        # TODO: redirection by '302 Found'
        # TODO: if sess does not exist
        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),  # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),  # To receive cookie
                        ('Set-Cookie', 'sessid=none' + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                        #('Location', 'http://ihse.tk/login.html')
                        ])
    else:
        start_response('403 Forbidden',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
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

    # Check registration code
    user_type = gsheets.check_code(code)

    if user_type is not None:

        sql.register(name, passw, user_type, phone, 0)  # Create new user

        post_login(env, start_response, name, passw)  # Automatically login user

    else:
        start_response('403 Forbidden',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


def post_feedback(env, start_response, query, cookie):
    """ Login HTTP request
    By cookie create feedback for day

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
         None; Only http answer

    """

    day = query['day']


    # Get json from response
    feedback_obj = get_json_by_response(env)


    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    if gsheets.save_feedback(user_obj, day, feedback_obj):   # TODO: If writing ok

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                        ])

    else:
        start_response('405 Method Not Allowed',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


def post_credits(env, start_response, query, cookie):
    """ Sing in at lecture  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
         None; Only http answer

    """

    # Event code
    code  = query['code']
    print('Credits code: ', code)

    event_id = 42 # TODO: Get event id


    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    event_obj = sql.get_event(event_id)
    if True or event_obj is not None:   # TODO: If writing ok
        gsheets.save_credits(user_obj, event_obj)

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                        ])

    else:
        start_response('405 Method Not Allowed',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

    return


def post_enroll(env, start_response, query, cookie):
    """ Enroll at lecture HTTP request (by student )
    By cookie add user to this event

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or nop places

    Returns:
         None; Only http answer

    """

    # Event code
    event_id  = query['id']


    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    if True or sql.enroll_user(event_id, user_obj):   # TODO: If writing ok
        # TODO: Enroll user

        event = sql.get_event(event_id)

        # Json event data
        data = {}

        data['count'] = event[4]
        data['total'] = event[5]

        json_data = json.dumps(data)  # creating real json here
        json_data = json_data.encode('utf-8')

        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),  # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),  # To receive cookie
                        ('Content-type', 'text/plant'),
                        ('Content-Length', str(len(json_data)))
                        ])

        return [json_data]

    else:
        start_response('405 Method Not Allowed',
                       [('Access-Control-Allow-Origin', '*'),
                        ])

        return


def post_project(env, start_response, query, cookie):
    """ Post project HTTP request
    Create new project signed by cookie

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers place
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
         None; Only http answer

    """

    # Get json from response
    project_obj = get_json_by_response(env)


    # Safety get user_obj
    user_obj = get_user_by_response(start_response, cookie)

    if user_obj is None:
        return


    if gsheets.save_project(user_obj, project_obj):   # If user exist
        # TODO: redirection
        start_response('200 Ok',
                       [('Access-Control-Allow-Origin', 'http://ihse.tk'),    # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Credentials', 'true'),         # To receive cookie
                        #('Location', 'http://ihse.tk/login.html')
                        ])

    else:
        start_response('405 Method Not Allowed',
                       [('Access-Control-Allow-Origin', '*'), ]
                       )

    return




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
