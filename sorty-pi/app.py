import os
import cv2
import time
import argparse
import logging
import numpy as np
import tensorflow as tf
import serial
import re

from datetime import datetime
from imutils.video import FPS, VideoStream
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

#SERIAL_PORT = '/dev/ttyACM0'
SERIAL_PORT = '/dev/tty.usbmodem1421'
BAUD = 9600
TOUT = 3.0

CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
LABELS = 'model/object-detection.pbtxt'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELS)
NUM_CLASSES = 90


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=NUM_CLASSES,
    use_display_name=True
)

category_index = label_map_util.create_category_index(categories)


def detect_objects(image_np, sess, detection_graph):
    # Expand dimensions since the model expects
    # images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image
    # where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded}
    )
    output_dict = {}
    output_dict['detection_boxes'] = np.squeeze(boxes)
    output_dict['detection_classes'] = np.squeeze(classes).astype(np.int32)
    output_dict['detection_scores'] = np.squeeze(scores)

    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8)
    return image_np, output_dict


def serialize(output_dict, confidence=.75):
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

def readSerial(ser,term):
    matcher = re.compile(term)    #gives you the ability to search for anything
    tic     = time.time()
    buff    = ser.read(128)
    # you can use if not ('\n' in buff) too if you don't like re
    while ((time.time() - tic) < TOUT) and (not matcher.search(buff)):
       buff += ser.read(128)

    return buff

def user_args():
    ap = argparse.ArgumentParser()
    # video source
    ap.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index of the camera.'
    )
    # video width
    ap.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=580,
        help='Width of the frames in the video stream.'
    )
    # video height
    ap.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=460,
        help='Height of the frames in the video stream.'
    )
    # frame rate
    ap.add_argument(
        "-fr",
        "--frame_rate",
        type=int,
        default=4,
        help="Framerate of video stream."
    )
    # use pi camara?
    ap.add_argument(
        "-p",
        "--picamera",
        type=int,
        default=-1,
        help="whether or not the Raspberry Pi camera should be used"
    )
    return ap.parse_args()

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=TOUT)
    print(ser.name)  # check which port was really used

    # start logging file
    logging.basicConfig(filename="sample.log", level=logging.INFO)
    # get user args
    args = user_args()
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
        framerate=args.frame_rate
    ).start()
    # sleep for 2 seconds...
    time.sleep(2.0)
    # start frames per second timer
    fps = FPS().start()
    # while fps._numFrames < 120
    while True:
        # read Arduino PIR sensor state
        status = ser.readline().decode('utf-8').strip("\r\n")
#        status = readSerial(ser, "still")
        print(status)

        raw_frame = video_capture.read()
        t = time.time()
        # set information
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
        # get img and raw output
        frame, raw_output = detect_objects(
            rgb_frame,
            sess,
            detection_graph
        )
        # serialize output
        predictions = serialize(raw_output)

        # show image
        cv2.imshow('Video', frame)
        if predictions:
            # sample output
            # [{'id': 0, 'score': 0.98922765, 'class': 1, 'label': 'metal',
            # 'bbox': [0.2890249, 0.39757824, 0.714632, 0.6900569],
            # 'time': '2018-02-20T10:46:11:207357'}]
            for prediction in predictions:
                print(prediction['class'])
                if status == "still":
                    ser.write(str(prediction['class']).encode())
#                    status = readSerial(ser, "done")
#                    status = ser.readline().decode('utf-8').strip("\r\n")
#                    if status != "done":
#                        status = ser.readline().decode('utf-8').strip("\r\n")
#                        print(status)
#                        time.sleep(0.1)

            # log results to sample.log
            logging.info(predictions)

#        else:
#            print("Nothing detected.")

        key = cv2.waitKey(1) & 0xFF
        fps.update()
#        print('[INFO] elapsed time: {:.2f}'.format(time.time() - t))
        if key == ord('q'):
            break

    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))
    # stop video
    video_capture.stop()
    # destroy window
    cv2.destroyAllWindows()
    ser.close()


if __name__ == '__main__':
	main()