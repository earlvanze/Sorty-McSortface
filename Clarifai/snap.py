from pygame.locals import *
from datetime import datetime

from Clarifai import cv2

cap = cv2.VideoCapture(0)
#pygame.init()
#pygame.camera.init()
#cam = pygame.camera.Camera("/dev/video0",(640,480))
#cam.start()

def wait():
    raw_input('waiting')
    snap()

def snap():
    frame = cap.read()
    cv2.imwrite("snaps/" + "{:%H%M%S%f}".format(datetime.now()))
    #image = cam.get_image()
    #pygame.image.save(image, "snaps/" + "{:%H%M%S%f}".format(datetime.now()) + ".jpg")
    wait()

wait()
