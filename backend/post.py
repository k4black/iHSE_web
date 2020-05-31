import typing as tp
import random
import json

import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse
from utils.http import get_user_by_response, get_json_by_response
from utils.auxiliary import logger, get_datetime_str, check_enroll_time
from utils.config import CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS
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

    team = random.randint(1, NUMBER_TEAMS)  # TODO: Sex distribution

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
        return http.wrong_cookie(env['HTTP_HOST'])

    if user_obj['user_type'] == 0:
        return http.not_allowed(host=env['HTTP_HOST'])

    event = sql.get_in_table(event_id, 'events')

    if event is None:  # No such event
        return http.not_allowed(host=env['HTTP_HOST'])

    # print('Checkin class. event', event)

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

        logger('post_checkin()', f'Checkin users {users_in_checkins} to master event {event_id}', type_='LOG')
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

        logger('post_checkin()', f'Checkin user {checkins} to lecture event {event_id}', type_='LOG')

    return http.ok(env['HTTP_HOST'])


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

    if enrolls is not None:

        # TODO: check do better
        for enroll in enrolls:
            sql.update_in_table(enroll, 'enrolls')

            if enroll['attendance'] in (True, 'true'):
                sql.pay_credit(enroll['user_id'], enroll['event_id'],
                               CREDITS_MASTER + min(CREDITS_ADDITIONAL, enroll['bonus']),
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
    if user_obj['name'] not in project_obj['names']:
        project_obj['names'].append(user_obj['name'])

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
    if user_obj['type'] == 0 and user_obj['project_id'] != project_obj['id']:
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

    # project_id = query['project_id']

    # Safety get user_obj
    user_obj = get_user_by_response(cookie)
    if user_obj is None:
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Check current user can edit
    if user_obj['project_id'] == 0:
        return http.conflict()

    sql.deenroll_project(user_obj['id'])

    return http.ok(host=env['HTTP_HOST'])
