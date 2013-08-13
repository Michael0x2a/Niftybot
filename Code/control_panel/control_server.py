#!/usr/bin/env python

import flask
import cherrypy.wsgiserver

import core

class ControlServer(core.Worker):
    def setup(self):
        def app_factory():
            app = flask.Flask(self.name)
            
            @app.route('/', methods=['GET'])
            def index():
                output = '\n'.join([
                    r'<!DOCTYPE html><html>',
                    r'<head><title>Niftybot debug</title></head>',
                    r'<body>',
                    r'<strong>Nifybot debug</strong>',
                    r'<dl>{0}</dl>',
                    r'</body></html>'])
                
                debug = []
                for name in self.datastore.keys():
                    if name == 'image_frame':
                        value = '[IMAGE]'
                    else:
                        value = self.datastore[name]
                    debug.append('<dt>{0}</dt><dd>{1}</dd>'.format(name, value))
                output = output.format('\n'.join(debug))
                
                return output
                
            @app.route('/about/')
            def about():
                return "About me!"
                
            return app
            
        self.app = app_factory()
        
        # Normally, when the app has no parameters, it runs only on
        # localhost and isn't accessible across the network. By setting
        # the host to '0.0.0.0', the http server will listen for requests
        # from this machine's local ip address.
        #self.app.run(host = '0.0.0.0', debug=False)
        self.app.run(debug=True)
        
        #host = '127.0.0.1'
        #port = 5000
        
        #dispatcher = cherrypy.wsgiserver.WSGIPathInfoDispatcher({'/': self.app})
        #self.server = cherrypy.wsgiserver.CherryPyWSGIServer((host, port), dispatcher)
        #self.server.start()
        
    def work(self, command):
        pass
            
    def kill(self):
        pass 
        #self.server.stop()
        
    def get_snapshot(self):
        return str(self.datastore)
        
