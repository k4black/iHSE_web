import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse
from utils.http import get_user_by_response, get_json_by_response
from utils.auxiliary import logger, generate_codes
from utils.config import write_config
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
    if user_obj['user_type'] == 0:
        return http.unauthorized()

    logger('admin_panel()', f'Admin try with user: {user_obj}', type_='LOG')
    logger('admin_panel()', f'Admin want to {env["PATH_INFO"]}', type_='LOG')

    if env['PATH_INFO'] == '/admin_get_config':
        return get_config(env, query, cookie)

    if env['PATH_INFO'] == '/admin_post_config':
        return post_config(env, query, cookie)

    if env['PATH_INFO'] == '/admin_get_credits':
        data = sql.get_credits_short()

        # Send req data tables
        return http.ok(host=env['HTTP_HOST'], json_dict=data)

    if env['PATH_INFO'] == '/admin_get_table':
        table_name = query['table']

        if table_name in sql.table_fields.keys():
            data = sql.get_table(table_name)
        else:
            logger('admin_panel()', '400 Bad Request by admin', type_='ERROR')
            return http.bad_request(host=env['HTTP_HOST'])

        # Send req data tables
        return http.ok(host=env['HTTP_HOST'], json_dict=data)

    if env['PATH_INFO'] == '/admin_clear_table':
        table_name = query['table']

        if table_name in sql.table_fields.keys():
            sql.clear_table(table_name)
        else:
            logger('admin_panel()', '400 Bad Request by admin', type_='ERROR')
            return http.bad_request(host=env['HTTP_HOST'])

        return http.ok(host=env['HTTP_HOST'])

    if env['PATH_INFO'] == '/admin_send_data':  # Update or add row to some table
        table_name = query['table']
        # Get json from response
        obj = get_json_by_response(env)

        if 'id' not in obj.keys() or obj['id'] == '':
            if table_name in sql.table_fields.keys():
                sql.insert_to_table(obj, table_name)

        else:
            if table_name in sql.table_fields.keys():
                sql.update_in_table(obj, table_name)

        return http.ok(host=env['HTTP_HOST'])

    if env['PATH_INFO'] == '/admin_remove_data':  # Remove some row in some table
        table_name = query['table']
        obj_id = query['id']

        if table_name in sql.table_fields.keys():
            sql.remove_in_table(obj_id, table_name)

        return http.ok(host=env['HTTP_HOST'])

    if env['PATH_INFO'] == '/admin_codes':
        codes = generate_codes(20)

        for code in codes:
            data = {'code': code, 'type': 0, 'used': False}
            sql.insert_to_table(data, 'codes')

        return http.ok()


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

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    config = get_json_by_response(env)

    CREDITS_TOTAL = config['total']
    CREDITS_MASTER = config['master']
    CREDITS_LECTURE = config['lecture']
    CREDITS_ADDITIONAL = config['additional']
    NUMBER_TEAMS = config['groups']

    write_config()

    # TODO: Cherck rights
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

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    data = {
        'total': CREDITS_TOTAL,
        'master': CREDITS_MASTER,
        'lecture': CREDITS_LECTURE,
        'additional': CREDITS_ADDITIONAL,

        'groups': NUMBER_TEAMS
    }

    return http.ok(host=env['HTTP_HOST'], json_dict=data)
