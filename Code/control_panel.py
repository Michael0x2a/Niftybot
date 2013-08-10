import flask

import core

class ControlServer(core.Worker):
    def setup(self):
        def app_factory():
            app = flask.Flask(self.name)
            
            @app.route('/')
            def index():
                output = "{0}\n\n{1}"
                output = output.format(
                    "Hello world!",
                    self.get_snapshot())
                return output
                
            return app
            
        self.app = app_factory()
        self.app.run()
        
    def work(self, command):
        pass
            
    def kill(self):
        pass
        
    def get_snapshot(self):
        return str(self.datastore)
        
