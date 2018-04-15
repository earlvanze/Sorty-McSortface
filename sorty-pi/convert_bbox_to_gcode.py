# Measurements in gcode
IMAGE_WIDTH = 10
IMAGE_HEIGHT = 5

def convert_bbox_to_gcode(predictions):
    # [{'id': 0, 'score': 0.674207, 'class': 2, 'label': 'plastic',
    # 'bbox': [0.1543164, 0.3783059, 0.9762945, 0.6049226],
    # 'time': '2018-03-30T21:52:17:712133'}]

# TO-DO: Don't forget to loop through these predictions!
# TO-DO: Z-AXIS!

    bbox = predictions[0]['bbox']
    class_prediction = str(predictions[0]['class']).encode()
    ymin = float(bbox[0])
    xmin = float(bbox[1])
    ymax = float(bbox[2])
    xmax = float(bbox[3])
    print(ymin,xmin,ymax,xmax)
    # [ymin, xmin, ymax, xmax]
    # [0.089723945, 0.03985843, 0.92255473, 0.42330945]
    print(bbox)

    xMiddle = (xmax + xmin) / 2;
    yMiddle = (ymax + ymin) / 2;
    print(xMiddle, yMiddle)

    # Displacements from (0,0) of image
    xdisp = IMAGE_WIDTH * xMiddle
    ydisp = IMAGE_HEIGHT * yMiddle

    gcode = "F300 G90 \n"   # set motor speed in # of steps/minute
    gcode += "G1 X7 Y2 \n"  # move to offset (0,0) top left corner of camera image
    gcode += "G1 X{} Y{}".format(xdisp, ydisp)  # move to center of bbox

    # move to left bin or right bin based on class_prediction

    class_switcher = {
        1: "G1 X3",
        2: "G1 X19"
    }
    gcode += class_switcher.get(class_prediction, "")

    gcode += "G4 P1\n"      # Pause for s seconds (Ps)
    gcode += "G28 X0 Y0"    # move to home

    # reference test
#     gcode = "F300 G90 \n G28 Y0 \n G1 X9 Y3 \n G4 P1 \n X0 Y0"

    return gcode