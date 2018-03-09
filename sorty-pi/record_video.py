# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from cv2 import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1920, 1080))

# set up video writer format
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# set up video writer
video_writer = cv2.VideoWriter('recording.m4v', fourcc, 30.0, (1280, 720))
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
 
	# show the frame
	cv2.imshow("Frame", image)
	video_writer.write(image)
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

video_writer.release()
cv2.destroyAllWindows()
