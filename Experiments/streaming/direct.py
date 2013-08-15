import SimpleCV as scv
import time

def run():
    cam = scv.Camera(0)
    stream = scv.Stream.JpegStreamer()
    while True:
        img = cam.getImage().flipHorizontal()
        img.save(stream)
        time.sleep(0.1)
        
        
if __name__ == '__main__':
    run()
    