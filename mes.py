#!/usr/bin/env python3
import cgi,os
import json
import configparser

config=configparser.ConfigParser(allow_no_value=True)
config.read(os.getenv('FRONTEND_CONFIG'))
form = cgi.FieldStorage()
token = form.getfirst("token", "")
if token not in config['tokens']:
    print('Status: 401 Unauthorized\n')
else:
    text = form.getfirst("text", "")
    msgs = json.loads(text)
    log = config['paths']['log']
    if len(log) > 0:
        with open(log, "a", encoding="utf-8") as f:
            print(token, file=f)
            print(msgs, file=f)
    with open(config['paths']['message_pipe'], "w", encoding="utf-8") as f:
        for t in msgs:
            if len(t)==3 and type(t[0]) is int and type(t[1]) is str and type(t[2]) is str:
                tt = json.dumps(t)
                #FIXME check PIPE_BUF
                f.write(u'\n'.join( (str(len(tt)), tt) ))
            else:
                print("Status: 400 Bad Request\n")
                exit(0)
    print('Status: 200 OK\n')
