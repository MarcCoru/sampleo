import tensorflow as tf
import sys

"""
usage:

python print_tfrecord.py 00000.tfrecord
"""

tfrecord=sys.argv[1]

for example in tf.python_io.tf_record_iterator(tfrecord):
	print(tf.train.Example.FromString(example))