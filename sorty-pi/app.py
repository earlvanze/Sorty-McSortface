import os
import cv2
import time
import argparse
import logging
import numpy as np
import tensorflow as tf

from datetime import datetime
from imutils.video import FPS, VideoStream
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

CWD_PATH = os.getcwd()
GRAPH_NAME = 'inference_graph/frozen_inference_graph.pb'
LABELS = 'model/object-detection.pbtxt'
PATH_TO_CKPT = os.path.join(CWD_PATH, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, LABELS)

NUM_CLASSES = 90

parser = argparse.ArgumentParser()
parser.add_argument('-src', '--source', dest='video_source', type=int,
                    default=0, help='Device index of the camera.')
parser.add_argument('-wd', '--width', dest='width', type=int,
                    default=580, help='Width of the frames in the video stream.')
parser.add_argument('-ht', '--height', dest='height', type=int,
                    default=460, help='Height of the frames in the video stream.')
parser.add_argument("-p", "--picamera", type=int, default=-1,
                    help="whether or not the Raspberry Pi camera should be used")
args = vars(parser.parse_args())

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=NUM_CLASSES,
    use_display_name=True
)

category_index = label_map_util.create_category_index(categories)


def detect_objects(image_np, sess, detection_graph):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
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


def serialize(output_dict):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S:%f')
    scores = output_dict['detection_scores']
    indices = [idx for idx, score in enumerate(scores) if score > .75]
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


if __name__ == '__main__':
    logging.basicConfig(filename="sample.log", level=logging.INFO)
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)

    video_capture = VideoStream(
        usePiCamera=args["picamera"] > 0,
        resolution=(640, 480),
        framerate=32
    ).start()

    time.sleep(2.0)

    fps = FPS().start()

    while True:  # fps._numFrames < 120
        frame = video_capture.read()
        t = time.time()
        ts_text = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
        position = (10, frame.shape[0] - 10)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        color = (0, 0, 255)

        cv2.putText(
            frame,
            ts_text,
            position,
            font_face,
            font_scale,
            color,
            1
        )

        output_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2BGR
        )

        out_tf_frame, output_dict = detect_objects(
            output_rgb,
            sess,
            detection_graph
        )

        output = serialize(output_dict)
        cv2.imshow('Video', out_tf_frame)

        if output:  # log results to sample.log
            print(output)
            logging.info(output)
        else:
            print("Nothing detected.")
        key = cv2.waitKey(33) & 0xFF
        fps.update()
        print('[INFO] elapsed time: {:.2f}'.format(time.time() - t))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))

    video_capture.stop()
    cv2.destroyAllWindows()
