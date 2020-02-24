import json
import time
import sys
from itertools import groupby
import typing as tp
import random

# Threading for sync
from threading import Timer
from datetime import datetime, timezone, timedelta

import urllib.parse
from http.cookies import SimpleCookie

import configparser

# Sqlite import
from utils import sql, gsheets

sys.path.append('/home/ubuntu/iHSE_web')

TODAY = datetime.today().strftime('%d.%m')

CONFIG_PATH = '/var/conf/ihse.ini'

# Timeout of updating objects
TIMEOUT = 7200  # In seconds 2h = 2 * 60m * 60s = 7200s : Couple of hours

TIMEZONE_SHIFT = 3  # MST timezone

ENROLL_CLOSE_FOR = 15  # Minutes


def get_datetime_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format yyyy-mm-dd hh:mm:ss
    """

    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%Y-%m-%d %H:%M:%S') + ' MSK'


def get_time_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format hh.mm
    """

    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%H.%M')


def get_date_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format dd.mm
    """

    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%d.%m')


def check_enroll_time(date: str, time_: str, year: str = '2020') -> bool:
    """ Check appropriate time for enroll on event

    Returns:
        bool can enroll or deenroll on the event
    """

    can_enroll = datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))) <= \
                 datetime.strptime(f'{date}.{year} {time_}', '%d.%m.%Y %M.%H') - timedelta(minutes=ENROLL_CLOSE_FOR)

    current_day = get_date_str() == date

    return can_enroll and current_day


def generate_codes(num: int) -> tp.Set[str]:
    """ Generate registration 6-sign codes
    Arguments:
        num:

    Returns:
        time str in format dd.mm
    """

    # random.seed(0)
    symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "0123456789" + "0123456789" + "0123456789"
    symbols = [i for i in symbols]

    codes = set({})  # type: tp.Set[str]
    for i in range(num):
        choose5 = ''.join(random.choices(symbols, k=5))
        control1 = symbols[hash(choose5) % len(symbols)]

        code = choose5 + control1
        codes.add(code)

    return codes


""" ---===---==========================================---===--- """
"""                       uWSGI typing objects                   """
""" ---===---==========================================---===--- """

TQuery = tp.Dict[str, str]
TEnvironment = tp.Dict[str, tp.Any]
TCookie = tp.Dict[str, tp.Any]  # TODO: Specify

TStatus = str
THeaders = tp.List[tp.Tuple[str, str]]
TData = tp.Optional[tp.List[tp.Any]]
TResponse = tp.Tuple[TStatus, THeaders, TData]

""" ---===---==========================================---===--- """
"""                    uWSGI main input function                 """
""" ---===---==========================================---===--- """


def application(env: tp.Dict[str, tp.Any], start_response: tp.Callable[..., None]) -> tp.List[tp.Any]:
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

    # Main methods
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

    # Setup request status and headers
    start_response(status, headers)
    return data


""" ---===---==========================================---===--- """
"""                 Sync functions to update data                """
""" ---===---==========================================---===--- """

cache_dict = {}  # Cache data by REQUEST_URI - save data_body and headers


def update_cache() -> None:
    """ Update cache and sync events, projects and etc

    Note:
        Run every TIMEOUT seconds
    """

    global TODAY

    # Update today
    TODAY = datetime.today().strftime('%d.%m')
    print('Today ', TODAY)
    print('sync time: ' + get_datetime_str())

    return

    # Update gsheets cache
    gsheets.update()

    # Update events
    events = gsheets.get_events()
    sql.load_events(events)

    # Update cache
    cache_dict.clear()

    # SQL sync - wal checkpoint
    sql.checkpoint()


def sync() -> None:
    """ Update cache and sync events, projects and etc

    Note:
        Run every TIMEOUT seconds
    """

    print('============ Sync start ============')
    print('sync_time:', get_datetime_str())
    # update_cache()  # Sync itself
    print('============= Sync end =============')

    start_sync(TIMEOUT)  # Update - to call again


def start_sync(delay: int) -> None:
    """ Start sync() in new thread
    This function will run every TIMEOUT seconds

    Args:
        delay: delay time before start of sync

    See:
        sync()
    """

    th = Timer(delay, sync)  # Run foo() through TIMEOUT seconds
    th.setDaemon(True)  # Can close without trouble
    th.start()


start_sync(0)  # Start sync

""" ---===---==========================================---===--- """
"""                   Config file interactions                   """
""" ---===---==========================================---===--- """

CREDITS_TOTAL = 0
CREDITS_MASTER = 0
CREDITS_LECTURE = 0
CREDITS_ADDITIONAL = 0  # Maximum allowed additional credits
NUMBER_TEAMS = 0


def read_config() -> None:
    """Read and save config file (`config.ini`) """

    print('========= Read config file =========')

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    try:
        CREDITS_TOTAL = config['CREDITS']['total']
        CREDITS_MASTER = config['CREDITS']['masterclass']
        CREDITS_LECTURE = config['CREDITS']['lecture']
        CREDITS_ADDITIONAL = config['CREDITS']['additional']

        NUMBER_TEAMS = config['TEAMS']['number']
    except KeyError:
        print('No config file. Using default values')
        CREDITS_TOTAL = 300
        CREDITS_MASTER = 15
        CREDITS_LECTURE = 15
        CREDITS_ADDITIONAL = 5
        NUMBER_TEAMS = 5

    print('===== End config file reading ======')


def write_config() -> None:
    """Write current configuration to config file (`config.ini`) """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    config = configparser.ConfigParser()

    config['CREDITS'] = {
        'total': CREDITS_TOTAL,
        'masterclass': CREDITS_MASTER,
        'lecture': CREDITS_LECTURE,
        'additional': CREDITS_ADDITIONAL
    }

    config['TEAMS'] = {
        'number': NUMBER_TEAMS
    }

    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)


read_config()

""" ---===---==========================================---===--- """
"""                  Cache function and methods                  """
""" ---===---==========================================---===--- """


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


""" ---===---==========================================---===--- """
"""          Auxiliary functions for processing requests         """
""" ---===---==========================================---===--- """


# TODO: switch to {env['HTTP_HOST']} in Origin
def wrong_cookie(host: str):
    response_wrong_cookie = ('401 Unauthorized',
                             [  # Because in js there is xhttp.withCredentials = true;
                                 ('Access-Control-Allow-Origin', f"//{host}"),
                                 # To receive cookie
                                 ('Access-Control-Allow-Credentials', 'true'),
                                 # Clear user sessid cookie
                                 ('Set-Cookie', f"sessid=none; Path=/; Domain={host}; HttpOnly; Max-Age=0;"),
                             ],
                             [])
    return response_wrong_cookie


def get_user_by_response(cookie: TCookie) -> tp.Optional[sql.TTableObject]:
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
        return None

    sess = sql.get_session(sessid)  # Get session object

    if sess is None:  # No such session - wrong cookie
        return None

    user_obj = sql.get_in_table(sess['user_id'], 'users')  # Get user by user id

    if user_obj is None:  # No such user - wrong cookie or smth wrong
        return None

    return user_obj


def get_json_by_response(env: TEnvironment) -> tp.Optional[tp.Dict[str, tp.Any]]:
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


def get(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ GET HTTP request
    Will manage and call specific function [account, registration]

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    if env['PATH_INFO'] == '/account':
        return get_account(env, query, cookie)

    if env['PATH_INFO'] == '/user':
        return get_user(env, query, cookie)

    if env['PATH_INFO'] == '/names':
        return get_names(env, query, cookie)

    if env['PATH_INFO'] == '/day':
        return get_day(env, query, cookie)

    if env['PATH_INFO'] == '/feedback':
        return get_feedback(env, query, cookie)

    if env['PATH_INFO'] == '/class':
        return get_class(env, query, cookie)

    if env['PATH_INFO'] == '/event':
        return get_event(env, query, cookie)

    if env['PATH_INFO'] == '/enrolls':
        return get_enrolls(env, query, cookie)

    if env['PATH_INFO'] == '/days':  # Get days list
        return get_days(env, query, cookie)

    if env['PATH_INFO'] == '/projects':
        return get_projects(env, query, cookie)

    if env['PATH_INFO'] == '/project':
        return get_project(env, query, cookie)

    if env['PATH_INFO'] == '/credits':
        return get_credits(env, query, cookie)

    return ('405 Method Not Allowed',
            [('Access-Control-Allow-Origin', '*'),
             ('Allow', '')],
            [])  # TODO: Allow


def admin_panel(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Manage admin HTTP request
    Will check session id and permissions

    Note:
        If there is no cookie or it is incorrect - Error

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    print("Admin try: ", cookie)

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])
    if user_obj['user_type'] == 0:
        return ('401 Unauthorized',
                [('Access-Control-Allow-Origin', '*')],
                [])

    print("Admin try with user: ", user_obj)
    # TODO: ADMIN!

    print(f'Admin want to {env["PATH_INFO"]}')

    if env['PATH_INFO'] == '/admin_get_config':
        return get_config(env, query, cookie)

    if env['PATH_INFO'] == '/admin_post_config':
        return post_config(env, query, cookie)

    if env['PATH_INFO'] == '/admin_get_credits':
        data = sql.get_credits_short()

        # Send req data tables
        json_data = json.dumps(data)
        json_data = json_data.encode('utf-8')

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                ],
                [json_data])

    if env['PATH_INFO'] == '/admin_get_table':
        table_name = query['table']
        print(f'Got get_table {table_name}')

        if table_name in sql.table_fields.keys():
            data = sql.get_table(table_name)
        else:
            print(' ========  400 Bad Request by admin  ======== ')
            return ('400 Bad Request',
                    [
                        # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                        # To receive cookie
                        ('Access-Control-Allow-Credentials', 'true')
                    ],
                    [])

        print('Sending data table', data)

        # Send req data tables
        json_data = json.dumps(data)
        json_data = json_data.encode('utf-8')

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Content-type', 'application/json'),
                    ('Content-Length', str(len(json_data)))
                ],
                [json_data])

    if env['PATH_INFO'] == '/admin_clear_table':
        table_name = query['table']
        print(f'Clearing {table_name}')

        if table_name in sql.table_fields.keys():
            sql.clear_table(table_name)
        else:
            return ('400 Bad Request',
                    [
                        # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                        # To receive cookie
                        ('Access-Control-Allow-Credentials', 'true')
                    ],
                    [])

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
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
            if table_name in sql.table_fields.keys():
                sql.insert_to_table(obj, table_name)

        else:
            if table_name in sql.table_fields.keys():
                sql.update_in_table(obj, table_name)

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
                [])

    if env['PATH_INFO'] == '/admin_remove_data':  # Remove some row in some table
        table_name = query['table']
        obj_id = query['id']
        print(f'Remove id:{obj_id} from {table_name}')

        if table_name in sql.table_fields.keys():
            sql.remove_in_table(obj_id, table_name)

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
                [])

    if env['PATH_INFO'] == '/admin_codes':
        codes = generate_codes(20)

        print('===codes===', codes)

        for code in codes:
            data = {'code': code, 'type': 0, 'used': False}
            sql.insert_to_table(data, 'codes')

        return ('200 OK',
                [('Access-Control-Allow-Origin', '*')],
                [])


def get_user(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ User data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    print(f'Got user :{user_obj}')

    # Json account data
    data = user_obj
    del data['pass']

    data['calendar'] = True
    data['feedback'] = False
    data['projects'] = True  # TODO: Notifacation

    data['total'] = CREDITS_TOTAL

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_config(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Config data HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL

    data = {
        'total': CREDITS_TOTAL,
        'master': CREDITS_MASTER,
        'lecture': CREDITS_LECTURE,
        'additional': CREDITS_ADDITIONAL
    }

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_names(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Send names data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = sql.get_names()

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_account(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Account data HTTP request
    Will check session id and return data according to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Json account data
    data = user_obj
    data['total'] = CREDITS_TOTAL

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_credits(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Credits data HTTP request
    Get credits data for chart according to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    data = sql.get_credits_by_user_id(user_obj['id'])

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_days(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Days data HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = sql.get_table('days')

    data = [obj for obj in data if obj['id'] != 0]

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


# @cache
def get_event(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Event data HTTP request
    Get event description by event id

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = sql.get_in_table(query['id'], 'events')

    # Json event data
    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


# @cache
def get_class(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Class data HTTP request
    Get class description by class id

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = sql.get_in_table(query['id'], 'classes')

    print(f"got class: {data}")

    # Json event data
    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


# @cache
def get_enrolls(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Enrolls data HTTP request
    Get enrolls list by event id or user id

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = []
    if 'event_id' in query.keys():
        data = sql.get_enrolls_by_event_id(query['event_id'])
        print('enrolls by event_id ', data)
    elif 'user_id' in query.keys():
        data = sql.get_enrolls_by_user_id(query['user_id'])
        print('enrolls by user_id ', data)

    json_data = json.dumps(data)
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                # ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                ('Access-Control-Allow-Origin', '*'),
                # To receive cookie
                # ('Access-Control-Allow-Credentials', 'true'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def get_feedback(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Account data HTTP request
    Got day num and return day event for feedback
    # TODO: Get data if feedback already exist

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    day = query['date']  # TODO: Check dd.mm of day_id

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    feedback_template, feedback_data = sql.get_feedback(user_obj['id'], day)
    print('feedback_template', feedback_template)
    print('feedback_data', feedback_data)

    data = {'template': feedback_template, 'data': feedback_data}

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
def get_projects(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Projects HTTP request
    Send list of projects in json format

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    data = sql.get_table('projects')
    data = [obj for obj in data if obj['id'] != 0]

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
def get_project(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Get  Project HTTP request by id
    Send project description in json format

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    project_id = query['id']

    data = sql.get_in_table(project_id, 'projects')

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
def get_day(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Day schedule data HTTP request
    Get day num and return html

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Cached by TIMEOUT
        return day html by req from query string (if none return today)

    Returns:
        Response - result of request

        html data: day schedule
    """

    # format is "dd.mm"
    day = query['day']
    if day not in ['Template', '05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06', '12.06',
                   '13.06', '14.06', '15.06', '16.06', '17.06', '18.06']:
        print('day overflow, falling back to the last day available')
        day = '05.06'

    print('get data days for ', day)

    data = sql.get_day(day)

    data = sorted(data, key=lambda x: x['time'])
    groups = groupby(data, key=lambda x: x['time'])

    processed_data = [{'time': time_, 'events': [event for event in group_]} for time_, group_ in groups]

    json_data = json.dumps(processed_data)  # creating real json here
    json_data = json_data.encode('utf-8')

    return ('200 OK',
            [
                ('Access-Control-Allow-Origin', '*'),
                ('Content-type', 'application/json'),
                ('Content-Length', str(len(json_data)))
            ],
            [json_data])


def post(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ POST HTTP request
    Will manage and call specific function [login, register]

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    if env['PATH_INFO'] == '/login':
        return post_login(env, query, cookie)

    if env['PATH_INFO'] == '/register':
        return post_register(env, query, cookie)

    if env['PATH_INFO'] == '/feedback':
        return post_feedback(env, query, cookie)

    if env['PATH_INFO'] == '/project':
        return post_project(env, query, cookie)

    if env['PATH_INFO'] == '/edit_project':
        return post_edit_project(env, query, cookie)

    if env['PATH_INFO'] == '/enroll_project':
        return post_enroll_project(env, query, cookie)

    if env['PATH_INFO'] == '/deenroll_project':
        return post_deenroll_project(env, query, cookie)

    if env['PATH_INFO'] == '/logout':
        return post_logout(env, query, cookie)

    if env['PATH_INFO'] == '/credits':
        return post_credits(env, query, cookie)

    if env['PATH_INFO'] == '/checkin':
        return post_checkin(env, query, cookie)

    if env['PATH_INFO'] == '/mark_enrolls':
        return post_mark_enrolls(env, query, cookie)

    if env['PATH_INFO'] == '/create_enroll':
        return post_create_enroll(env, query, cookie)

    if env['PATH_INFO'] == '/remove_enroll':
        return post_remove_enroll(env, query, cookie)

    if env['PATH_INFO'] == '/enroll':
        # TODO: Remove on release - admin
        user_obj = get_user_by_response(cookie)
        if user_obj is None:
            return wrong_cookie(env['HTTP_HOST'])
        if user_obj['user_type'] == 0:
            return ('401 Unauthorized',
                    [('Access-Control-Allow-Origin', '*')],
                    [])

        return post_enroll(env, query, cookie)

    return ('405 Method Not Allowed',
            [('Access-Control-Allow-Origin', '*'),
             ('Allow', '')],
            [])  # TODO: Allow


def post_config(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Config data HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if user exist and session created correctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:
        Response - result of request
        None
    """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL

    config = get_json_by_response(env)

    CREDITS_TOTAL = config['total']
    CREDITS_MASTER = config['master']
    CREDITS_LECTURE = config['lecture']
    CREDITS_ADDITIONAL = config['additional']

    write_config()

    # Safety get user_obj
    # user_obj = get_user_by_response(cookie)
    #
    # if user_obj[2] is None:  # No User
    #     return user_obj

    if True:  # TODO: Cherck rights

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # ('Location', '//ihse.tk/')
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_login(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Login HTTP request
    Create new session if it does not exist and send cookie sessid

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if user exist and session created correctly
                    and send cookie with sess id
            401 Unauthorized: if wrong name of pass

    Returns:
        Response - result of request
    """

    reg_data = get_json_by_response(env)
    try:
        phone, passw = reg_data['phone'], reg_data['pass']
    except KeyError:
        print('ERROR, No registration data.')
        return ('403 Forbidden',
                [('Access-Control-Allow-Origin', '*')],
                [])

    print(phone)
    phone = "+7" + phone[2:]
    phone = ''.join(i for i in phone if i.isdigit())

    # Get session obj or None
    session_id = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'], get_datetime_str())

    if session_id is not None:
        # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
        sessid = session_id.hex()
        # sessid = bytes.hex(res[0])
        # sessid = bytes(res[0])
        print(f'login with got:{sessid}')

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Set-Cookie',
                     "sessid=" + sessid + f"; Path=/; Domain={env['HTTP_HOST']}; HttpOnly; Max-Age=15768000;"),
                    # 1/2 year
                    # ('Location', '//ihse.tk/')
                ],
                [])

    else:
        return ('401 Unauthorized',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_logout(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Logout HTTP request
    Delete current session and send clear cookie sessid

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if session deleted and cookie with sess id cleared
            401 Unauthorized: if wrong name of pass

    Returns:
        Response - result of request
         None; Only http answer
    """

    # Get session id or ''
    # sessid = bytes.fromhex(cookie.get('sessid', ''))
    sessid = cookie.get('sessid', '')

    if sql.logout(sessid):

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # Clear cookie
                    ('Set-Cookie', 'sessid=none' + f"; Path=/; Domain={env['HTTP_HOST']}; HttpOnly; Max-Age=0;"),
                    # ('Location', '//ihse.tk/login.html')
                ],
                [])
    else:
        return ('403 Forbidden',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_register(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Register HTTP request
    Create new user if it does not exist and login user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Query args:
        env: HTTP request environment
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
        Response - result of request
    """

    reg_data = get_json_by_response(env)
    try:
        name = reg_data['name']
        surname = reg_data['surname']
        phone = reg_data['phone']
        sex = reg_data['sex']
        passw = reg_data['pass']
        code = reg_data['code']
    except KeyError:
        print('ERROR, No registration data.')
        return ('403 Forbidden',
                [('Access-Control-Allow-Origin', '*')],
                [])

    print(phone)
    phone = "+7" + phone[2:]
    phone = ''.join(i for i in phone if i.isdigit())

    # Check registration code
    # user_type = gsheets.check_code(code)

    user = sql.get_user_by_phone(phone)

    team = random.randint(1, NUMBER_TEAMS)  # TODO: Sex distribution
    # Create new user
    success = sql.register(code, name, surname, phone, sex, passw, team)
    if user is not None and success:
        # Auto login of user
        session_id = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'], get_datetime_str())

        if session_id is not None:
            # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
            sessid = session_id.hex()
            # sessid = bytes.hex(res[0])
            # sessid = bytes(res[0])
            print(f'login with got:{sessid}')

            return ('200 OK',
                    [
                        # Because in js there is xhttp.withCredentials = true;
                        ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                        # To receive cookie
                        ('Access-Control-Allow-Credentials', 'true'),
                        ('Set-Cookie',
                         'sessid=' + sessid + f"; Path=/; Domain={env['HTTP_HOST']}; HttpOnly; Max-Age=15768000;"),
                        # 1/2 year
                        # ('Location', '//ihse.tk/')
                    ],
                    [])
    else:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_feedback(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Login HTTP request
    By cookie create feedback for day

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
        Response - result of request
        None; Only http answer
    """

    date = query['date']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Get json from response
    feedback_obj = get_json_by_response(env)
    users = feedback_obj['users']
    events = feedback_obj['events']

    # TODO: check
    if sql.post_feedback(user_obj['id'], events) and sql.post_top(user_obj['id'], date, users):

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # ('Location', '//ihse.tk/')
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_credits(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Sing in at lecture  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
        Response - result of request
        None; Only http answer
    """

    # TODO: CREDITS

    # Event code
    code = query['code']
    print('Credits code: ', code)

    event_id = 42  # TODO: Get event id from code

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    event_obj = sql.get_event(event_id)
    if event_obj is not None:
        gsheets.save_credits(user_obj, event_obj)
        sql.checkin_user(user_obj, event_obj)

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_checkin(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Check in at lecture  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
        Response - result of request
        None; Only http answer
    """

    checkins = get_json_by_response(env)
    event_id = query['event']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    if user_obj['user_type'] == 0:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                 ('Access-Control-Allow-Credentials', 'true')],
                [])

    event = sql.get_in_table(event_id, 'events')

    if event is None:  # No such event
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                 ('Access-Control-Allow-Credentials', 'true')],
                [])

    print('Checkin class. event', event)

    # Set up credits and enrolls attendance
    if event['type'] == 1 and event['total'] > 0:
        # master
        # Check there are enrolls
        enrolls = sql.get_enrolls_by_event_id(event_id)

        users_in_enrolls = {enroll['user_id'] for enroll in enrolls if not enroll['attendance']}  # type: tp.Set[int]
        users_in_checkins = {int(checkin['id']): min(int(checkin['bonus']), CREDITS_ADDITIONAL) for checkin in
                             checkins}  # type: tp.Dict[int, int]

        users_to_set_credits = {k for k in users_in_checkins.keys() if k in users_in_enrolls}  # type: tp.Set[int]

        # Setup attendance for enrolls
        enrolls = [enroll for enroll in enrolls if
                   enroll['user_id'] in users_to_set_credits]  # type: tp.List[sql.TTableObject]
        for i in range(len(enrolls)):
            enrolls[i]['attendance'] = True
            enrolls[i]['bonus'] = users_in_checkins[enrolls[i]['user_id']]

            sql.update_in_table(enrolls[i], 'enrolls')

        # TODO: Minus balls if not attendant
        credits = [{'user_id': int(checkin['id']), 'event_id': event_id, 'time': get_datetime_str(),
                    'value': CREDITS_MASTER + min(int(checkin['bonus']), CREDITS_ADDITIONAL)} for checkin in checkins if
                   int(checkin['id']) in users_to_set_credits]  # type: tp.List[sql.TTableObject]
        for credit in credits:
            sql.insert_to_table(credit, 'credits')

        print('Checkin masterclass. event_id', event_id)
        print('users_in_enrolls', users_in_enrolls)
        print('users_in_checkins', users_in_checkins)
        print('New enrolls: ', enrolls)
        print('New credits: ', credits)
    else:
        # lecture
        enrolls = [{'class_id': event_id, 'user_id': int(checkin['id']), 'time': get_datetime_str(), 'attendance': True,
                    'bonus': min(int(checkin['bonus']), CREDITS_ADDITIONAL)} for checkin in
                   checkins]  # type: tp.List[sql.TTableObject]
        for enroll in enrolls:
            sql.update_in_table(enroll, 'enrolls')

        credits = [{'user_id': int(checkin['id']), 'event_id': event_id,
                    'time': get_datetime_str(),
                    'value': CREDITS_LECTURE + min(int(checkin['bonus']), CREDITS_ADDITIONAL)}
                   for checkin in checkins]  # type: tp.List[sql.TTableObject]
        for credit in credits:
            sql.insert_to_table(credit, 'credits')

        print('Checkin lecture. event_id', event_id)
        print('New enrolls: ', enrolls)
        print('New credits: ', credits)

    return ('200 Ok',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
            ],
            [])


# TODO: think mb rename
def post_mark_enrolls(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Sing in at lecture  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
        Response - result of request
        None; Only http answer
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    enrolls = get_json_by_response(env)

    if enrolls is not None:

        # TODO: check do better
        for enroll in enrolls:
            sql.update_in_table(enroll, 'enrolls')

            if enroll['attendance'] in (True, 'true'):
                sql.pay_credit(enroll['user_id'], enroll['event_id'],
                               CREDITS_MASTER + min(CREDITS_ADDITIONAL, enroll['bonus']),
                               get_datetime_str())
                # TODO: CREDITS_MASTER CREDITS_LECTURE check

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_create_enroll(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Create  HTTP request (by student )
    By cookie add enroll to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
        Response - result of request
        None; Only http answer
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    event_id = query['event_id']

    event = sql.get_event_with_date(event_id)

    if event is None:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if not check_enroll_time(event['date'], event['time']):  # Close for 15 min
        return ('410 Gone',
                [('Access-Control-Allow-Origin', '*')],
                [])

    if sql.enroll_user(event_id, user_obj['id'], get_datetime_str()):

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_remove_enroll(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Remove  HTTP request (by student )
    By cookie add credits to user

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or timeout

    Returns:
        Response - result of request
        None; Only http answer
    """

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    enroll_id = query['id']
    enroll = sql.get_in_table(enroll_id, 'enrolls')

    if enroll is not None and (
            user_obj['user_type'] == 0 and enroll['user_id'] == user_obj['id'] or user_obj['user_type'] >= 1):
        # Check admin or user remove himself

        event = sql.get_event_with_date(enroll['event_id'])

        if not check_enroll_time(event['date'], event['time']):  # Close for 15 min
            return ('410 Gone',
                    [('Access-Control-Allow-Origin', '*')],
                    [])

        sql.remove_enroll(enroll_id)

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                ],
                [])

    else:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_enroll(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Enroll at lecture HTTP request (by student )
    By cookie add user to this event

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it or nop places

    Returns:
        Response - result of request
        None; Only http answer
    """

    # Event code
    event_id = query['id']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # TODO:

    if sql.enroll_user(event_id, user_obj, get_datetime_str()):

        event = sql.get_event(event_id)

        # Json event data
        data = {'count': event[4], 'total': event[5]}  # TODO: Count total

        json_data = json.dumps(data)  # creating real json here
        json_data = json_data.encode('utf-8')

        return ('200 Ok',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
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


def post_project(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Post project HTTP request
    Create new project signed by cookie

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
        Response - result of request
    """

    # Get json from response
    project_obj = get_json_by_response(env)

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Mb there are some project for current user?
    if user_obj['project_id'] != 0:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])

    # Check current user in the project
    if user_obj['name'] not in project_obj['names']:
        project_obj['names'].append(user_obj['name'])

    if sql.save_project(project_obj):  # If user exist
        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # ('Location', '//ihse.tk/projects.html')
                    # ('Location', '//ihse.tk/')
                ],
                [])

    else:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])


def post_edit_project(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Post edit project HTTP request
    Edit project signed by cookie

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
        Response - result of request
    """

    # Get json from response
    project_obj = get_json_by_response(env)

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['type'] == 0 and user_obj['project_id'] != project_obj['id']:
        return ('405 Method Not Allowed',
                [('Access-Control-Allow-Origin', '*')],
                [])

    sql.update_in_table(project_obj, 'projects')

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                # ('Location', '//ihse.tk/projects.html')
                # ('Location', '//ihse.tk/')
            ],
            [])


def post_enroll_project(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Enroll current user to project HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
        Response - result of request
    """

    project_id = query['project_id']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['project_id'] != 0:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])

    sql.enroll_project(user_obj['id'], project_id)

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                # ('Location', '//ihse.tk/projects.html')
                # ('Location', '//ihse.tk/')
            ],
            [])


def post_deenroll_project(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ De Enroll current user to project HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Note:
        Send:
            200 Ok: if all are ok
            401 Unauthorized: if wrong session id
            405 Method Not Allowed: already got it

    Returns:
        Response - result of request
    """

    project_id = query['project_id']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return wrong_cookie(env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['project_id'] == 0:
        return ('409 Conflict',
                [('Access-Control-Allow-Origin', '*')],
                [])

    sql.deenroll_project(user_obj['id'])

    return ('200 OK',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true'),
                # ('Location', '//ihse.tk/projects.html')
                # ('Location', '//ihse.tk/')
            ],
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
