#!/usr/bin/env python
'''
# user_interface.py


## Introduction ##

This layer contains information and code to display what is currently
happening in the program.

The user interface layer is, in the end, essentially superficial.
The underlying code should be flexible enough to be adapted to any 
new UI without having to change in any manner, and should be able to
run independently with or without the user interface.

However, in practice, the user_interface provides the high-level logic 
to power the state machine.


## Confusing bits ##

Technically, we could have used SimpleCV's display window. However, I 
chose to use pygame for the additional flexibility it gave us.


## Dependencies ##

This layer requires every module within this project, the SimpleCV
library, and the pygame library to display the UI.


## Up next ##

After reading this file, move to `errors.py`
'''

# Libraries included within the Python standard library
import sys
import json
import copy
import types

import basic_hardware
import sensor_analysis
import robot_actions
import decision_making

import SimpleCV as cv
import pygame
from datetime import datetime


def inspect(thing, layers=1, prettyprint = False):
    '''
    This function performs a bit of meta-programming to inspect 
    any arbitrary python object, and returns a dictionary mapping all of the 
    objects attributes (but not methods!) to their values.
    
    Arguments:
    
    -   thing:  
        The object to inspect.
    -   layers:  
        How deep to analyze the object. If layers equals 1, it only returns
        a dict of attribtes of `thing`. If layers equals 2, it inspects any
        objects contained within the `thing` object.
    -   prettyprint:  
        Defaults to false. If set to true, the output would be a neatly
        formated JSON string.
        
    Returns:
    
    -   A dictionary mapping all the attributes inside an arbitary object
        to their values.
        
    How it works:
    
    The key insight to realize is that every object in Python contains an
    automatically created `__dict__` attribute which is a dictionary mapping
    attributes to their values. 
    
    This is exactly what we want. The bulk of the code is spent filtering
    out useless values (such as non-primitive objects), and inspecting 
    nested objects if `layers` is greater then `.
    '''
    if type(thing) == dict:
        return thing
    output = copy.deepcopy(thing.__dict__)
    
    if layers > 1:
        for attr, value in thing.__dict__.items():
            if isinstance(object, (type, types.ClassType)):
                output[attr] = inspect(value, layers - 1)
                
    if prettyprint:
        return json.dumps(output, indent=4, default=lambda x: '')
    else:
        # This is a very clumsy way of filtering out objects that don't
        # have a sensible string representation.
        # Doing str(obj) for an arbitrary object returns something like:
        #
        #   `<robot_actions.Robot instance at 0x0287B498>`
        return json.loads(json.dumps(
            output, 
            default = lambda x: str(x) if 'instance at' not in str(x) else '<obj>'))
        
    
class ControlPanel(object):
    '''
    This class is the main UI.
    '''
    def __init__(self, robot, state):
        pygame.init()
        self.size = (1200, 480)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Niftybot")
        self.font = pygame.font.Font(pygame.font.get_default_font(), 12)
        
        self.robot = robot
        self.state = state
        
        self.to_inspect = [(self.robot, 2), (self.state, 2)]
        self.images = sensor_analysis.ImageProviderManager(robot.camera.cam, 10)
        
        # Currently detects the face. See the source code of 
        # `sensor_analysis.find_human_features` for a full list of possible
        # features.
        self.images.start('face')
        
    def mainloop(self):
        '''
        This runs the program indefinitely.
        
        It first updates the state machine, then updates the graphics.
        '''
        self.get_feature_start = [datetime.now()]
        self.get_end = datetime.now()
        
        try:
            while True:
                
                image = self.robot.camera.get_image()
                image = image.flipHorizontal()
                #print("UserInterface.mainloop: image acquired")
                
                self.get_start = datetime.now()
                
                features = self.images.get_features()
                print("Time between successive calls to providermanager.get_features: "+sensor_analysis.time_string(self.get_end, self.get_start))                
                self.get_end = datetime.now()
                print("Time to run providermanager.get_features: "+sensor_analysis.time_string(self.get_start, self.get_end))                
                print("------------------------\n")

                
                #print("UserInterface.mainloop: features acquired")
                
                start = datetime.now()
                
                self.state.loop(features)
                #print("UserInterface.mainloop: features passed to state loop")
                self.draw_camera_feed(image)
                self.draw_features(features)
                self.draw_inspected(660, 20)
                #print("UserInterface.mainloop: features drawn")
                
                end = datetime.now()
                
                
                #print("Non feature-acquisition took "+sensor_analysis.time_string(start, end)+"(user_interface.mainloop()")
                
                
                self.process_events()
                self.heartbeat()
        finally:
            self.images.end()
            
    def draw_camera_feed(self, image):
        '''Draws the camera image to the pygame surface.'''
        surface = image.getPGSurface()
        self.screen.blit(surface, (0, 0))
            
    def draw_features(self, features):
        '''Draws the list of features as a series of rectangles to the 
        pygame surface.'''
        for feature in features:
            pygame.draw.rect(
                self.screen, 
                cv.Color.RED,
                pygame.Rect(
                    feature['top_left_x'],
                    feature['top_right_x'],
                    feature['width'],
                    feature['height']),
                3)
        centroid = sensor_analysis.get_centroid(features)
        pygame.draw.circle(
            self.screen,
            cv.Color.GREEN,
            centroid,
            20,
            5)
            
    def draw_inspected(self, x, y):
        '''Draw a clean version of the list of features on the pygame surface.
        
        Each object to be inspected gets their own column.'''
        def vert(text, x, y):
            offset = 0
            for index, (name, pair) in enumerate(text.items()):
                if type(pair) == dict:
                    out = str(name) + " : "
                else:
                    out = str(name) + " : " + str(pair)
                
                self.screen.blit(
                    self.font.render(out, True, (255,255,255)), 
                    (x, y + offset + index * 16))
                if type(pair) == dict:
                    offset += vert(pair, x + 16, y + offset + index * 16 + 16)
            offset = len(text) * 16
            return offset
            
                    
        for index, (obj, depth) in enumerate(self.to_inspect):
            obj = inspect(obj, depth)
            vert(obj, x + index * 200, y)
            
            
    def process_events(self):
        '''Keeps the user interface GUI from going hairwire, and responds to
        user data input.'''
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            self.images.end()
            sys.exit()
            
    def heartbeat(self):
        '''Contains the bare minimum to keep the program alive.'''
        pygame.display.flip()
        self.screen.fill((0,0,0))
            
def main():
    robot = robot_actions.Robot()
    states = decision_making.startup(robot)
    control = ControlPanel(robot, states)
    control.mainloop()
    
def test_inspector():
    robot = robot_actions.Robot(basic_hardware.FakeArduino())
    robot.set_forward_speed(1)
    print inspect(robot, 2, True)
    
    
    
if __name__ == '__main__':
    main()