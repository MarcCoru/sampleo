import tensorflow as tf
import os
from PIL import Image
import numpy as np
import sys

def read_tfrecord_srdata(filename):
    
    # reads a tfRecord file from Google Storage
    tf_file = filename
    print(tf_file)

    b1 = []
    b2 = []
    b3 = []
    b4 = []
    b5 = []
    b6 = []
    b7 = []
    b8 = []
    b8a = []
    b9 = []
    b10 = []
    b11 = []
    b12 = []
    year = []
    doy = []
    
    for serialized_example in tf.python_io.tf_record_iterator(tf_file, options=tf.python_io.TFRecordOptions(
                    compression_type=tf.python_io.TFRecordCompressionType.GZIP)):
        example = tf.train.Example()
        example.ParseFromString(serialized_example)
        b1_data = example.features.feature['B1'].float_list.value 
        b2_data = example.features.feature['B2'].float_list.value
        b3_data = example.features.feature['B3'].float_list.value 
        b4_data = example.features.feature['B4'].float_list.value 
        b5_data = example.features.feature['B5'].float_list.value 
        b6_data = example.features.feature['B6'].float_list.value 
        b7_data = example.features.feature['B7'].float_list.value 
        b8_data = example.features.feature['B8'].float_list.value 
        b8a_data = example.features.feature['B8A'].float_list.value 
        b9_data = example.features.feature['B9'].float_list.value 
        b10_data = example.features.feature['B10'].float_list.value 
        b11_data = example.features.feature['B11'].float_list.value 
        b12_data = example.features.feature['B12'].float_list.value 
        year_data = example.features.feature['year'].float_list.value
        doy_data = example.features.feature['DOY'].float_list.value     
        b1.append(b1_data)
        b2.append(b2_data)
        b3.append(b3_data)
        b4.append(b4_data)    
        b5.append(b5_data)
        b6.append(b6_data)      
        b7.append(b7_data)    
        b8.append(b8_data)
        b8a.append(b8a_data)    
        b9.append(b9_data)
        b10.append(b10_data)  
        b11.append(b11_data)
        b12.append(b12_data)
        year.append(year_data)
        doy.append(doy_data)
    
    year = np.mean(year, axis=1)  
    doy = np.mean(doy, axis=1) 

    return b1, b2, b3, b4, b5, b6, b7, b8, b8a, b9, b10, b11, b12, year, doy

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