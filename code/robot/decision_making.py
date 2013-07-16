#!/usr/bin/env python
'''
# decision_making.py #


## About ##

This layer is responsible for reading input from the robot, making a 
decision on what to do, and carrying out whatever it decided.

The decision-making process is essentially a "state machine". The 
robot can be in one of any multiple "states", such as "waiting",
"chasing human", or "avoiding obstacle". 

Each state is responsible for 

## Dependencies ##


'''

import sensor_analysis
import robot_actions

class WaitingState(object):
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
        if self.x_offset < 200:
            self.robot.set_left_speed(0.5)
            self.message = "Rotate left"
        elif self.x_offset > 280:
            self.robot.set_right_speed(0.5)
            self.message = "Rotate right"
        else:
            self.robot.set_forward_speed(0.5)
            self.message = "Go forward"
        return None
        
    def end(self):
        pass
        
        
class StateMachine(object):
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
    states = {
        'waiting': WaitingState(robot),
        'approach': ApproachState(robot)
    }
    return StateMachine(robot, 'waiting', states)
            
                
