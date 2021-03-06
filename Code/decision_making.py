#!/usr/bin/env python
'''
# decision_making.py #


## About ##

This layer is responsible for reading input from the robot, making a 
decision on what to do, and carrying out whatever it decided.

The decision-making process is essentially a "state machine". The 
robot can be in one of any multiple "states", such as "waiting",
"chasing human", or "avoiding obstacle". 

Each state is responsible for using the robot and a list of features to
determine what to do next. If `None` is returned from `loop`, the code 
will stay on the same loop. If a string is returned, the state will
switch to the new state specified by the string.


## Confusing bits ##

Note: each class must implement a `startup` method, a `loop` method which is 
repeatedly called (and runs the main logic and determines to stay in the current
state or move on to the next one)


## Dependencies ##

-   This layer uses the `sensor_analysis` layer to analyze the output from some
    sensors.
-   This layer uses the `robot_actions` layer to control the robot based on the 
    state.
    

## Up next ##

After reading this file, move on to `user_interface.py
'''

import math
import time
import socket

import sensor_analysis
import robot_actions
import drawing

class StartupState(object):
    '''Displays startup info.'''
    def __init__(self, robot):
        self.name = 'startup'
        self.message = 'Displaying startup info.'
        self.robot = robot
        self.wait_time = 30

    def startup(self):
        self.robot.set_speed(0, 0)
        self.proceed = False
        self.start = time.time()

    def loop(self, data):
        if self.proceed:
            return 'waiting'
        if time.time() - self.start > self.wait_time:
            return 'waiting'

    def draw(self, data, window):
        window.draw_mood('aqua')
        window.draw_text(
            'Webserver address:',
            socket.gethostbyname(socket.gethostname()) + ':5000',
            'Starting in {0:.1f} sec'.format(self.wait_time - (time.time() - self.start)))
        buttons = drawing.make_buttons(window, "Continue")
        for button in buttons:
            window.draw_button(button)
            if button.is_pressed(data.get('mousepress', [0, 0])):
                self.proceed = True
            if self.proceed:
                window.draw_filled_button(button)

    def end(self):
        pass


class WaitingState(object):
    '''Waits for a human to appear, then starts the `approach` state'''
    def __init__(self, robot):
        self.name = 'waiting'
        self.message = 'Searching for person'
        self.robot = robot
        
    def startup(self):
        '''time.sleep(1)
        self.robot.set_left_speed()
        time.sleep(2)
        self.robot.stop()'''
        self.robot.stop()
        
    def loop(self, data):
        self.robot.set_left_speed(0.9)
        time.sleep(1)
        
        if len(data.get('humans', [])) > 0:
            return "approach"
            
        return None

    def draw(self, data, window):
        window.draw_mood('blue')
        window.draw_text('Hello?')

    def end(self):
        pass
        
class ApproachState(object):
    '''Give a human, rotate the robot to face it and approaches it.'''
    def __init__(self, robot):
        self.name = 'approach'
        self.message = 'Approaching person'
        self.robot = robot
        
    def startup(self):
        self.pressed = None
        self.pressed_time = None
        self.x_offset = 0

    def loop(self, data):
        if self.pressed is not None:
            self.robot.set_speed(0, 0)
            if self.pressed_time is None:
                self.pressed_time = time.time()
            delta = time.time() - self.pressed_time
            if delta < 5:
                return
            else:
                return 'backoff'

        humans = data.get('humans', [])
        centroid = sensor_analysis.get_centroid(humans)
        if len(humans) == 0:
            return 'waiting'
            
        self.x_offset = centroid[0]

        self.center = data.get('image_size', [640, 480])
        width = self.center[0]
        height = self.center[1]                

        max_human_width = 0
        max_human_height = 0
        
        for human in humans:
            if human["height"] > max_human_height:
                max_human_height = human["height"]
        
        #if max_human_height > height*0.8:
        #    self.robot.stop()   
        #    self.message = "Stopped - someone is nearby"
        
        if True:
            if self.x_offset < width * 0.4:
                self.robot.set_left_speed(1)
                self.message = "Rotate left"
            elif self.x_offset > width * 0.6:
                self.robot.set_right_speed(1)
                self.message = "Rotate right"
            else:
                self.robot.set_forward_speed(1)
                self.message = "Go forward"

        self.y_offset = centroid[1]

        if self.y_offset < height*0.35:
            pass
            # self.robot.adjust_laptop_tilt(5)
            # print ("Person is high " +str(self.y_offset)+", Servo position: " + str(self.robot.laptop_servo.position))            
        elif self.y_offset > height*0.65:
            pass
            # self.robot.adjust_laptop_tilt(-5)
            # print ("Person is low " +str(self.y_offset)+", Servo position: " + str(self.robot.laptop_servo.position))            
        else:
            pass
        
    def draw(self, data, window):
        window.draw_mood('green')

        if self.pressed == 'Yes':
            window.draw_text("Thank you!")
        elif self.pressed == 'No':
            window.draw_text('Let me know if', 'you change your mind!')
        else:
            window.draw_text('Would you like to', 'donate some money?')#, "Message: "+self.message)
        buttons = drawing.make_buttons(window, "Yes", "No")
        for button in buttons:
            window.draw_button(button)
            if button.is_pressed(data.get('mousepress', [0, 0])):
                self.pressed = button.text
            if self.pressed == button.text:
                window.draw_filled_button(button)
        return None

    def end(self):
        pass

class BackOffState(object):
    def __init__(self, robot):
        self.name = 'backoff'
        self.message = 'Donation finished; backing off'
        self.robot = robot

    def startup(self):
        self.robot.set_speed(0, 0)
        self.start = time.time()

    def loop(self, data):
        delta = time.time() - self.start
        if 0 < delta <= 2.5:
            self.robot.set_speed(1, 0)
        elif 2.5 < delta <= 5:
            self.robot.set_speed(1, 1)
        elif delta > 5:
            return 'waiting'

    def draw(self, data, window):
        window.draw_mood('orange')
        window.draw_text('Hmm...')

    def end(self):
        self.robot.stop()

        
class ManualControlState(object):
    def __init__(self, robot):
        self.name = 'manual'
        self.message = 'Manually controlling robot.'
        self.robot = robot
        
    def startup(self):
        self.robot.set_speed(0, 0)
        
    def loop(self, data, max_speed=1):
        straight = data.get('straight', 0)
        rotate = data.get('rotate', 0)
        
        left_wheel = 0
        right_wheel = 0
        
        left_wheel = right_wheel = straight
        
        left_wheel = left_wheel + rotate
        right_wheel = right_wheel - rotate
        
        def clamp(speed, top):
            if abs(speed) > top:
                return top * (-1 if speed < 0 else 1)
            else:
                return speed
                
        left_wheel = clamp(left_wheel, max_speed)
        right_wheel = clamp(right_wheel, max_speed)
        
        self.robot.set_speed(left_wheel, right_wheel)

    def draw(self, data, window):
        window.draw_mood('purple')
        window.draw_text('MANUAL CONTROL')
        
    def end(self):
        self.robot.set_speed(0, 0)
        
class StateMachine(object):
    '''
    This class is responsible for managing all the different states
    and state switching.
    '''
    def __init__(self, robot, start_state, states):
        self.robot = robot
        self.state = states[start_state]
        self.state_name = start_state
        self.states = states
        self.suspended = None
        
    def start(self):
        self.state.startup()

    def loop(self, data):
        next = self.state.loop(data)
        next = self.intercept_manual_control(data, next)
        if next is not None and next in self.states:
            self.state.end()
            self.state = self.states[next]
            self.state.startup()
            self.state_name = next

    def draw(self, data, window):
        self.state.draw(data, window)
        window.heartbeat()
            
    def intercept_manual_control(self, data, next):
        is_manual = data.get('manual', False)
        if is_manual and self.state_name != 'manual':
            self.suspended = self.state_name
            return 'manual'
        if not is_manual and self.state_name == 'manual':
            out = self.suspended
            self.suspended = None
            return out
        return next
        
            
def startup(robot):
    '''This is a convenience method to create a new `StateMachine` object.'''
    states = {
        'startup': StartupState(robot),
        'waiting': WaitingState(robot),
        'approach': ApproachState(robot),
        'manual': ManualControlState(robot),
        'backoff': BackOffState(robot),
    }
    return StateMachine(robot, 'startup', states)
            
                
