#!/usr/bin/env python
'''
Requirements:

-   flask
-   greenlet
-   gevent (install directly from https://pypi.python.org/pypi/gevent#downloads)
-   gevent-websocket
'''

import base64
import cStringIO

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template

import traceback
import time

import pygame
pygame.init()

import SimpleCV as scv
 
app = Flask(__name__)
 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/api')
def api():
    try:
        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            for i in range(100):
                #message = ws.receive()
                time.sleep(0.1)
                
                ws.send(str(i))
            while True:
                message = ws.receive()
                ws.send(message)
    except Exception:
        error = traceback.format_exc()
        print error
    return
    
cam = scv.Camera(0)

@app.route('/camera')
def camera():
    try:
        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            
            while True:            
                image = cam.getImage().flipHorizontal().getPGSurface()
                data = cStringIO.StringIO()
                pygame.image.save(image, data)
                ws.send(base64.b64encode(data.getvalue()))
                time.sleep(0.5)
    except Exception:
        error = traceback.format_exc()
        print error
    return
 
if __name__ == '__main__':
    http_server = WSGIServer(('',5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    
