import typing as tp
import json

from utils import sql


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
"""          Auxiliary functions for processing requests         """
""" ---===---==========================================---===--- """


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
    # print(f"Getting user by response sessid raw:{cookie.get('sessid', '')}")
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
    # print(f'Log: decoding json from {request_body}')
    return json.loads(request_body)


""" ---===---==========================================---===--- """
"""                      Common responses                        """
""" ---===---==========================================---===--- """


def wrong_cookie(host: str):
    return (
        '401 Unauthorized',
        [  # Because in js there is xhttp.withCredentials = true;
            ('Access-Control-Allow-Origin', f"//{host}"),
            # To receive cookie
            ('Access-Control-Allow-Credentials', 'true'),
            # Clear user sessid cookie
            ('Set-Cookie', f"sessid=none; Path=/; Domain={host}; HttpOnly; Max-Age=0;"),
        ],
        []
    )


def conflict():
    return (
        '409 Conflict',
        [('Access-Control-Allow-Origin', '*')],
        []
    )


def not_allowed(host: tp.Optional[str] = None):
    if host:
        return (
            '405 Method Not Allowed',
            [
                ('Access-Control-Allow-Origin', f"//{host}"),
                ('Access-Control-Allow-Credentials', 'true'),
                # ('Allow', '')]  # TODO: Allowed methods
            ],
            []
        )
    else:
        return (
            '405 Method Not Allowed',
            [
                ('Access-Control-Allow-Origin', '*'),
                # ('Allow', '')]  # TODO: Allowed methods
            ],
            []
        )


def bad_request(host: tp.Optional[str] = None):
    if host:
        return (
            '400 Bad Request',
            [
                # Because in js there is xhttp.withCredentials = true;
                ('Access-Control-Allow-Origin', f"//{host}"),
                # To receive cookie
                ('Access-Control-Allow-Credentials', 'true')
            ],
            []
        )
    else:
        return (
            '400 Bad Request',
            [('Access-Control-Allow-Origin', '*')],
            []
        )


def ok(host: tp.Optional[str] = None, json_dict: tp.Optional[tp.Any] = None):
    if host:
        if json_dict:
            json_data = json.dumps(json_dict).encode('utf-8')
            return (
                '200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{host}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true'),
                    # To receive json
                    ('Content-type', 'application/json'),  # TODO: Check text/plant
                    ('Content-Length', str(len(json_data)))
                ],
                [json_data]
            )
        else:
            return (
                '200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', f"//{host}"),
                    # To receive cookie
                    ('Access-Control-Allow-Credentials', 'true')
                ],
                []
            )
    else:
        if json_dict:
            json_data = json.dumps(json_dict).encode('utf-8')
            return (
                '200 OK',
                [
                    # Because in js there is xhttp.withCredentials = true;
                    ('Access-Control-Allow-Origin', '*'),
                    # To receive json
                    ('Content-type', 'application/json'),  # TODO: check
                    ('Content-Length', str(len(json_data)))
                ],
                [json_data]
            )
        else:
            return (
                '200 OK',
                [('Access-Control-Allow-Origin', '*')],
                []
            )


def unauthorized():
    return (
        '401 Unauthorized',
        [('Access-Control-Allow-Origin', '*')],
        []
    )


def forbidden():
    return (
        '403 Forbidden',
        [('Access-Control-Allow-Origin', '*')],
        []
    )


def gone():
    return (
        '410 Gone',
        [('Access-Control-Allow-Origin', '*')],
        []
    )
