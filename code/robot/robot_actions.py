#!/usr/bin/env python

import time

import basic_hardware
import sensor_analysis

import Arduino

def no_op():
    pass

class Robot(object):
    def __init__(self, arduino=None):
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
        self.camera = basic_hardware.Camera(self.arduino)
        
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
        
    def conditional_action(
            self, 
            before=no_op, 
            until=(lambda: True), 
            during=no_op, 
            after=no_op, 
            timeout=float('inf')):
        start_time = time.time()
        before()
        while not until():
            during()
            if (time.time() - start_time) >= timeout:
                break
        after()
        return self
        
    def forward(self, until, speed=1, callback=(lambda: None), timeout=float('inf')):
        self.set_forward_speed(speed)
        start_time = time.time()
        while not until():
            callback()
            if (time.time() - start_time) >= timeout:
                break
        self.zero_speed()
        return self
        
    
            
        
        
            
        