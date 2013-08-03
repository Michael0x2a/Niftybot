import SimpleCV as scv
from datetime import datetime

def loop():
    cam = scv.Camera()
    while True:
        start = datetime.now()
        cam.getImage()
        end = datetime.now()
        delta = end-now
        print("cam capture time "+delta.seconds+delta.microseconds/1000000.0)
        

loop()