import os
import cv2
import time
import serial
import tensorflow as tf
from utils.cloud import write_to_S3, connect_to_aws
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
    if not args.no_serial:
        try:
            ser_grbl.write("\r\n\r\n".encode('utf-8'))
            time.sleep(2)
            ser_grbl.flushInput()
            gcodeArray = gcode.split('\n')
            for line in gcodeArray:
                l = line.strip()
                print('Sending: ' + l)
                ser_grbl.write((l + '\n').encode('utf-8'))
                grbl_out = ser_grbl.readline().decode('utf-8')
                print(' : ' + grbl_out.strip())
            time.sleep(2)
        except:
            print("Unable to communicate with GRBL")
            raise


def get_status(ser, args):
    if not args.no_serial:
        try:
            status = ser.readline().decode('ISO-8859-1').strip("\r\n")
            return status
        except:
            print("Unable to read Arduino status")
            raise
    return "still"


def set_serial(args):
    if args.use_jetsoncam:
        GRBL_PORT = '/dev/ttyS0'
        SERIAL_PORT = '/dev/ttyS1'
    elif args.picamera or args.debian:
        GRBL_PORT = '/dev/ttyACM0'
        SERIAL_PORT = '/dev/ttyACM1'
    else:
        GRBL_PORT = '/dev/tty.usbmodem1421'
        SERIAL_PORT = '/dev/tty.usbmodem1411'
    if not args.no_serial:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD, timeout=TOUT)
        except:
            print("Unable to connect to Arduino")
            raise
            ser = None
        else:
            print(ser)
        try:
            ser_grbl = serial.Serial(GRBL_PORT, GRBL_BAUD, timeout=TOUT)
        except:
            print("Unable to connect to GRBL")
            ser_grbl = None
        else:
            print(ser_grbl)
    else:
        ser, ser_grbl = None, None
    return ser, ser_grbl


def get_rbg_copy(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


def send_motor_home(msg="No recyclables detected."):
    print(msg)
    return "G28 X0 Y0"


def main():
    print("OpenCV version: {}".format(cv2.__version__))
    ser, ser_grbl = set_serial(args)

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

    # connect to aws S3 bucket
    aws = connect_to_aws()

    while True:
        # read Arduino PIR sensor state
        status = get_status(ser, args)
        raw_frame = video_capture.read()
        rgb_frame = get_rbg_copy(raw_frame)
        if show_help:
            help_text(rgb_frame)

        if status == 'still':
            frame, output = detect_objects(rgb_frame, sess, detection_graph)
            predictions = serialize(output)
            for prediction in predictions:
                gcode = convert_bbox_to_gcode(predictions)
                print(f"{status} \n {predictions} \n {gcode}")
                move_motors(gcode, ser_grbl)

            send_motor_home(msg="No recyclables detected.")

            if not args.no_serial:
                ser.write(str(4).encode())
                while get_status(ser, args) != 'done':
                    if get_status(ser, args) == 'done':
                        break
            if predictions:
                write_to_S3(aws, predictions, frame)
            show(frame)

        elif status == 'ready':
            cv2.imshow('Video', raw_frame)

        fps.update()

        # toggles for video feed window
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
