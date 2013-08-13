#!/usr/bin/env python

import core

import SimpleCV as scv

class CameraFeed(core.Worker):
    def setup(self, camera_number=0):
        self.camera = scv.Camera(camera_number)
        image = self.camera.getImage()
        self.datastore['camera_number'] = camera_number
        self.datastore['image_size'] = image.size()
        self.datastore['image_frame'] = None
        
    def work(self, command):
        image = self.camera.getImage()
        image = image.flipHorizontal()
        self.datastore['image_frame'] = image.toString()
        #image.show()
        
    def kill(self):
        pass
        
        
class CameraAnalysis(core.Worker):
    def setup(self, target_feature='face', quality=0.5):
        self.datastore['features'] = ()
        self.datastore['centroid'] = (0, 0)
        self.datastore['target_feature'] = target_feature
        self.target_feature = target_feature + '.xml'
        self.quality = quality
        
    def work(self, command):
        if 'image_frame' not in self.datastore:
            print "not found"
            return
        
        raw = self.datastore['image_frame']
        if raw is None:
            return
            
        print "found!"
        size = self.datastore['image_size']
        
        # Arguments for:
        # opencv.CreateImageHeader(
        #   CvSize size (Python tuple),
        #   int depth
        #   int channels)
        bmp = scv.cv.CreateImageHeader(size, scv.cv.IPL_DEPTH_8U, 3)
        scv.cv.SetData(bmp, raw)
        scv.cv.CvtColor(bmp, bmp, scv.cv.CV_RGB2BGR)
        img = scv.Image(bmp)
        
        features = img.scale(self.quality).findHaarFeatures(self.target_feature)
        print features
        
        if features is not None:
            output = []
            scale = round(1 / self.quality)
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
            self.datastore['features'] = output
            self.datastore['centroid'] = self.get_centroid(output)
        #else:
        #    self.datastore['features'] = ()
        #    self.datastore['centroid'] = (0, 0)
            
    def get_centroid(self, features):
        center_x = []
        center_y = []
        for feature in features:
            center_x.append(feature['center_x'])
            center_y.append(feature['center_y'])
        average = lambda x: int(round(sum(x) / len(x)))
        if len(center_x) == 0 or len(center_y) == 0:
            return (0, 0)
        return (average(center_x), average(center_y))
        
    def kill(self):
        pass
        