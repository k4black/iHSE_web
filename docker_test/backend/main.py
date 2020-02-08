


def application(environ, start_response):
    start_response('200 damn', [('Content-Type', 'text/html')])
    return [(f"Ololo! YOu want to {environ['PATH_INFO']}").encode("utf-8")]
