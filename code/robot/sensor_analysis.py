#!/usr/bin/env python
'''
# sensor_analysis.py #


## About ##

This file analyzes information from various sensors on the robot
and returns useful information to help with decision-making. 

This layer is currently extremely empty.

## Dependencies ##

*   This layer uses the `basic_hardware` layer to grab raw
    sensor data.
*   This layer uses a 3rd party library called [SimpleCV][sc]
    for vision processing.

[sc]: http://www.simplecv.org/
'''

from __future__ import division
import multiprocessing
import Queue

import SimpleCV as scv

def get_human_locations(image, quality = 0.25, target_feature="upper_body"):
    '''
    
    Gets the location of humans detected in the provided SimpleCV image. 
    
    Arguments:
    
    -   image:  
        The image in SimpleCV format to extract data from.
    -   quality:  
        At which quality the image should be analyzed. If the quality is set 
        to 1.0 (the max), the image analyzing will be of good quality, but 
        very slow. If it's set to something like 0.25, the image analyzing 
        will be faster, but less accurate. Internally, the `quality` variable
        is used to scale the image to change the resolution.
    -   target_feature:  
        The part of the human body to look for. The full list of valid 
        "features" can be found below, but we should stick to either
        `face`, `upper_body`, or `lower_body`. 
        
    Returns:
    
    A list containing information about each "feature" detected. If no 
    features are found in the image, the list will be empty.
    
    Each element inside the list is a dict containing the following items:
    
    -   height
    -   width
    -   top_left_x
    -   top_left_y
    -   center_x
    -   center_y
    -   full_feature
    
    The height, width, top left coordinates, and center coordinates are 
    the pixel coordinates of the detected feature respective to the top
    left corner of the original image. 
    
    The `full_feature` item is a 
    '''
    valid_features = [
        'eye', 
        'face', 
        'face2', 
        'face3', 
        'face4', 
        'fullbody', 
        'glasses', 
        'lefteye', 
        'left_ear', 
        'left_eye2', 
        'lower_body',
        'mouth', 
        'nose', 
        'profile', 
        'right_ear', 
        'right_eye', 
        'right_eye2', 
        'two_eyes_big', 
        'two_eyes_small', 
        'upper_body', 
        'upper_body2']
    assert(0 < quality <= 1)
    assert(target_feature in valid_features)
    
    features = image.scale(quality).findHaarFeatures(target_feature + ".xml")
    if features is None:
        return []
    else:
        output = []
        for feature in features:
            scale = round(1 / quality)
            x, y = feature.topLeftCorner()
            output.append({
                'height': feature.height() * scale,
                'width': feature.width() * scale,
                'top_left_x': x * scale,
                'top_right_x': y * scale,
                'center_x': feature.x * scale,
                'center_y': feature.y * scale,
                'full_feature': feature
            })
        return output
        
def _get_features(feat, quality, size, features_queue, images_queue):
    while True:
        try:
            raw = images_queue.get()
            
            bmp = scv.cv.CreateImageHeader(size, scv.cv.IPL_DEPTH_8U, 3)
            scv.cv.SetData(bmp, raw)
            scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
            img = scv.Image(bmp)
            
            features = img.scale(quality).findHaarFeatures(feat + '.xml')
            
            if features is not None:
                output = []
                scale = round(1 / quality)
                for feature in features:
                    x, y = feature.topLeftCorner()
                    output.append({
                        'height': feature.height() * scale,
                        'width': feature.width() * scale,
                        'top_left_x': x * scale,
                        'top_right_x': y * scale,
                        'center_x': feature.x * scale,
                        'center_y': feature.y * scale,
                        'full_feature': feature
                    })
                features_queue.put(output)
        except Queue.Empty:
            pass
        except Queue.Full:
            pass
          
          
class ImageProvider(object):
    def __init__(self, cam):
        self.cam = cam
        self.features = []
        
    def start(self, feature):
        img = self.cam.getImage().flipHorizontal()
        size = img.size()

        self.features_queue = multiprocessing.Queue(maxsize=5)
        
        self.images_queue = multiprocessing.Queue(maxsize=5)
        self.images_queue.put(img.toString())
        
        self.worker = multiprocessing.Process(target=_get_features, args=(
            feature, 1, size, self.features_queue, self.images_queue))
        self.worker.start()
        
    def get_features(self):
        img = self.cam.getImage().flipHorizontal()
        
        try:
            features = self.features_queue.get(False)
            self.images_queue.put(img.toString())
            self.features = features
        except Queue.Empty:
            pass
        
        return self.features
        
    def end(self):
        self.worker.end()
        
def get_centroid(features):
    center_x = []
    center_y = []
    for feature in features:
        center_x.append(feature['center_x'])
        center_y.append(feature['center_y'])
    average = lambda x: int(round(sum(x) / len(x)))
    if len(center_x) == 0 or len(center_y) == 0:
        return (0, 0)
    return (average(center_x), average(center_y))
    
class EncoderWatcher(object):
    '''
    A wrapper class which reads one or more encoders from the
    `basic_hardware` layer and determines what the average distance
    between all the encoders are.
    '''
    def __init__(self, *encoders):
        self.encoders = encoders
        self.initial_snapshot = []
        self.final_snapshot = []
        
    def start():
        self.initial_snapshot = self.get_snapshot()
        
    def end():
        self.final_snapshot = self.get_snapshot()
        
    def get_snapshot():
        return [encoder.get_distance() for encoder in self.encoders]
        
    def get_current_distance():
        return self.calculate_average_distance(
            self.initial_snapshot, 
            self.get_snapshot())
            
    def get_final_distance():
        return self.calculate_average_distance(
            self.initial_snapshot,
            self.final_snapshot())
        
    def calculate_average_distance(start, end):
        average_start = sum(start) / len(start)
        average_end = sum(end) / len(end)
        return average_end - average_start
        
        