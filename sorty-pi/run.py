import serial

SERIAL_PORT = '/dev/ttyACM0'

def main():
	ser = serial.Serial(SERIAL_PORT, 9600)
	while True:
		line = ser.readline()
		print line
		if line.strip() == "still":
	       	ser.write(str(type))


if __name__ == '__main__':
	main()
-