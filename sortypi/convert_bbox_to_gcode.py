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
    class_prediction = predictions[0]['class']
    ymin = float(bbox[0])
    xmin = float(bbox[1])
    ymax = float(bbox[2])
    xmax = float(bbox[3])
    print(ymin,xmin,ymax,xmax)
    # [ymin, xmin, ymax, xmax]
    # [0.089723945, 0.03985843, 0.92255473, 0.42330945]
    print(bbox)

    xMiddle = round(((xmax + xmin) / 2), 2)
    yMiddle = round(((ymax + ymin) / 2), 2)
    print(xMiddle, yMiddle)

    # Displacements from (0,0) of image
    xdisp = IMAGE_WIDTH * xMiddle
    ydisp = IMAGE_HEIGHT * yMiddle

    gcode = "F200 G90\n"   # set motor speed in # of steps/minute
    gcode += "G1 X9 Y2\n"  # move to offset (0,0) top left corner of camera image
    gcode += "G1 X{} Y{}\n".format(xdisp, ydisp)  # move to center of bbox
    gcode += "G4 P1\n"      # Pause for s seconds (Ps)

    # move to left bin or right bin based on class_prediction

    class_switcher = {
        1: "G1 X{}\n".format(-xdisp),
        2: "G1 X19\n".format(xdisp+10)
    }
    gcode += class_switcher.get(class_prediction, "")

    gcode += "G4 P1\n"      # Pause for s seconds (Ps)
    gcode += "G28 X0 Y0"    # move to home

    # reference test
#     gcode = "F300 G90 \n G28 Y0 \n G1 X9 Y3 \n G4 P1 \n X0 Y0"

    return gcode

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
G4 P1
G28 X0 Y0
2018-04-15 02:54:48.727 Python[77632:2219925] mMovieWriter.status: 3. Error: Cannot Save
'''
