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

import sensor_analysis
import robot_actions

class WaitingState(object):
    '''Waits for a human to appear, then starts the `approach` state'''
    def __init__(self, robot):
        self.name = 'waiting'
        self.message = 'Searching for person'
        self.robot = robot
        
    def startup(self):
        pass
        
    def loop(self, humans):
        if len(humans) > 0:
            return "approach"
        return None
        
    def end(self):
        pass
        
class ApproachState(object):
    '''Give a human, rotate the robot to face it and approaches it.'''
    def __init__(self, robot):
        self.name = 'approach'
        self.message = 'Approaching person'
        self.robot = robot
        self.x_offset = 0
        
    def startup(self):
        pass
        
    def loop(self, humans):
        centroid = sensor_analysis.get_centroid(humans)
        if len(humans) == 0:
            return 'waiting'
        self.x_offset = centroid[0]
        if self.x_offset < 300:
            self.robot.set_left_speed(0.5)
            self.message = "Rotate left"
        elif self.x_offset > 340:
            self.robot.set_right_speed(0.5)
            self.message = "Rotate right"
        else:
            self.robot.set_forward_speed(0.5)
            self.message = "Go forward"
        return None
        
    def end(self):
        pass
        
        
class StateMachine(object):
    '''
    This class is responsible for managing all the different states
    and state switching.
    '''
    def __init__(self, robot, start_state, states):
        self.robot = robot
        self.state = states[start_state]
        self.states = states
        
        self.state.startup()
        
    def loop(self, input):
        next = self.state.loop(input)
        if next is not None and next in self.states:
            self.state.end()
            self.state = self.states[next]
            self.state.startup()
            
def startup(robot):
    '''This is a convenience method to create a new `StateMachine` object.'''
    states = {
        'waiting': WaitingState(robot),
        'approach': ApproachState(robot)
    }
    return StateMachine(robot, 'waiting', states)
            
                
