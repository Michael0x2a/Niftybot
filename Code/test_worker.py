import core

class TestWorker(core.Worker):
    def setup(self):
        self.counter = 0
        self.display_counter = 0
        
    def work(self, command):
        if self.counter == 0:
            self.display_counter += 1
            self.datastore['counter'] = self.display_counter
            self.send_command('mailbox', 'take-snapshot')
        
        self.counter = (self.counter + 1) % 100
        
    def kill(self):
        pass
        
