import typing as tp

import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse  # noqa: F401
from utils.http import get_user_by_response, get_json_by_response  # noqa: F401
import utils.config as config
from utils.auxiliary import logger, generate_codes
from utils import sql


def admin(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
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

    logger('admin_panel()', 'Admin try with cookie {cookie}', type_='LOG')

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return http.wrong_cookie(host=env['HTTP_HOST'])

    logger('admin_panel()', f'Admin try with user: {user_obj}', type_='LOG')

    if user_obj['user_type'] == 0:
        return http.unauthorized()

    logger('admin_panel()', f'Admin want to {env["PATH_INFO"]}', type_='LOG')

    functions = {
        '/admin_get_config': get_config,
        '/admin_post_config': post_config,

        '/admin_get_places': get_places,
        '/admin_post_places': post_places,

        '/admin_get_credits': get_credits,

        '/admin_get_table': get_table,
        '/admin_clear_table': clear_table,
        '/admin_send_data': send_data,
        '/admin_remove_data': remove_data,

        '/admin_codes': codes
    }

    if env['PATH_INFO'] in functions:
        return functions[env['PATH_INFO']](env, query, cookie)


def get_credits(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    data = sql.get_credits_short()
    # Send req data tables
    return http.ok(host=env['HTTP_HOST'], json_dict=data)


def get_table(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    table_name = query['table']

    if table_name in sql.table_fields.keys():
        data = sql.get_table(table_name)
    else:
        logger('admin_panel()', '400 Bad Request by admin', type_='ERROR')
        return http.bad_request(host=env['HTTP_HOST'])

    # Send req data tables
    return http.ok(host=env['HTTP_HOST'], json_dict=data)


def clear_table(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    table_name = query['table']

    if table_name in sql.table_fields.keys():
        sql.clear_table(table_name)
    else:
        logger('admin_panel()', '400 Bad Request by admin', type_='ERROR')
        return http.bad_request(host=env['HTTP_HOST'])

    return http.ok(host=env['HTTP_HOST'])


def send_data(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """
    table_name = query['table']
    # Get json from response
    obj = get_json_by_response(env)

    if table_name in sql.table_fields.keys():
        if 'id' not in obj.keys() or obj['id'] == '':
            sql.insert_to_table(obj, table_name)
        else:
            sql.update_in_table(obj, table_name)

        if table_name == 'events':
            config.add_place(obj['place'])

    return http.ok(host=env['HTTP_HOST'])


def remove_data(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    table_name = query['table']
    obj_id = query['id']

    if table_name in sql.table_fields.keys():
        sql.remove_in_table(obj_id, table_name)

    return http.ok(host=env['HTTP_HOST'])


def codes(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    codes = generate_codes(20)

    for code in codes:
        data = {'code': code, 'type': 0, 'used': False}
        sql.insert_to_table(data, 'codes')

    return http.ok(host=env['HTTP_HOST'])


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

    Returns:
        Response - result of request
        None
    """

    config_raw = get_json_by_response(env)

    config_dict = {}  # type: tp.Dict[str, tp.Any]
    config_dict['CREDITS_TOTAL'] = config_raw['total']
    config_dict['CREDITS_MASTER'] = config_raw['master']
    config_dict['CREDITS_LECTURE'] = config_raw['lecture']
    config_dict['CREDITS_ADDITIONAL'] = config_raw['additional']
    config_dict['NUMBER_TEAMS'] = config_raw['groups']

    config.set_config(config_dict)

    return http.ok(host=env['HTTP_HOST'])


def get_config(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Config data HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    conf_dict = config.get_config()

    data = {
        'total': conf_dict['CREDITS_TOTAL'],
        'master': conf_dict['CREDITS_MASTER'],
        'lecture': conf_dict['CREDITS_LECTURE'],
        'additional': conf_dict['CREDITS_ADDITIONAL'],
        'groups': conf_dict['NUMBER_TEAMS']
    }

    return http.ok(host=env['HTTP_HOST'], json_dict=data)


def post_places(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Places HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
        None
    """

    places_raw = get_json_by_response(env)
    config.set_places(places_raw)

    return http.ok(host=env['HTTP_HOST'])


def get_places(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Places HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    places = config.get_places()
    data = places

    return http.ok(host=env['HTTP_HOST'], json_dict=data)
