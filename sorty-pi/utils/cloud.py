import json


def serialize_json_for_s3(data):
    output = []
    print(data)
    for idx, pred in enumerate(data):
        record = {}
        record['bbox'] = [str(i) for i in pred['bbox']]
        record['id'] = str(pred['id'])
        record['class'] = str(pred['class'])
        record['score'] = str(pred['score'])
        output.append(record)
    return output


def write_to_S3(session, data, bucket, path):
    output = serialize_json_for_s3(data)
    print("data", data)
    print("output", output)
    s3 = session.resource('s3')
    obj = s3.Object(bucket, path)
    obj.put(Body=json.dumps(output))
