import subprocess
import serial
import glob
import os
from cv import *
path = "trash*.jpg"

def main():
	ser = serial.Serial('/dev/ttyACM0', 9600)
	while True:
		line = ser.readline()
#		print line
		if line.strip() == "still":
#			print line
			subprocess.call(['./capture.sh'])
			input_file = glob.glob(path)[-1]
			type = predict(input_file)
			print(type)
			ser.write(str(type))
#			os.remove(input_file)


if __name__ == '__main__':
	main()
