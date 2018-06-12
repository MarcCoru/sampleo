import os, sys
import unittest
import numpy as np
import tempfile
import tensorflow as tf

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import tfrecordutils

class TestTfrecordutils(unittest.TestCase):

    def test_read_tfrecord_srdata(self):
        filename="tmp/7777/COPERNICUSS2_60m_ee_export.tfrecord.gz"

        tfrecordutils.read_tfrecord_srdata(filename)

    # def test_load_dataset(self):
    #     filename="tmp/7777/COPERNICUSS2_60m_ee_export.tfrecord.gz"

    #     feature_format = {
    #         'label': tf.FixedLenFeature((), tf.float32),
    #         'image': tf.FixedLenFeature((40, 40), tf.float32),
    #     }

    #     reader = tf.TFRecordReader()
    #     filename_queue = tf.train.string_input_producer([filename], num_epochs=None)
    #     f, serialized_example = reader.read(filename_queue)

    #     example = tf.parse_single_example(serialized_example, feature_format)
        
        #tfrecordutils.parser(filenames)example = tf.parse_single_example(serialized_example, feature_format)

    # def test_read_gee_tfrecord(self):

    #     filename="tmp/7777/COPERNICUSS2_60m_ee_export.tfrecord.gz"

    #     ds = tfrecordutils.read_gee_tfrecord(filename)

    #     self.fail("fail")

    def test_write(self):

        x = (np.random.rand(6,48,48,6)*1e3).astype(np.int64)
        y = (np.random.rand(24,24,1)*255).astype(np.int64)
    
        try:
            
            try:
                tfrecordutils.write("tmptestfile.tfrecord",x,y)
            finally:
                os.remove("tmptestfile.tfrecord")
            
            try:
                tfrecordutils.write("tmptestfile.tfrecord.gz",x,y)
            finally:
                os.remove("tmptestfile.tfrecord.gz")
            

        except:
            self.fail("Could not write tfrecord from random data")

if __name__ == '__main__':
    unittest.main()
