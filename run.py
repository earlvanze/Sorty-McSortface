import subprocess
import serial
import glob
import os
from cv import *
import sys

path = "trash*.jpg"

mode = len(sys.argv)
is_debug = mode > 1

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
                        if is_debug:
                                type = input('1 = ee, 2 = metal, 3 = paper, 4 = plastic')
                                material = ''
                                if type == 1:
                                        material = 'ee'
                                if type == 2:
                                        material = 'metal'
                                if type == 3:
                                        material = 'paper'
                                if type == 4:
                                        material = 'plastic'
                                result = execute_js('set_status.js ' + material)
                                result = execute_js('update.js ' + material)
                                time.sleep(0.1)
                                result = execute_js('set_status.js waiting')

	       	        ser.write(str(type))
#			os.remove(input_file)


if __name__ == '__main__':
	main()
