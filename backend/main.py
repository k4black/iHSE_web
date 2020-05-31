import typing as tp
from threading import Timer

import urllib.parse
from http.cookies import SimpleCookie

from utils.auxiliary import logger
from get import get
from post import post
from admin import admin


# Timeout of updating objects
TIMEOUT = 7200  # In seconds 2h = 2 * 60m * 60s = 7200s : Couple of hours


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
        status, headers, data = admin(env, query, cookie)

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

    # Update today
    # print('Today ', TODAY)
    # print('sync time: ' + get_datetime_str())
    logger('update_cache()', 'Update day', type_='LOG')

    return

    # Update gsheets cache
    # gsheets.update()

    # Update events
    # events = gsheets.get_events()
    # sql.load_events(events)

    # Update cache
    # cache_dict.clear()

    # SQL sync - wal checkpoint
    # sql.checkpoint()


def sync() -> None:
    """ Update cache and sync events, projects and etc

    Note:
        Run every TIMEOUT seconds
    """

    # print('============ Sync start ============')
    logger('sync()', '==== Sync start ====', type_='LOG')
    # print('sync_time:', get_datetime_str())
    # update_cache()  # Sync itself
    # print('============= Sync end =============')
    logger('sync()', '==== Sync end ======', type_='LOG')

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
"""                       env dict example                       """
""" ---===---==========================================---===--- """


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
