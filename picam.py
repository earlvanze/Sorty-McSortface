from picamera import PiCamera
from time import sleep

camera = PiCamera()

def take_photo():
    camera.start_preview()
    sleep(2)
    camera.capture('/home/pi/Desktop/trash.jpg')
    camera.stop_preview()
