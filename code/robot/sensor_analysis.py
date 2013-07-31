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
import datetime
import time
from datetime import datetime
import SimpleCV as scv
     

def time_string(start, end):
    delta = end-start
    return str(delta.seconds + delta.microseconds/1000000.0)

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
        
def _get_features(features_queue, images_queue, size, quality, target_feature, provider=1):
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
        output = []
        try:
            # Get the image, but give up if it takes longer then 2 seconds to get.
            raw = images_queue.get(timeout = 2)
            # print("Size of image queue after get: "+str(images_queue.qsize())+" (_get_features())")
            # Convert the raw image string into a SimpleCV image object.
            bmp = scv.cv.CreateImageHeader(size, scv.cv.IPL_DEPTH_8U, 3)
            scv.cv.SetData(bmp, raw)
            scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
            img = scv.Image(bmp)
            
            # Use Haar features as usual.
            
            start = datetime.now()
            features = img.scale(quality).findHaarFeatures(target_feature + '.xml')
            if features is not None:
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
            # If any of the Queues to receive data is empty or full, ignore.
            
            end = datetime.now()
            
            # print("Features acquired from provider #"+str(provider)+". "+str(len(output))+" features found."+"Took "+time_string(start,end)+"sec (_get_features)")
        except Queue.Empty:
            pass
        except Queue.Full:
            pass
        features_queue.put(output)
        # print("Size of features queue after put: "+str(features_queue.qsize())+" (_get_features())")
        
          
class ImageProviderManager(object):
    def __init__(self, cam, num_of_providers=2):
        self.cam = cam
        self.providers = []
        self.provider_index = 0  
        self.runtimes = []
        self.updating = True
        self.add_process = True
            
        for i in range(num_of_providers):
            self.providers.append(ImageProvider(cam, len(self.providers)))   
                

            
    def start(self, feature='face'):                    
        for provider in self.providers:
            provider.start(feature)
        self.target_feature = feature        
        start = datetime.now()
        self.providers[self.provider_index].get_features()
        end = datetime.now()
        delta = end-start            
            
        self.avg_runtime = delta.seconds+delta.microseconds/1000000.0                
        self.run_instances = 1
        print("ImageProviderManage.start(): provider manager started")
        
    def add_provider(self):
        new_provider = ImageProvider(self.cam, len(self.providers))
        self.providers.append(new_provider)
        # print("ImageProviderManager.add_provider: provider created")       
        self.providers[-1].start(self.target_feature)
        
    def change_target_feature(self, feature):
        self.target_feature = feature
    
    def remove_provider(self, index=-1):
        if len(self.providers) != 1:
            self.providers[index].end()
            self.providers.pop(index)
        
    def get_features(self):

        start = datetime.now()
        
        self.provider_index %= len(self.providers)
        
        self.loopstart = datetime.now()
        features = self.providers[self.provider_index].get_features()
        # print("ImageProviderManager: features acquired FROM PROVIDER: "+str(self.provider_index))
        self.provider_index += 1
        
        end = datetime.now()
        
        delta = end-start            
        timespan = delta.seconds+delta.microseconds/1000000.0
        
        self.runtimes.append(timespan)
        self.avg_runtime = (timespan+self.avg_runtime*(self.run_instances))/(self.run_instances+1)
        
        self.run_instances+=1
        
        #if self.updating:
        self.update(10)
         
        return features
            
    def toggle_update_method(self):
        if self.add_process:
            self.add_process = False
        else:
            self.add_process = True
            
    def update(self, period):        
       
        recent_runtimes = 0
        try:
            for i in range(period):
                recent_runtimes += self.runtimes[i]/float(period)
                
            #if there are <period> values in runtimes and setting recent_runtimes was successful, reset runtimes    
            self.runtimes = []
            
            #reset the number of run instances for computing averages
            self.run_instances = 0
            
            
            try:
                delta = recent_runtimes - self.old_avg_runtime
                
                #if image processing got faster
                if delta < 0:
                    print("####getting faster####")
                    if self.add_process:
                        self.add_provider()
                        print("------ImageProviderManager: adding provider. NUMBER OF PROVIDERS: "+str(len(self.providers))+"-----")   
                            
                    else:
                        self.remove_provider()
                        print("-----ImageProviderManager: removing provider. NUMBER OF PROVIDERS: "+str(len(self.providers))+"-----")                                            
             
                #if image processing got slower, reverse the direction of update change    
                else:
                    print("####getting slower####")                
                    if self.add_process:
                        self.remove_provider()
                        self.toggle_update_method()
                        print("-----ImageProviderManager: removing provider. NEW NUMBER OF PROVIDERS: "+str(len(self.providers))+"-----")                                                                            
                            
                    else:
                        self.add_provider()
                        self.toggle_update_method()
                        print("------ImageProviderManager: adding provider. NEW NUMBER OF PROVIDERS: "+str(len(self.providers))+"-----")   
                                                          
                print("----ImageProviderManager: average runtime = "+str(recent_runtimes)+"\n")
            #if self.old_avg runtime is undefined, do nothing
            except AttributeError: 
                pass
                              
            
            #save the old average runtime before starting to compute a new one
            self.old_avg_runtime = self.avg_runtime             
            
        except IndexError:
            pass 
            
    def end(self):
        for provider in self.providers:
            provider.end()
            
            
class ImageProvider(object):
    '''
    This class provides a friendly way to process features in a separate process
    and return results.
    '''
    def __init__(self, cam, provider_index):
        self.cam = cam
        self.features = []
        self.provider_index = provider_index
        self.processing_start = [datetime.now()]
        
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
        
        img = self.cam.getImage().flipHorizontal()
        size = img.size()

        self.features_queue = multiprocessing.Queue()
        
        self.images_queue = multiprocessing.Queue()
        self.images_queue.put(img.toString())
        
        self.worker = multiprocessing.Process(target=_get_features, args=(
            self.features_queue, self.images_queue, size, 1.0, feature, self.provider_index))
        self.worker.start()
        
    def get_features(self):
        '''This grabs an image from the camera, converts it to a string, and 
        passes it to the worker to process. While the worker returns None
        (not finished processing), this method will return the last known
        list of features. Otherwise, it'll return the newest one and command
        the worker to start processing a new frame.'''
        img = self.cam.getImage().flipHorizontal()
        
        self.processing_start.append(datetime.now())
        self.images_queue.put(img.toString())
        
        try:
            start = datetime.now()
            
            p_end = datetime.now()
            p_start = self.processing_start[-2]
            
            # print("Time between start of processing and call to get: "+time_string(p_start,p_end))
            
            features = self.features_queue.get(False)
            end = datetime.now()
            # print("Time to get feature from queue for provider #"+str(self.provider_index)+": "+time_string(start,end)+" Features length: "+str(len(features))+" (ImageProvider.get_features)")                
            
            if features is not None:
                self.features = features
        except Queue.Empty:
            print("Features queue was empty (ImageProvider.get_features)")
        return self.features
        
    def end(self):
        '''This safely ends the previously-started process.'''
        #self.worker.join()
        self.images_queue.close()
        self.features_queue.close()
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
    
class EncoderWatcher(object):
    '''
    A wrapper class which reads one or more encoders from the
    `basic_hardware` layer and determines what the average distance
    between all the encoders are.
    
    Not currently implemented.
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
        
        