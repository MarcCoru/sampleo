import tensorflow as tf
import os
from PIL import Image
import numpy as np
import sys

def write(filename, x, y):

    if filename.endswith(".gz"):    
        opt = tf.python_io.TFRecordOptions(tf.python_io.TFRecordCompressionType.GZIP)
    else:
        opt = tf.python_io.TFRecordOptions(tf.python_io.TFRecordCompressionType.NONE)

    writer = tf.python_io.TFRecordWriter(filename, options=opt)

    x=x.astype(np.int64)
    y=y.astype(np.int64)

    feature={
        'x/data' : tf.train.Feature(bytes_list=tf.train.BytesList(value=[x.tobytes()])),
        'x/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=x.shape)),
        'y/data': tf.train.Feature(bytes_list=tf.train.BytesList(value=[y.tobytes()])),
        'y/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=y.shape)),
    }

    example = tf.train.Example(features=tf.train.Features(feature=feature))

    writer.write(example.SerializeToString())

    writer.close()
    sys.stdout.flush()

def tif2tfrecord(tiffolder, tfrecord):

    # assumes that input images are located in <tile>/x and labels in <tile>/y
    # y labels can be also single image
    x_images = [os.path.join(tiffolder,'x',img) for img in os.listdir(os.path.join(tiffolder,'x'))]
    y_images = [os.path.join(tiffolder,'y',img) for img in os.listdir(os.path.join(tiffolder,'y'))]

    x_list = [np.array(Image.open(img)) for img in x_images]
    x = np.array(x_list)

    y_list = [np.array(Image.open(img)) for img in y_images]
    y = np.array(y_list)
    write(tfrecord, x, y)