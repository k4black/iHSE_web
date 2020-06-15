import typing as tp

import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse  # noqa: F401
from utils.http import get_user_by_response, get_json_by_response  # noqa: F401
import utils.config as config
from utils.auxiliary import logger, generate_codes, get_datetime_str
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
        return http.forbiden()

    logger('admin_panel()', f'Admin want to {env["PATH_INFO"]}', type_='LOG')

    functions = {
        '/admin_get_config': get_config,
        '/admin_post_config': post_config,

        '/admin_get_places': get_places,
        '/admin_post_places': post_places,

        '/admin_get_credits': get_credits,
        '/checkin': post_checkin,

        '/admin_get_table': get_table,
        '/admin_clear_table': clear_table,
        '/admin_send_data': send_data,
        '/admin_remove_data': remove_data,

        '/admin_codes': codes,

        '/admin_change_password': change_password
    }

    if env['PATH_INFO'] in functions:
        return functions[env['PATH_INFO']](env, query, cookie)


def post_checkin(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Check in at lecture  HTTP request (by admin)
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

    event = sql.get_in_table(event_id, 'events')

    if event is None:  # No such event
        return http.not_allowed(host=env['HTTP_HOST'])

    config_dict = config.get_config()

    # Set up credits and enrolls attendance
    if event['type'] == 1 and event['total'] > 0:
        # master
        # Check there are enrolls
        enrolls = sql.get_enrolls_by_event_id(event_id)

        users_in_enrolls = {enroll['user_id'] for enroll in enrolls if not enroll['attendance']}  # type: tp.Set[int]
        users_in_checkins = {int(checkin['id']): min(int(checkin['bonus']), config_dict['CREDITS_ADDITIONAL']) for checkin in
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
        credits = [{'user_id': int(checkin['id']),
                    'event_id': event_id,
                    'validator_id': user_obj['id'],
                    'time': get_datetime_str(),
                    'value':
                        config_dict['CREDITS_MASTER'] + min(int(checkin['bonus']), config_dict['CREDITS_ADDITIONAL'])}
                   for checkin in checkins
                   if int(checkin['id']) in users_to_set_credits]  # type: tp.List[sql.TTableObject]
        for credit in credits:
            sql.insert_to_table(credit, 'credits')

        logger('post_checkin()', f'Checkin users {users_in_checkins} to master event {event_id}', type_='LOG')
    else:
        # lecture
        enrolls = [{'class_id': event_id, 'user_id': int(checkin['id']), 'time': get_datetime_str(), 'attendance': True,
                    'bonus': min(int(checkin['bonus']), config_dict['CREDITS_ADDITIONAL'])} for checkin in
                   checkins]  # type: tp.List[sql.TTableObject]
        for enroll in enrolls:
            sql.update_in_table(enroll, 'enrolls')

        credits = [{'user_id': int(checkin['id']),
                    'event_id': event_id,
                    'time': get_datetime_str(),
                    'value': config_dict['CREDITS_LECTURE'] + min(int(checkin['bonus']),
                                                                  config_dict['CREDITS_ADDITIONAL'])}
                   for checkin in checkins]  # type: tp.List[sql.TTableObject]
        for credit in credits:
            sql.insert_to_table(credit, 'credits')

        logger('post_checkin()', f'Checkin user {checkins} to lecture event {event_id}', type_='LOG')

    return http.ok(env['HTTP_HOST'])


def change_password(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        TODO: add description
    """

    data = get_json_by_response(env)

    if 'user_id' not in data or 'pass' not in data:
        return http.bad_request(host=env['HTTP_HOST'])

    logger('change_password()', f'Change password for {data["user_id"]}.', type_='LOG')

    if sql.change_password(data['user_id'], data['pass']):
        return http.ok(host=env['HTTP_HOST'])
    else:
        return http.bad_request(host=env['HTTP_HOST'])


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
