import os
import re
import cv2
import time
import argparse
import logging
import numpy as np
import tensorflow as tf
import serial
import json
import boto3
from datetime import datetime
from imutils.video import FPS, VideoStream
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from convert_bbox_to_gcode import *
from utils import cloud

BAUD = 9600
TOUT = 3.0

CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
LABELS = 'model/object-detection.pbtxt'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELS)
NUM_CLASSES = 90
BUCKET_NAME = 'sorty-logs'

session = boto3.Session(
    aws_access_key_id='AWS_ACCESS_KEY_ID',
    aws_secret_access_key='AWS_SECRET_ACCESS_KEY',
)

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
    matcher = re.compile(term)  # gives you the ability to search for anything
    tic = time.time()
    buff = ser.read(128)
    # you can use if not ('\n' in buff) too if you don't like re
    while ((time.time() - tic) < TOUT) and (not matcher.search(buff)):
        buff += ser.read(128)

    return buff


def user_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index of the camera.'
    )
    ap.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=1280,
        help='Width of the frames in the video stream.'
    )
    ap.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=720,
        help='Height of the frames in the video stream.'
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
        default=-1,
        help="whether or not the Raspberry Pi camera should be used"
    )
    return ap.parse_args()


def main():
    logging.basicConfig(filename="sample.log", level=logging.INFO)
    args = user_args()
    detection_graph = tf.Graph()

    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)

    video_capture = VideoStream(
        usePiCamera=args.picamera > 0,
        resolution=(args.width, args.height),
        framerate=args.frame_rate
    ).start()
    time.sleep(2.0)
    fps = FPS().start()

    while True:
        status = "still"
        raw_frame = video_capture.read()
        t = time.time()
        ts_text = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
        position = (10, raw_frame.shape[0] - 10)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        color = (0, 0, 255)
        cv2.putText(
            raw_frame,
            ts_text,
            position,
            font_face,
            font_scale,
            color,
            1
        )
        rgb_frame = cv2.cvtColor(
            raw_frame,
            cv2.COLOR_RGB2BGR
        )
        frame, raw_output = detect_objects(
            rgb_frame,
            sess,
            detection_graph
        )
        predictions = serialize(raw_output)
        # Save predictions to S3
        if len(predictions) > 0:
            ts = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
            outpath = f"{ts}.json"
            cloud.write_to_S3(session, predictions, BUCKET_NAME, outpath)
        cv2.imshow('Video', frame)
        if predictions and status == 'still':
            class_prediction = str(predictions[0]['class']).encode()
            convert_bbox_to_gcode(predictions)
            logging.info(predictions)
            print(predictions)
        elif status == "still":
            print(datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f'))
        else:
            print("Waiting for something....")
            time.sleep(2)
        fps.update()
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))
    video_capture.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
