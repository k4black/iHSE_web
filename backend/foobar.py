def application(env, start_response):
    message_return = b"<p>Hello from uWSGI!</p>"
    # message_return.append(b"<p>Hello from uWSGI!</p>")
    # message_return.append(b"Second string")
    # message_return.append(b"Another one!")
    # message_return.append(b"Another one!")
    start_response('200 OK',
                   [('Access-Control-Allow-Origin', '*'),
                    ('Content-type', 'text/html'),
                    # ('Content-Length', str(len(message_return)))
                    ])
    # open("/tmp/ot.txt", "w").write(message_return)
    # ret = open("/tmp/ot.txt").read()

    # message_return_2 = b"<p> ttt: " + type(env) + b"</p>"
    s = ""
    for i in env.keys():
        s = s + str(i) + ":" + str(env[i]) + "\n"

    message_return_3 = ("<p>Hi again!" + s + "!</p>")   
    message_return_3 = message_return_3.encode('utf-8')
    
    return [message_return, message_return_3]
