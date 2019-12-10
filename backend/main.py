import urllib.parse
from http.cookies import SimpleCookie
import json
import time
import sys
sys.path.append('/home/ubuntu/iHSE_web')


# import backend
# Sqlite import
from backend import sql
# GSheetsAPI imports
from backend import gsheets

# Threading for sync
from threading import Timer

from datetime import datetime

TODAY = datetime.today().strftime('%d.%m')

# Timeout of updating objects (from gsheets)
TIMEOUT = 7200  # In seconds 2h = 2 * 60m * 60s = 7200s TODO: Couple of hours
CREDITS = 300  # Max credits # TODO: Get from table?



""" ---===---==========================================---===--- """
"""                    uWSGI main input function                 """
""" ---===---==========================================---===--- """


def application(env, start_response):
    """ uWSGI entry point
    Manages HTTP request and calls specific functions for [GET, POST]

    Args:
        env: HTTP request environment - dict
        start_response: HTTP response headers function

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


    status = '200 OK'
    headers = []
    data = []


    if env['REQUEST_METHOD'] == 'GET':
        status, headers, data = get(env, query, cookie)

    if env['REQUEST_METHOD'] == 'POST':
        status, headers, data = post(env, query, cookie)

    if env['REQUEST_METHOD'] == 'OPTIONS':
        status = '200 OK'
        headers = [
                       ('Access-Control-Allow-Origin', '*'),
                       ('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS'),
                       ('Access-Control-Allow-Headers', '*'),
                       ('Allow', 'GET, POST, HEAD, OPTIONS')  # TODO: Add content application/json
                   ]


    start_response(status, headers)
    return data


""" ---===---==========================================---===--- """
"""          Auxiliary functions for processing requests         """
""" ---===---==========================================---===--- """


cache_dict = {}  # Cache data by REQUEST_URI - save data_body and headers


def update_cache():
    """ Update cache and sync events, projects and etc

    Note:
        Run every TIMEOUT seconds

    Returns:

    """
    global TODAY

    # Update today
    TODAY = datetime.today().strftime('%d.%m')
    print('Today ', TODAY)

    # Update gsheets cache
    gsheets.update()

    # Update events
    events = gsheets.get_events()
    sql.load_events(events)

    # Update cache
    cache_dict.clear()


    # SQL sync - wal checkpoint
    sql.checkpoint()

    print('sync: ' + str(time.time()))


def sync():
    """ Update cache and sync events, projects and etc

    Note:
        Run every TIMEOUT seconds

    Returns:

    """

    print('sync_start')
    update_cache()  # Sync itself
    print('sync_end')

    start_sync(TIMEOUT)  # Update - to call again


def start_sync(delay):
    """ Start sync() in new thread
    This function will run every TIMEOUT seconds

    Args:
        delay: delay time before start of sync

    See:
        sync()

    Returns:

    """

    th = Timer(delay, sync)  # Run foo() through TIMEOUT seconds
    th.setDaemon(True)  # Can close without trouble
    th.start()


start_sync(0)  # Start sync


def cache(foo):
    """ Decorator for cache some function
    Wil check exist cache version response or not and send it

    Args:
        foo: Function to cache foo(env, query)

    Usage:
        @cache
        foo(env, query):
            pass

    Returns:
        Decorated function foo

    """

    def decorated_foo(env, query):
        """ Decorated function
        Try to get cached data from dict. if no data - create it
        And manage headers
        Run the foo

        Args:
            env: HTTP request environment - dict
            query: url query parameters - dict

        Note:
            foo: Function to cache foo(env, query)

        Returns:
            foo response

        """

        if env['REQUEST_URI'] in cache_dict.keys():  # If no cache data - create it
            cached_status, cached_headers, cached_data = cache_dict[env['REQUEST_URI']]
        else:
            cached_status, cached_headers, cached_data = foo(env, query)
            cache_dict[env['REQUEST_URI']] = (cached_status, cached_headers, cached_data)

        return cached_status, cached_headers, cached_data

    return decorated_foo


def get_user_by_response(cookie):
    """ Manage get user operation

    Args:
        cookie: http cookie parameters - dict (may be empty)

    Note:
        Send 401 Unauthorized - if no such user

    Returns:
        user_obj or None if wrong session id - (id, type, phone, name, pass, team, credits, avatar)

    """

    # Get session id or ''
    sessid = bytes.fromhex(cookie.get('sessid', ''))  # Get session id from cookie

    if sessid == b'':  # No cookie

        return ('401 Unauthorized',
                [('Access-Control-Allow-Origin', '*')],
                None)

    sess = sql.get_session(sessid)  # Get session object

    if sess is None:  # No such session - wrong cookie

        return ('401 Unauthorized',
                [    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # Clear user sessid cookie
                    ('Set-Cookie', 'sessid=none; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                ],
                None)

    user_obj = sql.get_user(sess[1])  # Get user by user id

    if user_obj is None:  # No such user - wrong cookie or smth wrong

        return ('401 Unauthorized',
                [    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # Clear user sessid cookie
                    ('Set-Cookie', 'sessid=none; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                ],
                None)

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


def get(env, query, cookie):
    """ GET HTTP request
    Will manage and call specific function [account, registration]

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict
        cookie: http cookie parameters - dict (may be empty)

    Returns:
        data: which will be transmitted

    """

    if env['PATH_INFO'] == '/account':
        return get_account(env, query, cookie)

    if env['PATH_INFO'] == '/user':
        return get_user(env, query, cookie)

    if env['PATH_INFO'] == '/names':
        return get_names(env, query, cookie)

    if env['PATH_INFO'] == '/day':
        return get_day(env, query)

    if env['PATH_INFO'] == '/feedback':
        return get_feedback(env, query, cookie)

    if env['PATH_INFO'] == '/event':
        # TODO: Remove on release - admin
        user_obj = get_user_by_response(cookie)
        if user_obj[2] is None:  # No User
            return user_obj  # (id, type, phone, name, pass, team, credits, avatar)
        if user_obj[1] == 0:
            return ('401 Unauthorized',
                    [('Access-Control-Allow-Origin', '*')],
                    None)

        return get_event(env, query, cookie)

    if env['PATH_INFO'] == '/projects':
        return get_projects(env, query)

    if env['PATH_INFO'] == '/credits':
        return get_credits(env, query, cookie)


    # Manage gsheets update cache
    if env['PATH_INFO'] == '/gsheets_update_212442':
        print('/gsheets_update_212442')
        update_cache()
        return


    # Manage admin actions
    if env['PATH_INFO'][:6] == '/admin':
        return admin_panel(env, query, cookie)




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


    return ('200 OK',
            [
                ('Access-Control-Allow-Origin', '*'),
                ('Content-type', 'text/html'),
                ('Content-Length', str(len(message_return) + len(message_env) + len(request_body)))
             ],
            [message_return, message_env, request_body])


def admin_panel(env, query, cookie):
    """ Manage admin HTTP request
    Will check session id and permissions

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:
        If there is no cookie or it is incorrect -

    Returns:
        data: which will be transmitted

    """

    print("Admin try: ", cookie)

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    print("Admin try: ", user_obj)

    if user_obj[2] is None or user_obj[1] < 1:  # No User or no Permissions
        return user_obj

    if env['PATH_INFO'] == '/admin_get_table':
        table_name = query['table']
        if table_name == 'users':
            data = []
            for user in sql.get_users():
                data.append({
                    'id': user[0],
                    'type': user[1],
                    'phone': user[2],
                    'name': user[3],
                    'pass': user[4],
                    'team': user[5],
                    'credits': user[6],
                    'avatar': user[7]
                })
        elif table_name == 'sessions':
            data = []
            for sess in sql.get_sessions():
                data.append({
                    'id': sess[0],
                    'user_id': sess[1],
                    'user_type': sess[2],
                    'user_agent': sess[3],
                    'last_ip': sess[4],
                    'time': sess[5],
                })
        # elif table_name == 'feedback':
        #     data = []
        #     for feedback in sql.get_feedback():
        #         data.append({
        #             'user_id': feedback[0],
        #             'days': feedback[1],
        #             'time': feedback[2]
        #         })
        elif table_name == 'events':
            data = []
            for event in sql.get_events():
                data.append({
                    'id': event[0],
                    'type': event[1],
                    'title': event[2],
                    'credits': event[3],
                    'count': event[4],
                    'total': event[5],
                    'date': event[6]
                })
        else:
            return ('400 Bad Request',
                    [('Access-Control-Allow-Origin', '*')],
                    [])

        # Send req data tables
        json_data = json.dumps(data)
        json_data = json_data.encode('utf-8')

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                ],
                [json_data])

    if env['PATH_INFO'] == '/admin_send_data':  # Uddate or add row to some table
        table_name = query['table']
        # Get json from response
        obj = get_json_by_response(env)

        if table_name == 'users':
            data = (obj['id'], obj['type'], obj['phone'], obj['name'], obj['pass'], obj['team'], obj['credits'], obj['avatar'])
            sql.post_user(data)

        elif table_name == 'sessions':
            data = (obj['id'], obj['user_id'], obj['user_type'], obj['user_agent'], obj['last_ip'], obj['time'])
            sql.post_session(data)

        # elif table_name == 'feedback':
        #     data = (ibj['user_id'], obj['days'], obj['time'])
        #     sql.post_feedback(data)

        elif table_name == 'events':
            data = (obj['id'], obj['type'], obj['title'], obj['credits'], obj['count'], obj['total'], obj['date'])
            sql.post_event(data)

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if env['PATH_INFO'] == '/admin_remove_data':  # Remove some row in some table
        table_name = query['table']
        obj_id = query['id']

        if table_name == 'users':
            sql.remove_user(obj_id)

        elif table_name == 'sessions':
            sql.remove_session(obj_id)

        # elif table_name == 'feedback':
        #     sql.remove_feedback(obj_id)

        elif table_name == 'events':
            sql.remove_event(obj_id)

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if env['PATH_INFO'] == '/admin_save':
        users_list = sql.get_users()
        gsheets.save_users(users_list)

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if env['PATH_INFO'] == '/admin_load':
        gsheets.update_cache('Users')
        users_list = gsheets.get_users()
        sql.load_users(users_list)

        event_list = gsheets.get_events()
        sql.load_events(event_list)

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if env['PATH_INFO'] == '/admin_update':

        gsheets.parse_events()

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if env['PATH_INFO'] == '/admin_codes':

        gsheets.generate_codes(150, 25, 5)

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])


def get_user(env, query, cookie):
    """ User data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    # Json account data
    data = {}

    data['name'] = user_obj[3]
    data['phone'] = user_obj[2]
    data['type'] = user_obj[1]
    data['group'] = user_obj[5]

    data['calendar'] = True
    data['feedback'] = False
    data['projects'] = True  # TODO: Notifacation

    data['avatar'] = user_obj[7]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


def get_names(env, query, cookie):
    """ Send names data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    # Names
    data = [ i[3] for i in sql.get_users() ]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


def get_account(env, query, cookie):
    """ Account data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:

    Returns:
        data: which will be transmitted

    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    # Json account data
    data = {}

    data['name'] = user_obj[3]
    data['phone'] = user_obj[2]
    data['type'] = user_obj[1]
    data['group'] = user_obj[5]

    data['credits'] = user_obj[6]
    data['total'] = CREDITS

    data['avatar'] = user_obj[7]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


def get_credits(env, query, cookie):
    """ Credits data HTTP request
    Get credits data for chart according to user

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Note:


    Returns:
        data: which will be transmitted - [int, int, ...]

    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    # Json credits data
    data = gsheets.get_credits(user_obj)

    # print('Credits data ', data)

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


# @cache
def get_event(env, query, cookie):
    """ Event data HTTP request
    Get event description by event id

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)

    Note:
        Cached by TIMEOUT

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

    if len(event) > 10:
        data['anno'] = event[10]

    if len(event) > 8:
        data['count'] = sql.get_event(query['id'])[4]
        data['total'] = event[9]


    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


def get_feedback(env, query, cookie):
    """ Account data HTTP request
    Got day num and return day event for feedback
    # TODO: Get data if feedback already exist

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Returns:
        data: which will be transmitted

    """

    day = query['day']

    tmp = gsheets.get_feedback(day)  # return (title, [event1, event2, event3] ) or None

    data = {}

    data['title'] = day + ': ' + tmp[0]
    data['events'] = [ {'title': tmp[1][0]},
                       {'title': tmp[1][1]},
                       {'title': tmp[1][2]}
                     ]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                ('Access-Control-Allow-Origin', ''),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


@cache
def get_projects(env, query):
    """ Projects HTTP request
    Send list of projects in json format

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)

    Note:
        Cached by TIMEOUT

    Returns:
        projects: List of projects descriptions
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

    data = gsheets.get_projects()

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                ('Access-Control-Allow-Origin', '*'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


# @cache
def get_day(env, query):
    """ Day schedule data HTTP request
    Get day num and return html

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)

    Note:
        Cached by TIMEOUT
        return day html by req from query string (if none return today)

    Returns:
        html data: day schedule

    """

    # format is "dd.mm"
    day = query['day']
    if day not in ['Template', '05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06', '12.06', '13.06', '14.06', '15.06', '16.06', '17.06', '18.06']:
        print('day overflow, falling back to the last day available')
        day = '18.06'

    data = gsheets.get_day(day)  # getting pseudo-json here

    #print('get_day', data)

    json_data = json.dumps(data)  # creating real json here
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                ('Access-Control-Allow-Origin', '*'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


def post(env, query, cookie):
    """ POST HTTP request
    Will manage and call specific function [login, register]

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)
        cookie: http cookie parameters - dict (may be empty)

    Returns:
         None; Only http answer

    """

    if env['PATH_INFO'] == '/login':
        return post_login(env, query['phone'], query['pass'])

    if env['PATH_INFO'] == '/register':
        return post_register(env, query['name'], query['phone'], query['pass'], query['code'])

    if env['PATH_INFO'] == '/feedback':
        return post_feedback(env, query, cookie)

    if env['PATH_INFO'] == '/project':
        return post_project(env, query, cookie)

    if env['PATH_INFO'] == '/logout':
        return post_logout(env, query, cookie)

    if env['PATH_INFO'] == '/credits':
        return post_credits(env, query, cookie)

    if env['PATH_INFO'] == '/enroll':
        # TODO: Remove on release - admin
        user_obj = get_user_by_response(cookie)
        if user_obj[2] is None:  # No User
            return user_obj  # (id, type, phone, name, pass, team, credits, avatar)
        if user_obj[1] == 0:
            return ('401 Unauthorized',
                    [('Access-Control-Allow-Origin', '*')],
                    None)

        return post_enroll(env, query, cookie)


def post_login(env, phone, passw):
    """ Login HTTP request
    Create new session if it does not exist and send cookie sessid

    Args:
        env: HTTP request environment - dict
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

    print(phone)
    phone = phone[0] + "7" + phone[2:]

    # Get session obj or None
    res = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'])

    if res is not None:

        # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
        sessid = res[0].hex()

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Set-Cookie', 'sessid=' + sessid + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=15768000;'),  # 1/2 year
                    # ('Location', 'http://ihse.tk/')
                 ],
                [])

    else:
        return ('401 Unauthorized',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_logout(env, query, cookie):
    """ Logout HTTP request
    Delete current session and send clear cookie sessid

    Args:
        env: HTTP request environment - dict
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

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # Clear cookie
                    ('Set-Cookie', 'sessid=none' + '; Path=/; Domain=ihse.tk; HttpOnly; Max-Age=0;'),
                    # ('Location', 'http://ihse.tk/login.html')
                 ],
                [])
    else:
        return ('403 Forbidden',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_register(env, name, phone, passw, code):
    """ Register HTTP request
    Create new user if it does not exist and login user

    Args:
        env: HTTP request environment - dict
        name: User name - string
        phone: User phone - string
        passw: Password hash - int
        code: special code responsible for the user type and permission to register - string

    Note:
        Send:
            200 Ok: if user exist and session created correctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:

    """
    phone = phone[0] + "7" + phone[2:]

    # Check registration code
    user_type = gsheets.check_code(code)

    user = sql.get_user_by_phone(phone)
    if user is not None:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])


    if user_type is not None:

        sql.register(name, passw, user_type, phone, 0)  # Create new user

        return post_login(env, name, passw)  # Automatically login user

    else:
        return ('403 Forbidden',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_feedback(env, query, cookie):
    """ Login HTTP request
    By cookie create feedback for day

    Args:
        env: HTTP request environment - dict
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
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    if gsheets.save_feedback(user_obj, day, feedback_obj):

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # ('Location', 'http://ihse.tk/')
                 ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_credits(env, query, cookie):
    """ Sing in at lecture  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment - dict
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
    code = query['code']
    print('Credits code: ', code)

    event_id = 42  # TODO: Get event id from code


    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    event_obj = sql.get_event(event_id)
    if event_obj is not None:
        gsheets.save_credits(user_obj, event_obj)
        sql.checkin_user(user_obj, event_obj)

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                 ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_enroll(env, query, cookie):
    """ Enroll at lecture HTTP request (by student )
    By cookie add user to this event

    Args:
        env: HTTP request environment - dict
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
    event_id = query['id']


    # Safety get user_obj
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    if sql.enroll_user(event_id, user_obj):

        event = sql.get_event(event_id)

        # Json event data
        data = {}

        data['count'] = event[4]
        data['total'] = event[5]

        json_data = json.dumps(data)  # creating real json here
        json_data = json_data.encode('utf-8')

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Content-type', 'text/plant'),
                    ('Content-Length', str(len(json_data)))
                 ],
                [json_data])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])  # TODO: Return count and total


def post_project(env, query, cookie):
    """ Post project HTTP request
    Create new project signed by cookie

    Args:
        env: HTTP request environment - dict
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
    user_obj = get_user_by_response(cookie)

    if user_obj[2] is None:  # No User
        return user_obj


    if gsheets.save_project(user_obj, project_obj):   # If user exist

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # ('Location', 'http://ihse.tk/projects.html')
                    # ('Location', 'http://ihse.tk/')
                 ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


# """
# Resource - iHSE.tk/path/resource?param1=value1&param2=value2
#
# REQUEST_METHOD: GET
# PATH_INFO: /path/resource
# REQUEST_URI: /path/resource?param1=value1&param2=value2
# QUERY_STRING: param1=value1&param2=value2
# SERVER_PROTOCOL: HTTP/1.1
# SCRIPT_NAME:
# SERVER_NAME: ip-172-31-36-110
# SERVER_PORT: 50000
# REMOTE_ADDR: USER_IP
# HTTP_HOST: ihse.tk:50000
# HTTP_CONNECTION: keep-alive
# HTTP_PRAGMA: no-cache
# HTTP_CACHE_CONTROL: no-cache
# HTTP_ORIGIN: http: //ihse.tk
# HTTP_USER_AGENT: USER_AGENT
# HTTP_DNT: 1
# HTTP_ACCEPT: */*
# HTTP_REFERER: http: //ihse.tk/
# HTTP_ACCEPT_ENCODING: gzip, deflate
# HTTP_ACCEPT_LANGUAGE: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
# wsgi.input: <uwsgi._Input object at 0x7f0ef198c810>
# wsgi.file_wrapper: <built-in function uwsgi_sendfile>
# wsgi.version: (1, 0)
# wsgi.errors: <_io.TextIOWrapper name=2 mode='w' encoding='UTF-8'>
# wsgi.run_once: False
# wsgi.multithread: True
# wsgi.multiprocess: True
# wsgi.url_scheme: http
# uwsgi.version: b'2.0.15-debian'
# uwsgi.core: 1
# uwsgi.node: b'ip-172-31-36-110'
# """
