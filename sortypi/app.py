import os
import cv2
import time
import tensorflow as tf
import serial
from inference import detect_objects, serialize
from utils.app_utils import FPS, VideoStream
from datetime import datetime as dt
from commands import args
from convert_bbox_to_gcode import convert_bbox_to_gcode


BAUD = 9600
TOUT = 0.2
GRBL_BAUD = 115200
CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)

WINDOW_NAME = "Sorty"


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


def main():
    print("OpenCV version: {}".format(cv2.__version__))
    GRBL_PORT = '/dev/ttyACM0'
    SERIAL_PORT = '/dev/ttyACM1'

    if (args.use_jetsoncam):
        GRBL_PORT = '/dev/ttyS0'
        SERIAL_PORT = '/dev/ttyS1'
    elif (args.picamera or args.debian):
        GRBL_PORT = '/dev/ttyACM0'
        SERIAL_PORT = '/dev/ttyACM1'
    else:
        # MacOS
        GRBL_PORT = '/dev/tty.usbmodem1421'
        SERIAL_PORT = '/dev/tty.usbmodem1411'

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
    video_capture = VideoStream(
        usePiCamera=args.picamera > 0,
        resolution=(args.width, args.height),
        framerate=args.frame_rate,
        use_jetsoncam=args.use_jetsoncam,
        src=args.video_source
    ).start()

    fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
    video_writer = cv2.VideoWriter(
        'output.avi', fourcc, args.frame_rate, (args.width, args.height))
    time.sleep(2.0)

    fps = FPS().start()

    showHelp = True
    showFullScreen = False
    helpText = "'Esc' or 'Q' to Quit, 'H' to Toggle Help, 'F' to Toggle Fullscreen"
    font = cv2.FONT_HERSHEY_PLAIN

    while True:
        # read Arduino PIR sensor state
        if not args.no_serial:
            status = ser.readline().decode('utf-8').strip("\r\n")
        else:
            status = "still"
        raw_frame = video_capture.read()
        t = time.time()
        ts_text = dt.now().strftime("%A %d %B %Y %I:%M:%S%p")
        position = (10, raw_frame.shape[0] - 10)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        color = (0, 0, 255)
        # put information text in the lower bottom corner
        cv2.putText(
            raw_frame,
            ts_text,
            position,
            font_face,
            font_scale,
            color,
            1
        )
        # transform image into rgb
        rgb_frame = cv2.cvtColor(
            raw_frame,
            cv2.COLOR_RGB2BGR
        )

        if showHelp:
            cv2.putText(raw_frame, helpText, (11, 20), font,
                        1.0, (32, 32, 32), 4, cv2.LINE_AA)
            cv2.putText(raw_frame, helpText, (10, 20), font,
                        1.0, (240, 240, 240), 1, cv2.LINE_AA)

        if status == 'still':
            frame, raw_output = detect_objects(
                rgb_frame,
                sess,
                detection_graph
            )
            predictions = serialize(raw_output)
            print(predictions)

            if predictions:
                print(status)
                gcode = convert_bbox_to_gcode(predictions)
                print(gcode)
                if not args.no_serial:
                    move_motors(gcode, ser_grbl)
            else:
                print("No recyclables detected. Probably trash.")
                if not args.no_serial:
                    ser.write(str(4).encode())

            bgr_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
            cv2.imshow('Video', bgr_frame)

        elif status == 'ready':
            cv2.imshow('Video', raw_frame)

        fps.update()
        video_writer.write(raw_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('H') or key == ord('h'):
            showHelp = not showHelp
        elif key == ord('F') or key == ord('f'):
            showFullScreen = not showFullScreen
            if showFullScreen:
                cv2.setWindowProperty(
                    WINDOW_NAME,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_FULLSCREEN,
                )
            else:
                cv2.setWindowProperty(
                    WINDOW_NAME,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_NORMAL,
                )
        elif key == ord('Q') or key == ord('q') or key == 27:
            break

    fps.stop()
    video_capture.stop()
    video_writer.release()
    cv2.destroyAllWindows()

    if not args.no_serial:
        ser.close()
        ser_grbl.close()


if __name__ == '__main__':
    main()
