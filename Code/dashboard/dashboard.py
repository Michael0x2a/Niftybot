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

import flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

class Dashboard(multiprocessing.Process):
    def __init__(self, name, data, mailbox):
        super(Dashboard, self).__init__(name=name)
        self.data = data
        self.mailbox = mailbox
        
    def setup(self):
        def make_safe(thing):
            return json.loads(json.dumps(thing, default=lambda x: "(HIDDEN)"))
    
        def app_factory():
            app = flask.Flask(self.name)
            
            @app.route('/', methods=['GET'])
            def index():
                return flask.render_template('index.html', name="Dashboard :: Niftybot")
                
            @app.route('/state', methods=['GET'])
            def status():
                copy = dict(self.data.items())
                return flask.jsonify(make_safe(copy))
                
            @app.route('/state/<name>', methods=['GET', 'PUT'])
            def set_state(name):
                if name not in self.data.keys():
                    return flask.jsonify({
                        success: "false", 
                        reason: "could not find {0}".format(name)
                    })
                if flask.request.method == 'GET':
                    return flask.jsonify(make_safe({name: + self.data[name]}))
                else:
                    value = flask.request.form(['value'])
                    try:
                        self.data['name'] = float(value)
                    except ValueError:
                        self.data['name'] = value
                    return flask.jsonify({success: "true"})
                    
            '''
            @app.route('/camera')
            def camera():
                if request.environ.get('wsgi.websocket'):
                    ws = request.environ['wsgi.websocket']
            '''
                    
                
            return app
            
        self.app = app_factory()
        
    def run(self):
        self.setup()
    
        # Normally, when the app has no parameters, it runs only on
        # localhost and isn't accessible across the network. By setting
        # the host to '0.0.0.0', the http server will listen for requests
        # from this machine's local ip address.
        #self.app.run(host = '0.0.0.0', debug=False)
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
    dashboard.app.run(host=host, debug=True)
