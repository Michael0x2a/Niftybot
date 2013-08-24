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
import math

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
                self.kind = "Real"
            except:
                self.arduino = basic_hardware.FakeArduino()
                self.kind = "Fake"
        else:
            self.arduino = arduino
            self.kind = "Passed"

        # if arm_servo is None:            
        #    self.arm_servo = basic_hardware.Servo(self.arduino, 5)
        # else:
        #    self.arm_servo = arm_servo
            
        '''
        if laptop_servo is None:
            self.laptop_servo = basic_hardware.Servo(self.arduino, 6)
        else:
            self.laptop_servo = laptop_servo
        '''
        
        self.left_wheel = basic_hardware.Motor(self.arduino, "left")
        self.right_wheel = basic_hardware.Motor(self.arduino, "right")
        
    def set_speed(self, left, right):
        self.left_wheel.set_speed(left*0.6)
        self.right_wheel.set_speed(0.5*right*0.6)
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
        if 50 <= position < 180:
            print(str(position)+" : This is the position used in set_laptop_tilt")
            start_position = self.laptop_servo.position
            new_position = position
            movement = int(math.fabs(new_position-start_position))
            
            
            if new_position > start_position:
                delta = 1
            else:
                delta = -1
                
                
            current = start_position
            
            for i in range(movement):
                time.sleep(0.5/180.0) # takes 0.5 extra sec to travel 180 degrees 
                current += delta
                self.laptop_servo.set_angle(current)
        
        
    def adjust_laptop_tilt(self, increment):
        position = self.laptop_servo.position
        self.set_laptop_tilt(position+increment)
    
    def smart_adjust_tilt(self, y_offset, laptop_length):
        position = self.laptop_servo.position
        new_position = math.asin(2.0*y_offset/laptop_length)
        self.set_laptop_tilt(new_position)
    
    def set_arm_position(self, position):
        if 0 < position < 180:
            start_position = self.laptop_servo.position
            new_position = position
            movement = int(math.fabs(new_position-start_position))
            
            
            if new_position > start_position:
                delta = 1
            else:
                delta = -1
                
                
            current = start_position
            
            for i in range(movement):
                time.sleep(0.5/180.0) # takes 0.5 extra sec to travel 180 degrees 
                current += delta
                self.laptop_servo.set_angle(current)
