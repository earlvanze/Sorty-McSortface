import cv2
from utils.app_utils import VideoStream


def stream(args):
    vs = VideoStream(
        usePiCamera=args.picamera > 0,
        resolution=(args.width, args.height),
        framerate=args.frame_rate,
        use_jetsoncam=args.use_jetsoncam,
        src=args.video_source
    )
    return vs


def show(frame):
    bgr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow('Video', bgr_frame)


def full_screen(args):
    cv2.setWindowProperty(
        args.window_name,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN,
    )


def normal_screen(args):
    cv2.setWindowProperty(
        args.window_name,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_NORMAL,
    )


def help_text(frame):
    text = "'Esc' or 'Q' to Quit, 'H' to Toggle Help, 'F' to Toggle Fullscreen"
    font = cv2.FONT_HERSHEY_PLAIN
    cv2.putText(
        frame,
        text,
        (11, 20),
        font,
        1.0,
        (32, 32, 32),
        4,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        text,
        (10, 20),
        font,
        1.0,
        (240, 240, 240),
        1,
        cv2.LINE_AA
    )
