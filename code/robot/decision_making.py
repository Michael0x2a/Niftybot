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
        
    def loop(self):
        image = robot.camera.get_image()
        humans = sensor_analysis.get_human_locations(image)
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
        
        self.images = sensor_analysis.ImageProvider(robot.camera.cam)
        
    def startup(self):
        self.images.start('face')
        
    def loop(self):
        centroid = self.get_centroid(self.images.get_features())
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
        
    def end(self):
        self.images.end()
        
        
class StateMachine(object):
    def __init__(self, robot, start_state, states):
        self.robot = robot
        self.state = states[start_state]
        self.states = states
        
        self.state.startup()
        
    def loop(self):
        next = self.state.loop()
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
            
                
