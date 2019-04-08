def application(env, start_response):
    message_return = "<p>Hello from uWSGI!</p>"
    # message_return.append(b"<p>Hello from uWSGI!</p>")
    # message_return.append(b"Second string")
    # message_return.append(b"Another one!")
    # message_return.append(b"Another one!")
    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    ('Content-Length', str(len(message_return)))])
    # open("/tmp/ot.txt", "w").write(message_return)
    # ret = open("/tmp/ot.txt").read()
    return [message_return]
