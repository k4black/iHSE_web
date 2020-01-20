import urllib.parse
from http.cookies import SimpleCookie
import json
import time
import sys
import string
from itertools import groupby
from operator import itemgetter

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


    # Manage admin actions
    if env['PATH_INFO'][:6] == '/admin':
        status, headers, data = admin_panel(env, query, cookie)


    elif env['REQUEST_METHOD'] == 'GET':
        status, headers, data = get(env, query, cookie)

    elif env['REQUEST_METHOD'] == 'POST':
        status, headers, data = post(env, query, cookie)

    elif env['REQUEST_METHOD'] == 'OPTIONS':
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
    print(f"Getting user by response sessid raw:{cookie.get('sessid', '')}")
    # sessid = bytes.fromhex(cookie.get('sessid', ''))  # Get session id from cookie
    # print(f'Getting user by response sessid:{sessid}')
    sessid = cookie.get('sessid', '')

    if sessid == '':  # No cookie

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
    print(f'Log: decoding json from {request_body}')
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

    if env['PATH_INFO'] == '/class':
        return get_class(env, query, cookie)

    if env['PATH_INFO'] == '/enrolls':
        return get_enrolls(env, query, cookie)

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
    # user_obj = get_user_by_response(cookie)
    #
    # print("Admin try: ", user_obj)
    #
    # if user_obj[2] is None or user_obj[1] < 1:  # No User or no Permissions
    #     return user_obj
    # TODO: ADMIN!

    print(f'Admin want to {env["PATH_INFO"]}')

    if env['PATH_INFO'] == '/admin_get_table':
        table_name = query['table']
        print(f'Got get_table {table_name}')

        if table_name == 'users':
            data = sql.process_sql(sql.get_users(), 'users')
        elif table_name == 'credits':
            data = sql.process_sql(sql.get_credits(), 'credits')
            print('credits', data)
        elif table_name == 'sessions':
            data = sql.process_sql(sql.get_sessions(), 'sessions')
            print('sessions', data)
        elif table_name == 'codes':
            data = sql.process_sql(sql.get_codes(), 'codes')
        # elif table_name == 'feedback':
        #     data = sql.process_sql(sql.get_feedback(), 'feedback')
        elif table_name == 'projects':
            data = sql.process_sql(sql.get_projects(), 'projects')
        elif table_name == 'events':
            data = sql.process_sql(sql.get_events(), 'events')
        elif table_name == 'classes':
            data = sql.process_sql(sql.get_classes(), 'classes')
        elif table_name == 'enrolls':
            data = sql.process_sql(sql.get_enrolls(), 'enrolls')
        else:
            print(' ========  400 Bad Request by admin  ======== ')
            return ('400 Bad Request',
                    [
                        # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                        # To receive cookie
                        ('Access-Control-Allow-Credentials', 'true')
                     ],
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

    if env['PATH_INFO'] == '/admin_clear_table':
        table_name = query['table']
        print(f'Clearing {table_name}')

        if table_name == 'users':
            sql.clear_users()
        elif table_name == 'credits':
            sql.clear_credits()
        elif table_name == 'sessions':
            sql.clear_sessions()
        elif table_name == 'codes':
            sql.clear_codes()
        # elif table_name == 'feedback':
        #     sql.clear_feedback()
        elif table_name == 'projects':
            sql.clear_projects()
        elif table_name == 'events':
            sql.clear_events()
        elif table_name == 'classes':
            sql.clear_classes()
        elif table_name == 'enrolls':
            sql.clear_enrolls()
        else:
            return ('400 Bad Request',
                    [
                        # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                        # To receive cookie
                        ('Access-Control-Allow-Credentials', 'true')
                     ],
                    [])

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
                [])

    if env['PATH_INFO'] == '/admin_send_data':  # Update or add row to some table
        table_name = query['table']
        # Get json from response
        print('Update row (env) ', env)
        print(f'Update row (raw)  {env["wsgi.input"]} len:{env.get("CONTENT_LENGTH", 0)}')
        obj = get_json_by_response(env)

        if 'id' not in obj.keys() or obj['id'] == '':
            if table_name == 'users':
                data = sql.dict_to_tuple(obj, 'users')
                sql.insert_user(data)

            elif table_name == 'credits':
                data = sql.dict_to_tuple(obj, 'credits')
                sql.insert_credit(data)

            elif table_name == 'sessions':
                data = sql.dict_to_tuple(obj, 'sessions')
                sql.insert_session(data)

            elif table_name == 'codes':
                data = sql.dict_to_tuple(obj, 'codes')
                sql.insert_code(data)

                # elif table_name == 'feedback':
                #     data = sql.dict_to_tuple(obj, 'users')
                #     sql.insert_feedback(data)

            elif table_name == 'projects':
                data = sql.dict_to_tuple(obj, 'projects')
                sql.insert_project(data)

            elif table_name == 'events':
                data = sql.dict_to_tuple(obj, 'events')
                sql.insert_event(data)

            elif table_name == 'classes':
                data = sql.dict_to_tuple(obj, 'classes')
                sql.insert_class(data)

            elif table_name == 'enrolls':
                data = sql.dict_to_tuple(obj, 'enrolls')
                sql.insert_enroll(data)

        else:
            if table_name == 'users':
                data = sql.dict_to_tuple(obj, 'users')
                sql.edit_user(data)

            elif table_name == 'credits':
                data = sql.dict_to_tuple(obj, 'credits')
                sql.edit_credit(data)

            elif table_name == 'sessions':
                data = sql.dict_to_tuple(obj, 'sessions')
                sql.edit_session(data)

            elif table_name == 'codes':
                data = sql.dict_to_tuple(obj, 'codes')
                sql.edit_code(data)

            # elif table_name == 'feedback':
            #     data = sql.dict_to_tuple(obj, 'feedback')
            #     sql.edit_feedback(data)

            elif table_name == 'projects':
                data = sql.dict_to_tuple(obj, 'projects')
                sql.edit_project(data)

            elif table_name == 'events':
                data = sql.dict_to_tuple(obj, 'events')
                sql.edit_event(data)

            elif table_name == 'classes':
                data = sql.dict_to_tuple(obj, 'classes')
                sql.edit_class(data)

            elif table_name == 'enrolls':
                data = sql.dict_to_tuple(obj, 'enrolls')
                sql.edit_enroll(data)

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
                [])

    if env['PATH_INFO'] == '/admin_remove_data':  # Remove some row in some table
        table_name = query['table']
        obj_id = query['id']
        print(f'Remove id:{obj_id} from {table_name}')

        if table_name == 'users':
            sql.remove_user(obj_id)

        if table_name == 'credits':
            sql.remove_credit(obj_id)

        elif table_name == 'sessions':
            sql.remove_session(obj_id)

        elif table_name == 'codes':
            sql.remove_code(obj_id)

        # elif table_name == 'feedback':
        #     sql.remove_feedback(obj_id)

        elif table_name == 'projects':
            sql.remove_project(obj_id)

        elif table_name == 'events':
            sql.remove_event(obj_id)

        elif table_name == 'classes':
            sql.remove_class(obj_id)

        elif table_name == 'enrolls':
            sql.remove_enroll(obj_id)

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
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

    print(f'Got user :{user_obj}')


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

    # # Safety get user_obj
    # user_obj = get_user_by_response(cookie)
    #
    # if user_obj[2] is None:  # No User
    #     return user_obj

    # Names
    data = [{'name': i[3], 'id': i[0]} for i in sql.get_users()]  # TODO: Move in sql.py

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
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

    data = sql.get_credits_by_id(user_obj[0])
    processes_data = sql.process_sql(data, 'credits')

    json_data = json.dumps(processes_data)
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

    event = sql.get_event(query['id'])

    # Json event data
    data = sql.tuple_to_dict(event, 'events')

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


# @cache
def get_class(env, query, cookie):
    """ Class data HTTP request
    Get class description by class id

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)

    Note:
        Cached by TIMEOUT

    Returns:
        data: which will be transmitted
    """

    class_event = sql.get_class(query['id'])

    # Json event data
    data = sql.tuple_to_dict(class_event, 'classes')

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
             ],
            [json_data])


# @cache
def get_enrolls(env, query, cookie):
    """ Enrolls data HTTP request
    Get enrolls list by event id or user id

    Args:
        env: HTTP request environment - dict
        query: url query parameters - dict (may be empty)

    Note:
        Cached by TIMEOUT

    Returns:
        data: which will be transmitted
    """

    enrolls = []
    if 'event_id' in query.keys():
        enrolls = sql.get_enrolls_by_event_id(query['event_id'])
        print('enrolls by event_id ', enrolls)
    elif 'user_id' in query.keys():
        enrolls = sql.get_enrolls_by_event_id(query['user_id'])
        print('enrolls by user_id ', enrolls)


    # Json event data
    data = sql.process_sql(enrolls, 'enrolls')

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', 'http://ihse.tk'),
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
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
                ('Access-Control-Allow-Origin', '*'),
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

    print('get data days for ', day)

    data = sql.get_day(day)

    data = sorted(data, key=itemgetter(6))
    groups = groupby(data, key=itemgetter(6))

    processed_data = [{'time': k, 'events': [sql.tuple_to_dict(x, 'events') for x in v]} for k, v in groups]
    # [{time: 15.12, events: [events_obj]},  ... {}]


    #print('get_day', data)


    json_data = json.dumps(processed_data)  # creating real json here
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
    phone = ''.join(i for i in phone if i.isdigit())

    # Get session obj or None
    res = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'])

    if res is not None:

        # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
        sessid = res[0].hex()
        # sessid = bytes.hex(res[0])
        # sessid = bytes(res[0])
        print(f'login with got:{sessid}')

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
    sessid = cookie.get('sessid', '')

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
    print(phone)
    phone = phone[0] + "7" + phone[2:]
    phone = ''.join(i for i in phone if i.isdigit())

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
