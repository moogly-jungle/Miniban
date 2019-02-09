# coding: utf8
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np

class Camera:
    def __init__(self):
        self.camera = PiCamera()
        return

    def file_format(self): return 'jpg'
    
    def take_photo(self, filename = 'image'):
        siz = (640,480)
        self.camera.resolution = siz
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=siz)
        self.camera.capture(self.rawCapture,format='bgr')
        image = self.rawCapture.array
        image = cv2.flip(image,-1)
        cv2.imwrite('/var/www/html/'+filename+'.jpg',image)
        cv2.imwrite('image.jpg',image)
