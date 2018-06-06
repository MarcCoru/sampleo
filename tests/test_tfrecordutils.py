import os, sys
import unittest
import numpy as np
import tempfile

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import tfrecordutils

class TestTfrecordutils(unittest.TestCase):

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
