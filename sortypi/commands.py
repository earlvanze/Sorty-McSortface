import argparse


def user_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        "-j",
        "--jetson",
        dest="use_jetsoncam",
        help="use Jetson on-board camera",
        action="store_true"
    )
    args.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index # of USB webcam (/dev/video?) [0]'
    )
    args.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=1280,
        help='Width of the frames in the video stream. [1280]'
    )
    args.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=720,
        help='Height of the frames in the video stream. [720]'
    )
    args.add_argument(
        "-fr",
        "--frame_rate",
        type=int,
        default=30,
        help="Framerate of video stream."
    )
    args.add_argument(
        "-p",
        "--picamera",
        type=int,
        default=0,
        help="whether or not the Raspberry Pi camera should be used"
    )
    args.add_argument(
        "--rtsp",
        dest="use_rtsp",
        help="use IP CAM (remember to also set --uri)",
        action="store_true"
    )
    args.add_argument(
        "--uri",
        dest="rtsp_uri",
        help="RTSP URI string, e.g. rtsp://192.168.1.64:554",
        default=None, type=str)
    args.add_argument(
        "--latency",
        dest="rtsp_latency",
        help="latency in ms for RTSP [200]",
        default=200, type=int)
    args.add_argument(
        "-d",
        "--debian",
        dest="debian",
        help="use Debian-based OS",
        action="store_true"
    )
    args.add_argument(
        "--noserial",
        dest="no_serial",
        help="disable serial for testing without Arduinos",
        action="store_true"
    )
    args.add_argument(
        "--show_help",
        dest="show_help",
        help="Show help screen",
        action="store_true"
    )
    args.add_argument(
        "--window_size",
        dest="window_size",
        help="Size of screen",
        type=str,
        default='normal',
    )
    args.add_argument(
        "--window_name",
        dest="window_name",
        help="Window name",
        type=str,
        default='normal',
    )
    return args.parse_args()


args = user_args()
