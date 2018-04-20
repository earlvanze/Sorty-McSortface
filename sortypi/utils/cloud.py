import json
import boto3
import configparser
import base64


def base64_encode_image(img):
    img_shape = img.shape
    img_dtype = img.dtype
    base64_bytes = base64.b64encode(img)
    base64_string = base64_bytes.decode('utf-8')
    return img_shape, img_dtype, base64_string


def serialize_json_for_s3(data):
    output = {}
    for _, pred in enumerate(data):
        record = {}
        record['bbox'] = [str(i) for i in pred['bbox']]
        record['id'] = str(pred['id'])
        record['class'] = str(pred['class'])
        record['score'] = str(pred['score'])
        output['prediction'] = record
    return output


def write_to_S3(session, predictions, img, bucket, path):
    output = serialize_json_for_s3(predictions)
    print("predictions", predictions)
    img_shape, img_dtype, base64_string = base64_encode_image(img)
    output['image'] = base64_string
    output['img_dtype'] = str(img_dtype)
    output['img_shape'] = str(img_shape)
    s3 = session.resource('s3')
    obj = s3.Object(bucket, path)
    obj.put(Body=json.dumps(output))


def connect_to_aws():
    config = configparser.ConfigParser()
    config.read('config.ini')
    sess = boto3.Session(
        aws_access_key_id=config['AWS']['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS']['AWS_SECRET_ACCESS_KEY'],
    )
    return sess
