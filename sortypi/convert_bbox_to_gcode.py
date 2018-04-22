# Measurements in gcode
IMAGE_WIDTH = 10
IMAGE_HEIGHT = 5


def get_center_xy(bbox):
    ymin, xmin, ymax, xmax = (float(bbox[i]) for i in range(4))
    x_midpoint = round(((xmax + xmin) / 2), 2)
    y_midpoint = round(((ymax + ymin) / 2), 2)
    return (x_midpoint, y_midpoint)


def calibrate(x_midpoint, y_midpoint, img):
    height, width = img.shape
    return width * x_midpoint, height * y_midpoint


def convert_bbox_to_gcode(predictions):
    # [{'id': 0, 'score': 0.674207, 'class': 2, 'label': 'plastic',
    # 'bbox': [0.1543164, 0.3783059, 0.9762945, 0.6049226],
    # 'time': '2018-03-30T21:52:17:712133'}]

    # TO-DO: Don't forget to loop through these predictions!
    # TO-DO: Z-AXIS!

    bbox = predictions[0]['bbox']
    class_prediction = predictions[0]['class']
    x_midpoint, y_midpoint = get_center_xy(bbox)
    x_disp, y_disp = calibrate(x_midpoint, y_midpoint, predictions['image'])
    motor_speed = "F200 G90\n"

    gcode = f"""F200 G90\n
                       G1 X9 Y2\n
                       G1 X{x_disp} Y{y_disp}\n
                       G4 P1\n
                       """

    class_switcher = {
        1: "G1 X{}\n".format(-xdisp),
        2: "G1 X19\n".format(xdisp + 10)
    }
    gcode += class_switcher.get(class_prediction, "")

    gcode += "G4 P1\n"      # Pause for s seconds (Ps)
    gcode += "G28 X0 Y0"    # move to home

    return gcode


predictions = [
    {
        'id': 0,
        'score': 0.6170466,
        'class': 2,
        'label': 'plastic',
        'bbox': [0.18688142, 0.07887441, 0.91263545, 0.5849223],
        'time': '2018-04-15T02:54:48:720555'
    }
]

if __name__ == "__main__":
    print(convert_bbox_to_gcode(predictions))


'''
[]
No recyclables detected. Probably trash.
2018-04-15 02:54:48.394 Python[77632:2219925] mMovieWriter.status: 3. Error: Cannot Save
[{'id': 0, 'score': 0.6170466, 'class': 2, 'label': 'plastic', 'bbox': [0.18688142, 0.07887441, 0.91263545, 0.5849223], 'time': '2018-04-15T02:54:48:720555'}]
still
[{'id': 0, 'score': 0.6170466, 'class': 2, 'label': 'plastic', 'bbox': [0.18688142, 0.07887441, 0.91263545, 0.5849223], 'time': '2018-04-15T02:54:48:720555'}]
0.186881422996521 0.07887440919876099 0.9126354455947876 0.5849223136901855
[0.18688142, 0.07887441, 0.91263545, 0.5849223]
0.33 0.55
F300 G90
G1 X7 Y2
G1 X3.3000000000000003 Y2.75
G4 P1,Pause
G28 X0 Y0, Move home
2018-04-15 02:54:48.727 Python[77632:2219925] mMovieWriter.status: 3. Error: Cannot Save
'''
