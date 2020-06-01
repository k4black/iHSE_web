from itertools import groupby

import utils.http as http
from utils.http import TQuery, TEnvironment, TCookie, TStatus, THeaders, TData, TResponse  # noqa: F401
import utils.config as config
from utils.auxiliary import logger, get_datetime_str, check_enroll_time, get_date_str  # noqa: F401
from utils.http import get_user_by_response, get_json_by_response  # noqa: F401
from utils import sql


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

    functions = {
        '/account': get_account,
        '/user': get_user,
        '/names': get_names,

        '/feedback': get_feedback,

        '/class': get_class,
        '/event': get_event,
        '/enrolls': get_enrolls,

        '/days': get_days,
        '/day': get_day,

        '/projects': get_projects,
        '/project': get_project,

        '/credits': get_credits,
    }

    if env['PATH_INFO'] in functions:
        return functions[env['PATH_INFO']](env, query, cookie)

    return http.not_allowed()


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    if 'id' in query:
        user_obj = sql.get_user_by_id(query['id'])

    # Json account data
    data = user_obj
    del data['pass']

    data['calendar'] = True
    data['feedback'] = False
    data['projects'] = True  # TODO: Notifacation

    data['total'] = config.get_config()['CREDITS_TOTAL']
    data['today'] = get_date_str()  # TODO: remove. Only for debug???

    return http.ok(host=env['HTTP_HOST'], json_dict=data)


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
    return http.ok(json_dict=data)


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    # Json account data
    data = user_obj
    data['total'] = config.get_config()['CREDITS_TOTAL']

    return http.ok(host=env['HTTP_HOST'], json_dict=data)


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    data = sql.get_credits_by_user_id(user_obj['id'])
    return http.ok(host=env['HTTP_HOST'], json_dict=data)


def get_days(env: TEnvironment, query: TQuery, cookie: TCookie) -> TResponse:
    """ Days data HTTP request

    Args:
        env: HTTP request environment
        query: url query parameters
        cookie: http cookie parameters (may be empty)

    Returns:
        Response - result of request
    """

    days = sql.get_table('days')
    days = [obj for obj in days if obj['id'] != 0]

    data = {'days': days, 'today': get_date_str()}

    return http.ok(json_dict=data)


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
    return http.ok(host=env['HTTP_HOST'], json_dict=data)


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

    # Json event data
    return http.ok(json_dict=data)


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
        # print('enrolls by event_id ', data)
    elif 'user_id' in query.keys():
        data = sql.get_enrolls_by_user_id(query['user_id'])
        # print('enrolls by user_id ', data)

    return http.ok(json_dict=data)


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
        return http.wrong_cookie(host=env['HTTP_HOST'])

    feedback_template, feedback_data = sql.get_feedback(user_obj['id'], day)

    data = {'template': feedback_template, 'data': feedback_data}
    return http.ok(json_dict=data)


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

    return http.ok(json_dict=data)


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

    return http.ok(json_dict=data)


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
    try:
        day = query['day']
    except KeyError:
        day = get_date_str()  # Get for today day

    if day not in ['Template', '05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06', '12.06',
                   '13.06', '14.06', '15.06', '16.06', '17.06', '18.06']:
        # print('day overflow, falling back to the last day available')  # TODO: Remove or check in sql
        logger('get_day()', 'day overflow, falling back to the last day available', type_='ERROR')
        day = '05.06'

    # print('get data days for ', day)

    data = sql.get_day(day)

    data = sorted(data, key=lambda x: x['time'])
    groups = groupby(data, key=lambda x: x['time'])

    data = [{'time': time_, 'events': [event for event in group_]} for time_, group_ in groups]

    return http.ok(json_dict=data)
