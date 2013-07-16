#!/usr/bin/env python

import sys
import SimpleCV as scv

import Queue
import threading
import multiprocessing



features = [
    'eye.xml', 
    'face.xml', 
    'face2.xml', 
    'face3.xml', 
    'face4.xml', 
    'fullbody.xml', 
    'glasses.xml', 
    'lefteye.xml', 
    'left_ear.xml', 
    'left_eye2.xml', 
    'lower_body.xml',
    'mouth.xml', 
    'nose.xml', 
    'profile.xml', 
    'right_ear.xml', 
    'right_eye.xml', 
    'right_eye2.xml', 
    'two_eyes_big.xml', 
    'two_eyes_small.xml', 
    'upper_body.xml', 
    'upper_body2.xml']
    
def get_image(cam, gray = False):
    img = cam.getImage()
    if gray:
        img = img.toGray()
    return img
    
    
def simple_tracking():
    '''An example with no multithreading.'''
    cam = scv.Camera(0)
    disp = scv.Display((640, 480))
    
    scale = 0.5
    increase = round(1 / scale)
    
    while disp.isNotDone():
        img = get_image(cam)
        features = img.scale(scale).findHaarFeatures('face.xml')
        if features is not None:
            for feature in features:
                x, y = feature.topLeftCorner()
                width = feature.width()
                height = feature.height()
                img.drawRectangle(x * increase, y * increase, width * increase, height * increase, scv.Color.RED, 3)
        img.save(disp)
        #img.show()


def get_features(quality, size, features_queue, images_queue):
    '''The separate process.'''
    while True:
        try:
            raw = images_queue.get()
            
            bmp = scv.cv.CreateImageHeader(size, scv.cv.IPL_DEPTH_8U, 3)
            scv.cv.SetData(bmp, raw)
            scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
            img = scv.Image(bmp)
            
            features = img.scale(quality).findHaarFeatures('face.xml')
            
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
        


def normal_image():
    '''A multithreaded example'''
    cam = scv.Camera(0)

    img = get_image(cam)
    size = img.size()

    features_queue = multiprocessing.Queue(maxsize=5)
    
    images_queue = multiprocessing.Queue(maxsize=5)
    images_queue.put(img.toString())
    
    worker = multiprocessing.Process(target=get_features, args=(1, size, features_queue, images_queue))
    worker.start()
    
    try:
        disp = scv.Display((640, 480))
        
        features = None
        
        while disp.isNotDone():
            img = get_image(cam)
            
            try:
                features = features_queue.get(False)
                images_queue.put(img.toString())
            except Queue.Empty:
                pass
            
            if features is not None:
                for feature in features:
                    img.drawRectangle(
                        feature['top_left_x'],
                        feature['top_right_x'],
                        feature['width'],
                        feature['height'], 
                        color=scv.Color.GREEN, 
                        width = 5)
                
            img = img.applyLayers()
            img = img.flipHorizontal()
            img.save(disp)
    finally:
        worker.join()
        
if __name__ == '__main__':
    normal_image()
    #simple_tracking()

