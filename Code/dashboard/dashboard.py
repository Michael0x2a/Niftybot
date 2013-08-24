#!/usr/bin/env python
'''
# dashboard.py

## Introduction ##

## Confusing bits ##

## Dependencies ##

## Up next ##

After reading this file, move to `errors.py`
'''

import multiprocessing
import json
import traceback
import cStringIO
import time

import flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import SimpleCV as scv

class Dashboard(multiprocessing.Process):
    def __init__(self, name, data, mailbox, image_queue, image_size):
        super(Dashboard, self).__init__(name=name)
        self.data = data
        self.mailbox = mailbox
        self.image_queue = image_queue
        self.image_size = image_size
        
    def setup(self):
        def make_safe(thing):
            return json.loads(json.dumps(thing, default=lambda x: "(HIDDEN)"))
    
        def app_factory():
            app = flask.Flask(self.name)
            
            @app.route('/', methods=['GET'])
            def index():
                return flask.render_template('index.html', name="Dashboard :: Niftybot")

            @app.route('/webcam', methods=['GET'])
            def webcam():
                return flask.render_template('webcam.html', name="Video feed :: Niftybot")

            @app.route('/control', methods=['GET'])
            def control():
                return flask.render_template('control.html', name="Manual Control :: Niftybot")
                
            @app.route('/state', methods=['GET'])
            def status():
                copy = dict(self.data.items())
                return flask.jsonify(make_safe(copy))
                
            @app.route('/state/<name>', methods=['GET', 'PUT'])
            def set_state(name):
                try:
                    if name not in self.data.keys():
                        return flask.jsonify({
                            "success": False, 
                            "reason": "could not find {0}".format(name)
                        })
                    if flask.request.method == 'GET':
                        return flask.jsonify(make_safe({
                            "success": True, 
                            name: self.data[name]}))
                    else:
                        data = flask.request.json['data']
                        for name, value in data:
                            self.mailbox.put_nowait([name, value])
                        return flask.jsonify({"success": True})
                except:
                    error = traceback.format_exc()
                    print error


            @app.route('/camera')
            def camera():
                try:
                    if flask.request.environ.get('wsgi.websocket'):
                        ws = flask.request.environ['wsgi.websocket']
            
                        while True:
                            time.sleep(0.05)
                            if self.image_queue.empty():
                                continue

                            raw = self.image_queue.get()
            
                            # Convert the raw image string into a SimpleCV image object.
                            bmp = scv.cv.CreateImageHeader(self.image_size, scv.cv.IPL_DEPTH_8U, 3)
                            scv.cv.SetData(bmp, raw)
                            scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
                            image = scv.Image(bmp).getPIL()

                            # Send to client in jpg format.
                            data = cStringIO.StringIO()
                            image.save(data, 'JPEG')
                            ws.send(data.getvalue().encode("base64"))
                            data.close()
                except:
                    error = traceback.format_exc()
                    print error
                
            return app
            
        self.app = app_factory()
        
    def run(self):
        self.setup()
    
        # Normally, when the app has no parameters, it runs only on
        # localhost and isn't accessible across the network. By setting
        # the host to '0.0.0.0', the http server will listen for requests
        # from this machine's local ip address.
        #self.app.run(host = '0.0.0.0', debug=True)
        #self.app.run()
        
        #host = '127.0.0.1'
        #port = 5000
        
        #dispatcher = cherrypy.wsgiserver.WSGIPathInfoDispatcher({'/': self.app})
        #self.server = cherrypy.wsgiserver.CherryPyWSGIServer((host, port), dispatcher)
        #self.server.start()
        
        self.server = WSGIServer(('', 5000), self.app, handler_class=WebSocketHandler)
        self.server.serve_forever()
        
    def send_command(self, command, data):
        self.mailbox.put_nowait([command, message])
        
    #def get_image(self):
        
        
def run_independently(name='Dashboard', host='0.0.0.0', debug=True):
    print "WARNING:"
    print "You are currently running the webapp independently."
    print "Any attempts to control the robot will go ignored."
    print ""
    
    dashboard = Dashboard(name, {"test": "value"}, multiprocessing.Queue())
    dashboard.setup()

    server = WSGIServer(('', 5000), dashboard.app, handler_class=WebSocketHandler)
    server.serve_forever()
        
    #dashboard.app.run(host=host, debug=True)


