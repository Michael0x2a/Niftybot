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

After reading this file, move to `dashboard.py`
'''

# Libraries included within the Python standard library
import sys
import json
import copy
import types
import multiprocessing

import basic_hardware
import sensor_analysis
import robot_actions
import decision_making
import drawing
import dashboard

import arduino_modified as Arduino
import SimpleCV as scv
import cv2
import pygame

DEBUG = False


def inspect(thing, layers=1, prettyprint = False, exclude=[]):
    '''
    This function performs a bit of meta-programming to inspect 
    any arbitrary python object, and returns a dictionary mapping all of the 
    objects attributes (but not methods!) to their values.
    
    Arguments:
    
    -   thing:  
        The object to inspect.
    -   layers:  
        How deep to analyze the object. If layers equals 1, it only returns
        a dict of attributes of `thing`. If layers equals 2, it inspects any
        objects contained within the `thing` object.
    -   prettyprint:  
        Defaults to false. If set to true, the output would be a neatly
        formatted JSON string.
        
    Returns:
    
    -   A dictionary mapping all the attributes inside an arbitrary object
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
        
    try:
        output = copy.deepcopy(thing.__dict__)
    except AttributeError:
        return thing
        
    if layers > 1:
        for attr, value in thing.__dict__.items():
            if not isinstance(value, exclude):
                output[attr] = inspect(value, layers - 1, prettyprint, exclude=exclude)
    
    output = {attr: "(HIDDEN)" if isinstance(value, exclude) else value for (attr, value) in output.items()}
    
    if prettyprint:
        return json.dumps(output, indent=4)
    else:
        # This is a very clumsy way of filtering out objects that don't
        # have a sensible string representation.
        # Doing str(obj) for an arbitrary object returns something like:
        #
        #   `<robot_actions.Robot instance at 0x0287B498>`
        return output
        
    
class ControlPanel(object):
    '''
    This class is the main UI.
    '''
    def __init__(self, robot, state):
        self.robot = robot
        self.state = state
        
    def setup(self):
        pygame.init()
        self.window = drawing.Window()
        self.screen = self.window.screen
        self.font = pygame.font.SysFont("arial", 12)

        self.to_inspect = [
        #    ('robot', self.robot, 2, (Arduino.Arduino, basic_hardware.FakeArduino, scv.Camera)), 
        #    ('state', self.state, 3, (Arduino.Arduino, basic_hardware.FakeArduino, scv.Camera, robot_actions.Robot))]
        
        ]
                
        
        self.cam = scv.Camera(1)
        self.images = sensor_analysis.ImageProvider(self.cam)
        self.is_manual = False
            
        # Currently detects the face. See the source code of 
        # `sensor_analysis.find_human_features` for a full list of possible
        # features.
        self.images.start('face')
        
        self.mailbox = multiprocessing.Queue()
        self.data = multiprocessing.Manager().dict()
        self.dashboard = dashboard.Dashboard('dashboard', self.data, self.mailbox)
        self.dashboard.start()
        
        
    def mainloop(self):
        '''
        This runs the program indefinitely.
        
        It first updates the state machine, then updates the graphics.
        '''
        features = []
        self.setup()
        
        self.data['straight'] = 0
        self.data['rotate'] = 0
        self.data['manual'] = False
        
        try:    
            while True:
                # I/O
                self.process_events()
                
                image = self.cam.getImage()
                image = image.flipHorizontal()
                
                self.try_manual_control()
                
                while not self.mailbox.empty():
                    name, value = self.mailbox.get_nowait()
                    self.data[name] = value
                
                # Processing
                features = self.images.get_features()
                self.data['centroid'] = sensor_analysis.get_centroid(features)
                self.data['humans'] = features
                
                for name, obj in self.get_inspected():
                    print(name)
                    print(obj)
                    print(", ")
                    self.data[name] = obj
                
                # Handling decisions
                self.state.loop(self.data)
                if not DEBUG:
                    self.state.draw(self.data, self.window)
                else:
                    self.debug(image, features)

                # Display
                #self.draw_camera_feed(image)
                #self.draw_features(features)
                #self.draw_inspected(660, 20)
                
                # Bookkeeping
                #self.heartbeat()
        except:
            raise
        finally:
            pygame.quit()
            self.images.end()
            self.dashboard.terminate()
    
    def debug(self, image, features):
        self.draw_camera_feed(image)
        self.draw_features(features)
        self.draw_inspected(660, 20)
        self.heartbeat()        

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
                scv.Color.RED,
                pygame.Rect(
                    feature['top_left_x'],
                    feature['top_right_x'],
                    feature['width'],
                    feature['height']),
                3)
        centroid = sensor_analysis.get_centroid(features)
        pygame.draw.circle(
            self.screen,
            scv.Color.GREEN,
            centroid,
            20,
            5)
            
    def get_inspected(self):
        for (name, obj, depth, exclude) in self.to_inspect:
            yield (name, inspect(obj, depth, exclude=exclude))
            
    def draw_inspected(self, x, y):
        '''Draw a clean version of the list of features on the pygmae surface.
        
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
            
        for index, (name, obj) in enumerate(self.get_inspected()):
            vert(obj, x + index * 200, y)
        
    def try_manual_control(self, scale=0.5):
        def get_speed(key):
            return 1 if pygame.key.get_pressed()[key] else 0
    
        forward = get_speed(pygame.K_UP)
        back = get_speed(pygame.K_DOWN)
        left = get_speed(pygame.K_LEFT)
        right = get_speed(pygame.K_RIGHT)
        
        straight = (forward - back) * scale
        rotate = (right - left) * scale
        
        self.data['straight'] = straight
        self.data['rotate'] = rotate
    
    def process_events(self):
        '''Keeps the user interface GUI from going haywire, and responds to
        user data input.'''
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.is_manual = not self.is_manual
                self.data['manual'] = self.is_manual
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
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
    robot = robot_actions.Robot(Arduino())
    robot.set_forward_speed(1)
    print inspect(robot, 2, True)
    
    
    
if __name__ == '__main__':
    main()
