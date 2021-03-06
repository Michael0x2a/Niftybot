#!/usr/bin/env python
'''
# sensor_analysis.py #


## About ##

This file analyzes information from various sensors on the robot
defined in `basic_hardware.py` and returns useful information to 
help with decision-making. 

In the future, the image processing code may be moved to a 
separate module.


## Confusing bits ##

The image processing code is confusing within this module
because it contains two versions: a simple version, and a 
multi-threaded version. 

Basically, the image processing is too slow. Using it normally
will cause noticeable freezes of half a second to two seconds each
between each update. 

As a result, using multithreading is mandatory to get anywhere 
near the performance we need.

Note: technically, this code does multi-processing, not 
multi-threading. Multi-threading launches new "threads", which are
still part of the original program. Multi-prcessing launches new
processes, which are completely new instances of Python running
on the operating-system level.

Using multi-processing simplifies code a tad, can take advantage of
multiple cores, and will, in general, run faster when computation 
speed is the bottleneck.

Note that if IO (reading from a website/database) is the bottleneck,
using threads may be a better choice.

When I use the term "multi-threaded" in the documentation, I am 
treating processes and threads as interchangeable for clarity
(multi-processed feels silly to write).

You may want to first read the [Python documentation][mc] on the 
`multiprocessing` module first.

  [mp]: http://docs.python.org/2/library/multiprocessing.html


## Dependencies ##

*   This layer uses the `basic_hardware` layer to grab raw
    sensor data.
*   This layer uses a 3rd party library called [SimpleCV][sc]
    for vision processing.

  [sc]: http://www.simplecv.org/
  

## Up next

After reading this file, read `robot_actions.py`.
'''

from __future__ import division

import multiprocessing
import Queue
import time

import SimpleCV as scv

def get_human_locations(image, quality = 0.25, target_feature="upper_body"):
    '''
    Gets the location of humans detected in the provided SimpleCV image. 
    This is the simple, non-multi-processing version of the human-tracking code,
    used for illustration purposes.
    
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
    
    The `full_feature` item contains the original `Features` object 
    produced by SimpleCV, which contains all the additional data which 
    is not normally returned.
    
    In essense, this is how this function works:
    
        1.  Validate the input
        2.  Scale the image using the `quality` input. The smaller the image,
            the quicker this will run.
        3.  Using `target_features`, find the xml file describing feature you want.
            These xml files are provided by the SimpleCV library, and were created by
            analyzing a large quantity of features. For example, if you wanted to find
            only faces, you would use `face.xml`, which contains information about what
            the average face statistically looks like, based on the training data. Each
            face found is considered a "feature".
        4.  Using the statistical model provided within the xml file, analyze the image
            to find all the features present within the image.
        5.  Parse the output. If there are no features, return an empty list. Otherwise,
            grab only the data we need.
        6.  Scale the coordinates of the features back up depending on how much they were
            originally scaled down. This ensures that all the coordinates returned are 
            correct respective to the original image.
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
        
def _get_features(features_queue, images_queue, message_queue, size, quality, target_feature):
    '''
    This is part of the multi-threaded version of the algorithm described in 
    `find_human_features`.
    
    You should never directly call this function outside of the `ImageProvider`
    class.
    
    The reason why I cannot simply do some magic to convert `find_human_features`
    into a multi-threaded function that runs in parallel to the main program and
    returns results is because Python has several limitations in how it does
    multi-processing.
    
        1.  You can pass only Python primatives back and forth, such as strings
            or numbers. The `Image` object from SimpleCV is not a primative
            Python object. As a result, we pass a binary string function between
            this process and the original program to bypass this limitation.
        2.  Data can only be passed in and out through `multiprocessing.Queue` objects.
        3.  This function does not validate the input.
        
    If this function cannot find a feature, it returns either an empty list or None.
        
    See `ImageProvider` for more information.
    '''
    while True:
        output = None
        try:
            # bookkeeping
            message = message_queue.get(False)
            if message == "terminate":
                return
        except Queue.Empty:
            pass
        
        try:
            # Get the image, but give up if it takes longer then 2 seconds to get.
            raw = images_queue.get(timeout = 2)
            
            # Convert the raw image string into a SimpleCV image object.
            bmp = scv.cv.CreateImageHeader(size, scv.cv.IPL_DEPTH_8U, 3)
            scv.cv.SetData(bmp, raw)
            scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
            img = scv.Image(bmp)
            
            # Use Haar features as usual.
            features = img.scale(quality).findHaarFeatures(target_feature + '.xml')
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
                        #'full_feature': feature
                    })
            # If any of the Queues to receive data is empty or full, ignore.
        except Queue.Empty:
            pass
        except Queue.Full:
            pass
        features_queue.put(output)
        
          
          
class ImageProvider(object):
    '''
    This class provides a friendly way to process features in a separate process
    and return results.
    '''
    def __init__(self, cam, delta=1):
        self.cam = cam
        self.features = []
        self.last = time.time()
        self.delta = delta
        
    def start(self, feature):
        '''
        This method starts a separate process to find features. It also 
        provides an initial image for the process to work with.
        
        Note: the only way to communicate between two processes (the original
        program is technically a process) is through Queues, which are thread-safe
        list-like objects where you can append and take data.
        
        To pass images and feature data back and forth, we create Queue objects
        and append or get the data. You can conceptually think of them as "pipes".
        
        Whatever you put in a Queue can be retrieved from the same Queue in an 
        arbitrary number of objects.
        '''
        img = self.cam.getImage()#.flipHorizontal()
        self.size = img.size()

        self.features_queue = multiprocessing.Queue()
        
        self.images_queue = multiprocessing.Queue()
        self.images_queue.put(img.toString())
        
        self.message_queue = multiprocessing.Queue()
        
        self.worker = multiprocessing.Process(target=_get_features, args=(
            self.features_queue, self.images_queue, self.message_queue, self.size, 0.5, feature))
        self.worker.start()
        
    def get_features(self):
        '''This grabs an image from the camera, converts it to a string, and 
        passes it to the worker to process. While the worker returns None
        (not finished processing), this method will return the last known
        list of features. Otherwise, it'll return the newest one and command
        the worker to start processing a new frame.'''
        img = self.cam.getImage()#.flipHorizontal()
        
        try:
            features = self.features_queue.get(False)
            self.images_queue.put(img.toString())
            if features is not None:
                self.last = time.time()
                self.features = features
            elif (time.time() - self.last) > self.delta:
                self.features = []
        except Queue.Empty:
            pass
        
        return self.features
        
    def end(self):
        '''This safely ends the previously-started process.'''
        self.message_queue.put('terminate', False)
        self.worker.terminate()
        
def get_centroid(features):
    '''Calculates a sequence of features, and finds the average x and y centerpoints
    between them. Therefore, given a crowd of people, this function can find the 
    approximate center of the crowd.'''
    center_x = []
    center_y = []
    for feature in features:
        center_x.append(feature['center_x'])
        center_y.append(feature['center_y'])
    average = lambda x: int(round(sum(x) / len(x)))
    if len(center_x) == 0 or len(center_y) == 0:
        return (0, 0)
    return (average(center_x), average(center_y))
    
        
        
