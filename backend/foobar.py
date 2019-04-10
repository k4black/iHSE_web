import urllib.parse

# GET requare
def get(env, start_response, query):
    message_return = b"<p>Hello from uWSGI!</p>"

    s = ""
    for i in env.keys():
        s = s + str(i) + ":" + str(env[i]) + "\n"

    message_env = ("<p>" + s + "</p>")
    message_env = message_env.encode('utf-8')



    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    # ('Content-Length', str(len(message_return) + len(message_env)))
                    ])
    return [message_return, message_env, ("<p>" + request_body + "</p>").encode('utf-8')]



def login(env, start_response, name, passw):
# '302 Found'
    start_response('200 Ok',
                       [('Access-Control-Allow-Origin', '*'),
                        #('Content-type', 'text/html'),
                        ('Set-Cookie', 'sessid=123; HttpOnly; Path=/'),
                        #('Location', env['HTTP_REFERER']),
                        # ('Content-Length', str(len(message_return) + len(message_env)))
                        ])

    return


# POST requare
def post(env, start_response, query):

    if env['PATH_INFO'] == '/login':
        return login(query['name'], query['pass']);



'''
Resource - iHSE.tk/path/resource?param1=value1&param2=value2


REQUEST_METHOD: GET
PATH_INFO: /path/resource
REQUEST_URI: /path/resource?param1=value1&param2=value2
QUERY_STRING: param1=value1&param2=value2
SERVER_PROTOCOL: HTTP/1.1
SCRIPT_NAME:
SERVER_NAME: ip-172-31-36-110
SERVER_PORT: 50000
REMOTE_ADDR: USER_IP
HTTP_HOST: ihse.tk:50000
HTTP_CONNECTION: keep-alive
HTTP_PRAGMA: no-cache
HTTP_CACHE_CONTROL: no-cache
HTTP_ORIGIN: http: //ihse.tk
HTTP_USER_AGENT: USER_AGENT
HTTP_DNT: 1
HTTP_ACCEPT: */*
HTTP_REFERER: http: //ihse.tk/
HTTP_ACCEPT_ENCODING: gzip, deflate
HTTP_ACCEPT_LANGUAGE: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
wsgi.input: <uwsgi._Input object at 0x7f0ef198c810>
wsgi.file_wrapper: <built-in function uwsgi_sendfile>
wsgi.version: (1, 0)
wsgi.errors: <_io.TextIOWrapper name=2 mode='w' encoding='UTF-8'>
wsgi.run_once: False
wsgi.multithread: True
wsgi.multiprocess: True
wsgi.url_scheme: http
uwsgi.version: b'2.0.15-debian'
uwsgi.core: 1
uwsgi.node: b'ip-172-31-36-110'

'''
def application(env, start_response):

    urllib.parse.urlparse('https://someurl.com/with/query_string?a=1&b=2&b=3').query
        #a=1&b=2&b=3

    #urllib.parse.parse_qs('a=1&b=2&b=3');
        #{'a': ['1'], 'b': ['2','3']}

    #urllib.parse.parse_qsl('a=1&b=2&b=3')
        #[('a', '1'), ('b', '2'), ('b', '3')]

    query = dict( urllib.parse.parse_qsl( env['QUERY_STRING'] ) )
#     query = dict( urllib3.util.parse_url( env['QUERY_STRING'] ) )
        #{'a': '1', 'b': '3'}

    if env['REQUEST_METHOD'] == 'GET':
        return get(env, start_response, query)


    if env['REQUEST_METHOD'] == 'POST':
        return post(env, start_response, query)

    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env['wsgi.input'].read(request_body_size)



