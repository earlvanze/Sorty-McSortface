config = {
    'default': {
        'txt': dt.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        'pos':}

}


def place_text(frame):
    ts_text =
    position = (10, frame.shape[0] - 10)
    ft_face = cv2.FONT_HERSHEY_SIMPLEX
    ft_scale = 0.35
    color = (0, 0, 255)
    # put information text in the lower bottom corner
    cv2.putText(frame, ts_text, position, ft_face, ft_scale, color, 1)
