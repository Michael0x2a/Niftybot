#!/usr/bin/env python

import multiprocessing
import Queue
import datetime

import SimpleCV as scv

class Worker(multiprocessing.Process):
    def __init__(self, name, datastore, mailbox, *args, **kwargs):
        super(Worker, self).__init__(name=name)
        self.datastore = datastore
        self.mailbox = mailbox
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            self.setup(*self.args, **self.kwargs)
            while True:
                try:
                    command = self.mailbox.get_nowait()
                except Queue.Empty:
                    command = None
                if command == "kill":
                    break
                self.work(command)
        except:
            self.send_command('all', 'kill')
            raise
        finally:
            self.kill()
        
    def send_command(self, recipient, data):
        self.mailbox.put_nowait([recipient, data])
        
    def setup(self, *args, **kwargs):
        raise NotImplementedError()
        
    def work(self, command):
        raise NotImplementedError()
        
    def kill(self):
        raise NotImplementedError()
        
class Mailbox(object):
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.datastore = self.manager.dict()
        self.workers = {}
        self.datastore['active_workers'] = ()
        
    def register_worker(self, name, worker_class, *args, **kwargs):
        conn = multiprocessing.Queue()
        worker = worker_class(name, self.datastore, conn, *args, **kwargs)
        self.workers[name] = (worker, conn)
        
    def mainloop(self):
        try:
            for name, (worker, conn) in self.workers.items():
                worker.start()
            while True:
                self.loop()
                if len(self.workers) == 0:
                    break
        except KeyboardInterrupt:
            pass
        except:
            raise
        finally:
            self.send_universal_command("die")
            for name, (worker, conn) in self.workers.items():
                worker.terminate()
                worker.join()
                print 'Killed {0}'.format(name)
            
    def loop(self):
        active_workers = []
        
        for name, (worker, conn) in self.workers.items():
            if not worker.is_alive():
                del self.workers[name]
            else:
                active_workers.append(name)
            try:
                message = conn.get_nowait()
            except Queue.Empty:
                message = None
            
            if message is None:
                continue
                
            recipient, command = message
            if recipient == 'all':
                self.send_universal_command(command)
            elif recipient == 'mailbox':
                self.process_command(command)
            else:
                self.send_command(recipient, command)
        
        self.datastore['active_workers'] = active_workers
            
    def send_universal_command(self, command):
        for name, (worker, conn) in self.workers.items():
            conn.put_nowait(command)
        
    def send_command(self, recipient, command):
        if recipient in self.workers:
            self.workers[recipient][1].put_nowait(command)
            
    def process_command(self, command):
        if command == 'take_snapshot':
            with open('log.txt', 'a') as f:
                snapshot = str(self.datastore)
                f.write('{0}\n\n------------------\n\n'.format(snapshot))
                
                
                