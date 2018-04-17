import os
import cv2
import time
import tensorflow as tf
import serial
from inference import detect_objects, serialize
from utils.app_utils import FPS
from commands import args
from convert_bbox_to_gcode import convert_bbox_to_gcode
from video import stream, show, full_screen, normal_screen, help_text

BAUD = 9600
TOUT = 0.2
GRBL_BAUD = 115200
CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)


def move_motors(gcode, ser_grbl):
    ser_grbl.write("\r\n\r\n".encode())
    time.sleep(2)
    ser_grbl.flushInput()
    for line in gcode:
        l = line.strip()
        print('Sending: ' + l)
        ser_grbl.write(l + '\n'.encode())
        grbl_out = ser_grbl.readline()
        print(' : ' + grbl_out.strip())
    time.sleep(2)


def set_ports(args):
    if args.use_jetsoncam:
        GRBL_PORT = '/dev/ttyS0'
        SERIAL_PORT = '/dev/ttyS1'
    elif args.picamera or args.debian:
        GRBL_PORT = '/dev/ttyACM0'
        SERIAL_PORT = '/dev/ttyACM1'
    else:
        GRBL_PORT = '/dev/tty.usbmodem1421'
        SERIAL_PORT = '/dev/tty.usbmodem1411'
    return GRBL_PORT, SERIAL_PORT


def set_status(ser, args):
    if not args.no_serial:
        status = ser.readline().decode('utf-8').strip("\r\n")
        return status
    return "still"


def main():
    print("OpenCV version: {}".format(cv2.__version__))
    GRBL_PORT, SERIAL_PORT = set_ports(args)
    if not args.no_serial:
        ser = serial.Serial(SERIAL_PORT, BAUD, timeout=TOUT)
        ser_grbl = serial.Serial(GRBL_PORT, GRBL_BAUD, timeout=TOUT)

    # load tensorflow graph
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        # initialize tf session
        sess = tf.Session(graph=detection_graph)

    # start video stream
    video_capture = stream(args).start()
    fps = FPS().start()
    show_help = True
    show_full_screen = False

    while True:
        # read Arduino PIR sensor state
        status = set_status(ser, args)
        raw_frame = video_capture.read()
        rgb_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

        if show_help:
            help_text(rgb_frame)

        if status == 'still':
            frame, output = detect_objects(rgb_frame, sess, detection_graph)
            predictions = serialize(output)
            print(predictions)
            if predictions:
                gcode = convert_bbox_to_gcode(predictions)
                print(f"{status} \n {gcode}")
                if not args.no_serial:
                    move_motors(gcode, ser_grbl)
            else:
                print("No recyclables detected. Probably trash.")
                if not args.no_serial:
                    ser.write(str(4).encode())

            show(frame)

        elif status == 'ready':
            cv2.imshow('Video', raw_frame)

        fps.update()

        # shit show.
        key = cv2.waitKey(1) & 0xFF
        if key == ord('H') or key == ord('h'):
            show_help = not show_help
        elif key == ord('F') or key == ord('f'):
            show_full_screen = not show_full_screen
            if show_full_screen:
                full_screen(args)
            else:
                normal_screen(args)
        elif key == ord('Q') or key == ord('q') or key == 27:
            break

    fps.stop()
    video_capture.stop()
    cv2.destroyAllWindows()

    if not args.no_serial:
        ser.close()
        ser_grbl.close()


if __name__ == '__main__':
    main()
