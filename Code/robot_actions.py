#!/usr/bin/env python
'''

# robot_actions.py


## Introduction ##

This module contains code to represent a single, conceptual "robot", 
combining both basic hardware objects from `basic_hardware.py` and analytics
from `sensor_analytics.py`.

This class is essentially a high-level interface to control a single robot.


## Confusing bits ##

This module currently contains only a single `Robot` class. In the future, if 
we make different robot variants, we should create a new class instead of modifying
the current one.


## Dependencies ##

*   This layer uses the `basic_hardware` layer to control basic components.
*   This layer uses the `sensor_analysis` layer to provide some extra control
    over the robot.
*   This layer uses a 3rd party Arduino library called 
    the [Python Arduino Command API][pyca]
    
[pyca]: https://github.com/thearn/Python-Arduino-Command-API


## Up next ##

After reading this file, move to `decision_making.py`.

'''

import time

import basic_hardware
import sensor_analysis

import Arduino

class Robot(object):
    def __init__(self, arduino=None):
        '''
        Note: if this robot cannot connect to an Arduino, it 
        connects to a fake one instead.
        '''
        if arduino is None:
            try:
                self.arduino = Arduino.Arduino()
            except:
                self.arduino = basic_hardware.FakeArduino()
        else:
            self.arduino = arduino
        self.diagnostic_light = basic_hardware.LedLight(self.arduino, 13)
        self.left_wheel = basic_hardware.Motor(self.arduino, 14)
        self.right_wheel = basic_hardware.Motor(self.arduino, 15)
        
    def set_speed(self, left, right):
        self.left_wheel.set_speed(left)
        self.right_wheel.set_speed(right)
        return self
        
    def set_forward_speed(self, speed=1):
        self.set_speed(speed, speed)
        return self
        
    def set_backward_speed(self, speed=1):
        self.set_speed(-speed, -speed)
        return self
        
    def set_left_speed(self, speed=1):
        self.set_speed(-speed, speed)
        return self
        
    def set_right_speed(self, speed=1):
        self.set_speed(speed, -speed)
        return self
        
    def zero_speed(self):
        self.set_speed(0, 0)
        return self
        
        