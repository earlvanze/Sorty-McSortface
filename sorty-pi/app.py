import os
import re
import cv2
import time
import argparse
import numpy as np
import tensorflow as tf
import serial
from utils.app_utils import FPS, VideoStream
from datetime import datetime
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from convert_bbox_to_gcode import convert_bbox_to_gcode

from tensorflow.python.client import device_lib


def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']


BAUD = 9600
TOUT = 0.2
GRBL_BAUD = 115200

CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
LABELS = 'model/object-detection.pbtxt'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELS)
NUM_CLASSES = 90
windowName = "Sorty"

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=NUM_CLASSES,
    use_display_name=True
)

category_index = label_map_util.create_category_index(categories)


def detect_objects(image_np, sess, detection_graph):
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded}
    )
    output_dict = {}
    output_dict['detection_boxes'] = np.squeeze(boxes)
    output_dict['detection_classes'] = np.squeeze(classes).astype(np.int32)
    output_dict['detection_scores'] = np.squeeze(scores)

    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8)
    return image_np, output_dict


def serialize(output_dict, confidence=.6):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S:%f')
    scores = output_dict['detection_scores']
    indices = [idx for idx, score in enumerate(scores) if score > confidence]
    predictions = [{
        'id': idx,
        'score': scores[idx],
        'class': output_dict['detection_classes'][idx],
        'label': category_index[output_dict['detection_classes'][idx]]['name'],
        'bbox': list(output_dict['detection_boxes'][idx]),
        'time': ts
    }
        for idx in indices
    ]
    return predictions


def readSerial(ser, term):
    matcher = re.compile(term)
    tic = time.time()
    buff = ser.read(128)
    # you can use if not ('\n' in buff) too if you don't like re
    while ((time.time() - tic) < TOUT) and (not matcher.search(buff)):
        buff += ser.read(128)

    return buff


def user_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-j",
        "--jetson",
        dest="use_jetsoncam",
        help="use Jetson on-board camera",
        action="store_true")
    ap.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index # of USB webcam (/dev/video?) [0]'
    )
    ap.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=1280,
        help='Width of the frames in the video stream. [1280]'
    )
    ap.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=720,
        help='Height of the frames in the video stream. [720]'
    )
    ap.add_argument(
        "-fr",
        "--frame_rate",
        type=int,
        default=30,
        help="Framerate of video stream."
    )
    ap.add_argument(
        "-p",
        "--picamera",
        type=int,
        default=0,
        help="whether or not the Raspberry Pi camera should be used"
    )
    ap.add_argument(
        "--rtsp",
        dest="use_rtsp",
        help="use IP CAM (remember to also set --uri)",
        action="store_true")
    ap.add_argument(
        "--uri",
        dest="rtsp_uri",
        help="RTSP URI string, e.g. rtsp://192.168.1.64:554",
        default=None, type=str)
    # latency for RTPS
    ap.add_argument(
        "--latency",
        dest="rtsp_latency",
        help="latency in ms for RTSP [200]",
        default=200, type=int)
    ap.add_argument(
        "-d",
        "--debian",
        dest="debian",
        help="use Debian-based OS",
        action="store_true")
    ap.add_argument(
        "--noserial",
        dest="no_serial",
        help="disable serial for testing without Arduinos",
        action="store_true")

    return ap.parse_args()


def move_motors(gcode, ser_grbl):

    ser_grbl.write("\r\n\r\n")
    time.sleep(2)
    ser_grbl.flushInput(21)

    for line in gcode:
        l = line.strip()
        print('Sending: ' + l)
        ser_grbl.write(l + '\n')
        grbl_out = ser_grbl.readline()
        print(' : ' + grbl_out.strip())

    time.sleep(2)

    ser_grbl.close()


def main():
    print("OpenCV version: {}".format(cv2.__version__))
    args = user_args()

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
        'output.mp4', fourcc, args.frame_rate, (args.width, args.height))
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
        ts_text = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
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

        if showHelp == True:
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
                class_prediction = str(predictions[0]['class']).encode()
                if not args.no_serial:
                    ser.write(class_prediction)
                # log results to sample.log
#                logging.info(predictions)
                print(predictions)
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
                    windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(
                    windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        elif key == ord('Q') or key == ord('q') or key == 27:  # ESC or q key to quit program
            break

    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))
    video_capture.stop()
    video_writer.release()
    cv2.destroyAllWindows()
    if not args.no_serial:
        ser.close()


if __name__ == '__main__':
    main()
