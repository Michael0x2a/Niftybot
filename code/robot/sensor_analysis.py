#!/usr/bin/env python
'''
# sensor_analysis.py #


## About ##

This file analyzes information from various sensors on the robot
and returns useful information to help with decision-making. 

This layer is currently extremely empty.

## Dependencies ##

*   This layer uses the `basic_hardware` layer to grab raw
    sensor data.
*   This layer uses a 3rd party library called [SimpleCV][sc]
    for vision processing.

[sc]: http://www.simplecv.org/
'''

from __future__ import division

import SimpleCV

def get_human_locations(image):
    pass
    
class EncoderWatcher(object):
    '''
    A wrapper class which reads one or more encoders from the
    `basic_hardware` layer and determines what the average distance
    between all the encoders are.
    '''
    def __init__(self, *encoders):
        self.encoders = encoders
        self.initial_snapshot = []
        self.final_snapshot = []
        
    def start():
        self.initial_snapshot = self.get_snapshot()
        
    def end():
        self.final_snapshot = self.get_snapshot()
        
    def get_snapshot():
        return [encoder.get_distance() for encoder in self.encoders]
        
    def get_current_distance():
        return self.calculate_average_distance(
            self.initial_snapshot, 
            self.get_snapshot())
            
    def get_final_distance():
        return self.calculate_average_distance(
            self.initial_snapshot,
            self.final_snapshot())
        
    def calculate_average_distance(start, end):
        average_start = sum(start) / len(start)
        average_end = sum(end) / len(end)
        return average_end - average_start
        
        