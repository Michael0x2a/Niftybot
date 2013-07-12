#!/usr/bin/env python

import sys
import SimpleCV as cv

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
    img = cam.getImage().flipHorizontal()
    if gray:
        img = img.toGray()
    return img
    
    
def simple_tracking():
    cam = cv.Camera(0)
    disp = cv.Display((640, 480))
    
    while disp.isNotDone():
        img = get_image(cam)
        features = img.scale(0.25).findHaarFeatures('face.xml')
        if features is not None:
            for feature in features:
                x, y = feature.topLeftCorner()
                width = feature.width()
                height = feature.height()
                img.drawRectangle(x * 4, y * 4, width * 4, height * 4)
        img.save(disp)
        #img.show()


def get_features(size, images_queue, features_queue):
    import SimpleCV as cv
    while True:
        try:
            raw = images_queue.get()
            bmp = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
            cv.SetData(bmp, raw)
            cv.CvtColor(bmp, bmp, cv.CV_RGB2BGR)
            img = cv.Image(bmp)
            features = img.findHaarFeatures('face.xml')
            if features is not None:
                important = [(f.topLeftCorner(), f.width(), f.height()) for f in features]
                features_queue.put(important, block=False)
        except Queue.Empty:
            pass
        except Queue.Full:
            pass

def normal_image():
    cam = cv.Camera(0)
    disp = cv.Display((640, 480))

    features_queue = Queue.Queue(maxsize=5)
    features_queue.put(None)
    
    img = get_image(cam)
    images_queue = Queue.Queue()
    images_queue.put(img)
    
    worker = multiprocessing.Process(target=get_features, args=(img.size(), images_queue, features_queue))
    worker.daemon = True
    worker.start()
    
    features = None
    
    while disp.isNotDone():
        img = get_image(cam)
        images_queue.put(img.toString(), block=False)
        
        try:
            features = features_queue.get(block=False)
        except Queue.Empty:
            pass
            
        if features is not None:
            for ((x, y), width, height) in features:
                img.drawRectangle(x, y, width, height, color=cv.Color.GREEN, width = 5)
        
        img.save(disp)
        
if __name__ == '__main__':
    #normal_image()
    simple_tracking()

