


def application(environ, start_response):
    start_response('200 damn', [('Content-Type', 'text/html')])
    return ["Ololo!".encode("utf-8")]
