#!/usr/bin/env python
'''
# basic_hardware.py #


## About ##

This layer is meant to be a ridiculously simple skin over whatever Arudino 
library we end up using. It lets us control the basic motors, servos, and 
other actuators in higher layers without having to remember the details of
how the Arduino works. 


## Dependencies ##

*   This layer uses a 3rd party Arduino library called 
    the [Python Arduino Command API][pyca]
    
[pyca]: https://github.com/thearn/Python-Arduino-Command-API
'''

import Arduino
import time
        
class LedLight(object):
    '''
    This class is a small wrapper class over a simple LED light.
    It does only two things: turn on, or turn off.
    '''
    def __init__(self, arduino, pin):
        '''
        self    = For an explanation on what `self` is, see the following
                  link: <http://stackoverflow.com/q/6990099/646543>
        arduino = An arduino object
        pin     = The pin the light is connected to
        '''
        self.arduino = arduino
        self.pin = pin
        self.arduino.pinMode(self.pin, 'OUTPUT')
        self.is_on = False
        
    def turn_on(self):
        self.is_on = True
        self.arduino.digitalWrite(self.pin, 'HIGH')
        
    def turn_off(self):
        self.is_on = False
        self.arduino.digitalWrite(self.pin, 'LOW')
        
    def toggle(self):
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()
        
class Motor(object):
    '''
    Currently not implemented.
    '''
    def __init__(self, arduino, pin):
        self.arduino = arduino
        self.pin = pin
        
    def set_speed(self, speed):
        pass
        
class Servo(object):
    '''
    Although both motors and servos are things that spin, they are different
    in that motors are a function of velocity and servos are a function of 
    position.
    
    You change the speed of a motor, but change the angle/position of a 
    servo.
    '''
    def __init__(self, arduino, pin):
        self.arduino = arduino
        self.pin = pin
        
    def set_position(self, speed):
        pass
        
class Encoder(object):
    '''
    Currently not implemented.
    '''
    def __init__(self, arduino, pin):
        self.arduino = arduino
        self.pin = pin
        
    def get_rate(self):
        pass
        
    def get_distance(self):
        pass
        
class Camera(object):
    '''
    Currently not implemented.
    '''
    def __init__(self, arduino):
        self.arduino = arduino
        
    def get_raw_image(self):
        pass
        
    def enable_camera(self):
        pass
        
    def disable_camera(self):
        pass
        
        
def test():
    '''
    Tests to make sure we're connected to the Arduino by toggling
    the diagnostic light once a second.
    '''
    arduino = Arduino.Arduino()
    diagnostic_light = LedLight(arduino, 13)
    while True:
        diagnostic_light.toggle()
        time.sleep(1)
        
if __name__ == '__main__':
    test()
    