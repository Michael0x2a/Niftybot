#!/usr/bin/env python
'''
Contains code for last-resort error handling.
'''

import sys
from datetime import datetime

import Tkinter
import tkMessageBox

__version__ = "1.0.0"
__release__ = "May 28, 2013"

def error(message, record=False):
    '''Opens a window reporting an error. This is for when the program 
    is so borked that something has crashed in some way.'''
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showerror('Error!', message)
    if record:
        log(message)
    sys.exit()
    
def log(message):
    '''Opens a logfile and appends the error message to it.'''
    with open('log.txt', 'a') as logfile:
        text = '\n'.join([
            'Metadata:',
            '    Timestamp: ' + str(datetime.now()),
            '    Version:   ' + __version__,
            '',
            'BEGIN MESSAGE:',
            '',
            message,
            'END MESSAGE',
            '',
            '~~~~~~~~~~~~~~~~~~~~~~',
            ''])
        logfile.write(text)