#!/usr/bin/env python
'''
# basic_hardware.py #


## About ##

This layer is meant to be a ridiculously simple skin over whatever Arudino 
library we end up using. It lets us control the basic motors, servos, and 
other actuators in higher layers without having to remember the details of
how the Arduino works. 


## Confusing bits ##

If you'll notice, pretty much every single class within this module contains
a variable of some sort describing their state. For example, the Motor
class contains `self.speed`, which is a variable describing the current speed
of the motor. 

Technically, these descriptive variables are unnecessary, since it isn't used
at all in the class. However, these variables make it easier for us to easily 
tell what state the Motor is in, and are necessary if you want the user interface
to properly inspect the Motor object and report the speed.

Whenever you are making any new class within this module, be sure to include
variables that will fully describe the state of the object at any given time
because of these two reasons.


## Dependencies ##

*   This layer uses a 3rd party Arduino library called 
    the [Python Arduino Command API][pyca]
    
[pyca]: https://github.com/thearn/Python-Arduino-Command-API


## Up next ##

After reading this file, move on to `sensor_analysis.py`
'''

import math
import time
import sys
import arduino_modified as Arduino
import SimpleCV as scv
        
class LedLight(object):
    '''
    This class is a small wrapper class over a simple LED light.
    It does only two things: turn on, or turn off.
    '''
    def __init__(self, arduino, pin):
        '''
        Arguments:
        
        -   self:  
            For an explanation on what `self` is, see the following
            link: <http://stackoverflow.com/q/6990099/646543>
        -   arduino:  
            An arduino object
        -   pin:  
            The pin the light is connected to
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
    Creates a single motor, and sets the speed.
    '''
    def __init__(self, arduino, index):
        self.arduino = arduino
        self.speed = 0
        self.index = index        
        
        assert(self.index in [1, 2])
        if self.index == 1:
            self.pins = {"PWM": 3, "direction": 12}
        
            # PWM control for motor outputs 1 and 2
            self.arduino.pinMode(3, "OUTPUT")
            
            # Directional control for motor outputs 1 and 2
            self.arduino.pinMode(12, "OUTPUT")
            
        else:
            self.pins = {"PWM": 11, "direction": 13}
            
            # PWM control for motor outputs 3 and 4
            self.arduino.pinMode(11, "OUTPUT")
            
            # Directional control for motor outputs 3 and 4
            self.arduino.pinMode(13, "OUTPUT")
        

    
    def set_speed(self, speed):
        '''
        This sets the speed of the motor. It will continue spinning
        at the given speed indefinitely until given another speed. Calling
        motor.set_speed(0) will shut off the motor.
        
        The speed must be within -1 and 1 (for now).
        
        At the moment, positive speeds cause the wheel powered by the motor to spin towards
        the front of the robot (forward).
        '''
        self.speed = speed        
        
        PWM = self.pins["PWM"]
        dir = self.pins["direction"]
        
        assert(-1 <= speed <= 1)
        
        if self.speed > 0:
            self.arduino.digitalWrite(dir, "HIGH")
        else:
            self.arduino.digitalWrite(dir, "LOW")
                
        self.arduino.analogWrite(PWM, math.fabs(self.speed)*255)
        
    def stop(self):
        self.set_speed(0)
        
        
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
        self.position = 0
        
        self.arduino.Servos.attach(self.pin)
        
    def set_angle(self, position):
        self.position = position
        self.arduino.Servos.write(self.pin, position)
        
class FakeArduino(object):
    '''
    Represents a fake Arduino so we can test the code when a real Arduino is
    not connected.
    
    Only the methods we used above are implemented inside this fake class.
    Add more as necessary.
    '''
    def __init__(self, *args, **kwargs):
        '''
        This constructor accepts an arbitrary amount of arguments and keyword
        arguments so that it can accept whatever arguments you feed to the 
        actual Arduino.
        '''
        self.args = args
        self.kwargs = kwargs
        self.pins = {}
        self.Servos = FakeServos()
        
    def pinMode(self, pin, mode):
        self.pins[pin] = mode
        
    def digitalWrite(self, pin, state):
        self.pins[pin] = state
        
    def analogWrite(self, pin, value):
        self.pins[pin] = value
        
class FakeServos(object):
    def __init__(self):
        self.servos = []
        
    def attach(self, pin, *args, **kwargs):
        self.servos.append(pin)
        
def test(arduino):
    '''
    Tests to make sure we're connected to the Arduino by toggling
    the diagnostic light once a second.
    '''
    diagnostic_light = LedLight(arduino, 13)
    while True:
        diagnostic_light.toggle()
        time.sleep(1)
        
def test_motor(speed=0.5):
    board = Arduino.Arduino("9600")
    motor = Motor(board, 1)
    motor.set_speed(speed)
    test(board)
    
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_motor(sys.argv[1])
