#!/usr/bin/env python

import core

class TestWorker(core.Worker):
    def setup(self, optional="optional"):
        self.counter = 0
        self.display_counter = 0
        self.datastore['test_optional'] = optional
        
    def work(self, command):
        if self.counter == 0:
            self.display_counter += 1
            self.datastore['counter'] = self.display_counter
        
        self.counter = (self.counter + 1) % 100
        
    def kill(self):
        pass
        
