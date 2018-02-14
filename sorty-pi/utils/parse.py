import tensorflow as tf
from protobuf_to_dict import protobuf_to_dict


def tf_record(record):
    output = {}
    file_num = 0
    for example in tf.python_io.tf_record_iterator(record):
        obj = tf.train.Example.FromString(example)
        output[file_num] = protobuf_to_dict(obj)
        file_num += 1
    return output
