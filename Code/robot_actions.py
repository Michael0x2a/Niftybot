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

import arduino_modified as Arduino

class Robot(object):
    def __init__(self, arduino=None, arm_servo=None, laptop_servo=None):
        '''
        Note: if this robot cannot connect to an Arduino, it 
        connects to a fake one instead.
        '''
        if arduino is None:
            try:
                self.arduino = Arduino.Arduino("9600")
            except:
                self.arduino = basic_hardware.FakeArduino()
        else:
            self.arduino = arduino

        # if arm_servo is None:            
        #    self.arm_servo = basic_hardware.Servo(self.arduino, 5)
        # else:
        #    self.arm_servo = arm_servo
            
        
        # if laptop_servo is None:
        #    self.laptop_servo = basic_hardware.Servo(self.arduino, 6)
        # else:
        #    self.laptop_servo = laptop_servo
        
        self.left_wheel = basic_hardware.Motor(self.arduino, "left")
        self.right_wheel = basic_hardware.Motor(self.arduino, "right")
        self.camera = basic_hardware.Camera(self.arduino)
        
    def set_speed(self, left, right):
        self.left_wheel.set_speed(left)
        self.right_wheel.set_speed(0.5*right)
        return self
        
    def set_forward_speed(self, speed=1):
        self.set_speed(speed, speed)
        return self
        
    def set_backward_speed(self, speed=1):
        self.set_speed(-speed, -speed)
        return self
        
    def set_left_speed(self, speed=1):
        self.set_speed(-speed, 0.8*speed)
        return self
        
    def set_right_speed(self, speed=1):
        self.set_speed(speed, -speed)
        return self
        
    def zero_speed(self):
        self.set_speed(0, 0)
        return self
        
    def stop(self):
        self.zero_speed()
    
    def set_laptop_tilt(self, position):
        self.laptop_servo.set_angle(position)
        
    def adjust_laptop_tilt(self, increment):
        position = self.laptop_servo.position
        self.set_laptop_tilt(position+increment)
    
    def smart_adjust_tilt(self, y_offset, laptop_length):
        position = self.laptop_servo.position
        new_position = math.asin(2.0*y_offset/laptop_length)
        self.set_laptop_tilt(new_position)
    
    def set_arm_position(self, position):
        self.arm_servo.set_angle(position)

