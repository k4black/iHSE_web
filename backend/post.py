import typing as tp
import random
import requests
import json

import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse  # noqa: F401
from utils.http import get_user_by_response, get_json_by_response  # noqa: F401
from utils.auxiliary import logger, get_datetime_str, check_enroll_time  # noqa: F401
import utils.config as config
from utils import sql


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

    functions = {
        '/login': post_login,
        '/register': post_register,
        '/logout': post_logout,
        '/notification': post_notification,

        '/feedback': post_feedback,

        '/project': post_project,
        '/edit_project': post_edit_project,
        '/deenroll_project': post_deenroll_project,

        '/credits': post_credits,
        '/mark_enrolls': post_mark_enrolls,
        '/create_enroll': post_create_enroll,
        '/remove_enroll': post_remove_enroll,
    }

    if env['PATH_INFO'] in functions:
        return functions[env['PATH_INFO']](env, query, cookie)

    if env['PATH_INFO'] == '/enroll':
        # TODO: Remove on release - admin
        user_obj = get_user_by_response(cookie)
        if user_obj is None:
            return http.wrong_cookie(env['HTTP_HOST'])
        if user_obj['user_type'] == 0:
            return http.unauthorized()

        return post_enroll(env, query, cookie)

    return http.not_allowed()


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
        # print('ERROR, No registration data.')
        logger('post_login()', 'No registration data in req.', type_='ERROR')
        return http.forbidden()
    try:
        remember = reg_data['remember']
    except KeyError:
        remember = True

    # print(phone)
    phone = "+7" + phone[2:]
    phone = ''.join(i for i in phone if i.isdigit())

    # Get session obj or None
    session_id = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'], get_datetime_str())

    if session_id is not None:
        # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
        sessid = session_id.hex()
        # sessid = bytes.hex(res[0])
        # sessid = bytes(res[0])
        # print(f'login with got:{sessid}')

        expires = 'Max-Age=15768000;' if remember else ''

        return ('200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{env['HTTP_HOST']}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Set-Cookie',
                     f"sessid={sessid}; Path=/; Domain={env['HTTP_HOST']}; HttpOnly;{expires}"),
                    # 1/2 year
                    # ('Location', '//ihse.tk/')
                ],
                [])

    else:
        return http.unauthorized()


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
        return http.forbidden()


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
        # print('ERROR, No registration data.')
        logger('post_login()', 'No registration data in req.', type_='ERROR')
        return http.forbidden()

    # print(phone)
    phone = "+7" + phone[2:]
    phone = ''.join(i for i in phone if i.isdigit())

    # Check registration code
    # user_type = gsheets.check_code(code)

    # user = sql.get_user_by_phone(phone)

    team = random.randint(1, config.get_config()['NUMBER_TEAMS'])  # TODO: Sex distribution

    # Create new user
    if sql.register(code, name, surname, phone, sex, passw, team):
        # Auto login of user
        session_id = sql.login(phone, passw, env['HTTP_USER_AGENT'], env['REMOTE_ADDR'], get_datetime_str())

        if session_id is not None:
            # Convert: b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
            sessid = session_id.hex()
            # sessid = bytes.hex(res[0])
            # sessid = bytes(res[0])
            # print(f'login with got:{sessid}')

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
            return http.unauthorized()
    else:
        return http.conflict()


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
        return http.wrong_cookie(env['HTTP_HOST'])

    # Get json from response
    feedback_obj = get_json_by_response(env)
    users = feedback_obj['users']
    events = feedback_obj['events']

    # TODO: check
    if sql.post_feedback(user_obj['id'], events) and sql.post_top(user_obj['id'], date, users):
        return http.ok(env['HTTP_HOST'])

    else:
        return http.not_allowed()


from pyfcm import FCMNotification
push_service = FCMNotification(api_key="AAAAbDg5f5A:APA91bH9Z_jFxSGbhrxD0LC4SXCGKYlMj16Nz5bBIUqTITZkvtZ_2UsS8VqDuCPqXFxJidvbH5BRxSFsiQJMF2mBYbdpjMbwMY3QndOFUe2mjaoCVZGkZWjUp9LXnFXFdt6BfAflTPz6")


def post_notification(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Sing in current user to pushup notifications

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
        None; Only http answer
    """

    # TODO: Save to sql

    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return http.wrong_cookie(env['HTTP_HOST'])

    key_obj = get_json_by_response(env)


    registration_id = key_obj['token']
    message_title = "Uber update"
    message_body = f"Hi {user_obj['name']}, your customized news for today is ready"
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               message_body=message_body)

    print('!!!!!!result!!!!!!!', result)

    return http.ok(env['HTTP_HOST'])


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
    # code = query['code']
    # print('Credits code: ', code)

    event_id = 42  # TODO: Get event id from code

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return http.wrong_cookie(env['HTTP_HOST'])

    event_obj = sql.get_event(event_id)
    if event_obj is not None:
        # gsheets.save_credits(user_obj, event_obj)
        sql.checkin_user(user_obj, event_obj)
        logger('post_credits()', f'Checkin user {user_obj} to {event_obj}', type_='LOG')

        return http.ok(env['HTTP_HOST'])

    else:
        return http.not_allowed()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    enrolls = get_json_by_response(env)
    config_dict = config.get_config()

    if enrolls is not None:

        # TODO: check do better
        for enroll in enrolls:
            sql.update_in_table(enroll, 'enrolls')

            if enroll['attendance'] in (True, 'true'):
                sql.pay_credit(enroll['user_id'], enroll['event_id'],
                               config_dict['CREDITS_MASTER'] + min(config_dict['CREDITS_ADDITIONAL'], enroll['bonus']),
                               get_datetime_str())
                # TODO: CREDITS_MASTER CREDITS_LECTURE check

        return http.ok(host=env['HTTP_HOST'])

    else:
        return http.not_allowed()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    event_id = query['event_id']

    event = sql.get_event_with_date(event_id)

    if event is None:
        return http.not_allowed()

    if not check_enroll_time(event['date'], event['time']):  # Close for 15 min
        return http.gone()

    if sql.enroll_user(event_id, user_obj['id'], event['date'], get_datetime_str()):

        return http.ok(host=env['HTTP_HOST'])

    else:
        return http.not_allowed()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    enroll_id = query['id']
    enroll = sql.get_in_table(enroll_id, 'enrolls')

    if enroll is not None and (
            user_obj['user_type'] == 0 and enroll['user_id'] == user_obj['id'] or user_obj['user_type'] >= 1):
        # Check admin or user remove himself

        event = sql.get_event_with_date(enroll['event_id'])

        if not check_enroll_time(event['date'], event['time']):  # Close for 15 min
            return http.gone()

        sql.remove_enroll(enroll_id)

        return http.ok(host=env['HTTP_HOST'])

    else:
        return http.not_allowed()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # TODO:

    if sql.enroll_user(event_id, user_obj, get_datetime_str()):
        event = sql.get_event(event_id)

        # Json event data
        data = {'count': event[4], 'total': event[5]}  # TODO: Count total
        return http.ok(host=env['HTTP_HOST'], json_dict=data)

    else:
        return http.not_allowed()  # TODO: Return count and total


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Mb there are some project for current user?
    if user_obj['project_id'] != 0:
        return http.conflict()

    # Check current user in the project
    if user_obj['name'] not in project_obj['users']:
        project_obj['users'].append(user_obj['name'])

    if sql.save_project(project_obj):  # If user exist
        return http.ok(host=env['HTTP_HOST'])
    else:
        return http.conflict()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['user_type'] == 0 and user_obj['project_id'] != project_obj['id']:
        return http.not_allowed()

    sql.update_in_table(project_obj, 'projects')

    return http.ok(host=env['HTTP_HOST'])


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['project_id'] != 0:
        return http.conflict()

    sql.enroll_project(user_obj['id'], project_id)

    return http.ok(host=env['HTTP_HOST'])


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

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['project_id'] == 0:
        return http.conflict()

    sql.deenroll_project(user_obj['id'])

    return http.ok(host=env['HTTP_HOST'])
