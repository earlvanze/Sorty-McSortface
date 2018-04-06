def convert_bbox_to_gcode(predictions):
    # [{'id': 0, 'score': 0.674207, 'class': 2, 'label': 'plastic',
    # 'bbox': [0.1543164, 0.3783059, 0.9762945, 0.6049226],
    # 'time': '2018-03-30T21:52:17:712133'}]
    bbox = predictions[0]['bbox']
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
    

    gcode = "F300 G90 \n G28 Y0 \n G1 X9 Y3 \n G4 P1 \n X0 Y0"

    return gcode
