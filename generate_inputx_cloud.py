"""
Import and  band and auxiliary data and export to a GCS bucket

acocac@gmail.com
"""

import os
import sys
import numpy as np
import tensorflow as tf
import argparse
from tensorflow.python.lib.io import file_io

parser = argparse.ArgumentParser(description='Import gee data by input dir')

parser.add_argument('-d','--dataset', type=str, required=True, help='Input path with tfrecord files from GEE')
parser.add_argument('-f','--filename', type=str, required=True, help='Input tfrecord file from GEE')
parser.add_argument('-y','--tyear', type=str, required=True, help='Target year')
parser.add_argument('-m','--maxobs', type=int, required=True, help='Maximum number of observations')
parser.add_argument('-k','--kernelksize', type=int, required=True, help='Kernel ksize')
parser.add_argument('-b','--maxblocks', type=int, required=True, help='Maximum number of blocks')
parser.add_argument('-e','--envdata', default=False, action="store_true" , help="If true only env data is joined")
parser.add_argument('-s','--GCS', type=str, required=True, help='The URL to the GCS bucket')

#source: http://blog.innodatalabs.com/the-newb-guide-to-google-cloud-machine-learning-engine-episode-one/ 
def read_bucket_tfrecord_srdata(filename, indir):
    
    # reads a tfRecord file from Google Storage
    tf_file = GCS + '/' + indir + '/' + filename

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

def read_bucket_tfrecord_envdata(filename, indir, doy):
    
    # reads a tfRecord file from Google Storage
    tf_file = GCS + '/' + indir + '/' + filename
        
    _bio01 = []
    _bio12 = []
    _srtm = []
    
    for serialized_example in tf.python_io.tf_record_iterator(os.path.join(tf_file), options=tf.python_io.TFRecordOptions(
                    compression_type=tf.python_io.TFRecordCompressionType.GZIP)):
        example = tf.train.Example()
        example.ParseFromString(serialized_example)
        bio01_data = example.features.feature['bio01'].float_list.value    
        bio12_data = example.features.feature['bio12'].float_list.value   
        srtm_data = example.features.feature['elevation'].float_list.value                    
        _bio01.append(bio01_data)
        _bio12.append(bio12_data)   
        _srtm.append(srtm_data) 
        
    #tile according to available DOY
    bio01 = np.tile(_bio01,(len(doy),1))
    bio12 = np.tile(_bio12,(len(doy),1))
    srtm = np.tile(_srtm,(len(doy),1))
    
    return bio01, bio12, srtm
        
def list2array(l, maxobs):
    """
    a function to convert list to array with padding
    """
    return [pad2D(np.array(frag).astype(int), maxobs) for frag in l]    
    
def pad1D(arr, maxobs):
    """
        Helper function padds 1D array up zo maxobs in direction axis=0
    """
    obs = arr.shape[0]
    pa =np.full((maxobs - obs,1), -1)
    if obs != maxobs-1:
        arr_out = np.concatenate((arr.astype(int), pa.squeeze()), axis=0)
    else: 
        arr_out = np.concatenate((arr.astype(int), pa[0]), axis=0)
    return arr_out

def pad2D(arr, maxobs):
    """
        Helper function padds 2D array up zo maxobs in direction axis=0
    """
    obs, i = arr.shape
    pa =np.full((maxobs - obs,arr.shape[1]), -1)
    return np.concatenate((arr, pa), axis=0)

def conv2_4D(array, ksize):
    """
        Helper function convert 2D array to 4D
    """    
    return array.reshape(array.shape[0], ksize, ksize, int(array.shape[1]/(ksize*ksize)))

def trans(array):
    z = np.asarray(array).transpose(1,2,0,3)
    return z

def split_2d(array, splits):
    x, y = splits
    return np.split(np.concatenate(np.split(array, y, axis=1)), x*y)

def retrans(array):
    z = np.asarray(array).transpose(2,0,1,3)
    return z

args = parser.parse_args()
infile = args.filename
dataset = args.dataset
tyear = args.tyear
ksize = args.kernelksize
maxblocks = args.maxblocks
maxobs = args.maxobs
dataset = args.dataset
envdata = args.envdata
GCS = args.GCS

# Sanity check on the GCS bucket URL.
# source: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/tools/gcs_test/python/gcs_smoke.py   
if not GCS or not GCS.startswith("gs://"):
    print("ERROR: Invalid GCS bucket URL: \"%s\"" % GCS)
    sys.exit(1)
    
# create outdirs
outdir = GCS + '/' + dataset + '/gz/' + str(int(ksize/maxblocks)) + '/' 
if envdata == True:
    outdir += "bio" + '/'
else:
    outdir += "nonbio" + '/'
outdir += "data" + tyear[2:]
print("Data to be written to: %s" % outdir)
    
indir_srdata = os.path.join(dataset,'raw',str(ksize),"sr_data","data"+ tyear[2:])
b1, b2, b3, b4, b5, b6, b7, b8, b8a, b9, b10, b11, b12, year, doy = read_bucket_tfrecord_srdata(infile, indir_srdata)
#
#b1_ = pad2D(np.array(b1).astype(int), maxobs)
#b2_ = pad2D(np.array(b2).astype(int), maxobs)
#b3_ = pad2D(np.array(b3).astype(int), maxobs)
#b4_ = pad2D(np.array(b4).astype(int), maxobs)
#b5_ = pad2D(np.array(b5).astype(int), maxobs)
#b6_ = pad2D(np.array(b6).astype(int), maxobs)
#b7_ = pad2D(np.array(b7).astype(int), maxobs)
#b8_ = pad2D(np.array(b8).astype(int), maxobs)
#b8a_ = pad2D(np.array(b8a).astype(int), maxobs)
#b9_ = pad2D(np.array(b9).astype(int), maxobs)
#b10_ = pad2D(np.array(b10).astype(int), maxobs)
#b11_ = pad2D(np.array(b11).astype(int), maxobs)
#b12_ = pad2D(np.array(b12).astype(int), maxobs)
#
#b1_ = b1_.reshape(b1_.shape[0], ksize, ksize, int(b1_.shape[1]/(ksize*ksize)))
#b2_ = b2_.reshape(b2_.shape[0], ksize, ksize, int(b2_.shape[1]/(ksize*ksize)))        
#b3_ = b3_.reshape(b3_.shape[0], ksize, ksize, int(b3_.shape[1]/(ksize*ksize)))
#b4_ = b4_.reshape(b4_.shape[0], ksize, ksize, int(b4_.shape[1]/(ksize*ksize)))
#b5_ = b5_.reshape(b5_.shape[0], ksize, ksize, int(b5_.shape[1]/(ksize*ksize)))     
#b6_ = b6_.reshape(b6_.shape[0], ksize, ksize, int(b6_.shape[1]/(ksize*ksize)))        
#b7_ = b7_.reshape(b7_.shape[0], ksize, ksize, int(b7_.shape[1]/(ksize*ksize))) 
#b8_ = b8_.reshape(b8_.shape[0], ksize, ksize, int(b8_.shape[1]/(ksize*ksize)))   
#b8a_ = b8a_.reshape(b8a_.shape[0], ksize, ksize, int(b8a_.shape[1]/(ksize*ksize)))
#b9_ = b9_.reshape(b9_.shape[0], ksize, ksize, int(b9_.shape[1]/(ksize*ksize)))        
#b10_ = b10_.reshape(b10_.shape[0], ksize, ksize, int(b10_.shape[1]/(ksize*ksize)))        
#b11_ = b11_.reshape(b11_.shape[0], ksize, ksize, int(b11_.shape[1]/(ksize*ksize)))        
#b12_ = b12_.reshape(b12_.shape[0], ksize, ksize, int(b12_.shape[1]/(ksize*ksize)))
#
#if envdata == False:
#    x_l = [b1_, b2_, b3_, b4_, b5_, b6_, b7_, b8_, b8a_, b9_, b10_, b11_, b12_]
#    
#else:
#    indir_aux = os.path.join(dataset,'raw',str(ksize),"env_data")
#
#    bio01, bio12, srtm  = read_bucket_tfrecord_envdata(infile, indir_aux, doy)
#    
#    bio01_ = pad2D(np.array(bio01).astype(int), maxobs)
#    bio12_ = pad2D(np.array(bio12).astype(int), maxobs)
#    srtm_ = pad2D(np.array(srtm).astype(int), maxobs)    
#    
#    bio01_ = bio01_.reshape(bio01_.shape[0], ksize, ksize, int(bio01_.shape[1]/(ksize*ksize)))
#    bio12_ = bio12_.reshape(bio12_.shape[0], ksize, ksize, int(bio12_.shape[1]/(ksize*ksize)))
#    srtm_ = srtm_.reshape(srtm_.shape[0], ksize, ksize, int(srtm_.shape[1]/(ksize*ksize)))
#    
#    x_l = [b1_, b2_, b3_, b4_, b5_, b6_, b7_, b8_, b8a_, b9_, b10_, b11_, b12_, bio01_, bio12_, srtm_]
#
#x_ = np.concatenate(x_l, axis = 3)        
#
#if year.shape[0] < maxobs:
#    year_ = pad1D(year, maxobs)
#else:
#    year_ = year
#
#if doy.shape[0] < maxobs:
#    doy_ = pad1D(doy, maxobs)  
#else:
#    doy_ = doy
#
##preprocessing big block to small blocks
#x_r = trans(x_)
#
#x_chunk_data = split_2d(x_r,(maxblocks,maxblocks))  
#
#all_blocks = range(0,maxblocks*maxblocks,1)
#
#if maxblocks == 10:
#    ignore = [9, 19, 29, 39, 49, 59, 69, 79, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99] #                
#    
#good_indices = list(set(all_blocks).difference(ignore))
#
#x_ = [retrans(x_chunk_data[i]) for i in good_indices]
#
#for t in range(0, len(x_), 1):
#
#    #write results with GZ format
#    filename_out = str(t) + '_' + infile  
#    
#    outdir_file = outdir + '/' + filename_out
#
#    writer = tf.python_io.TFRecordWriter(outdir_file, options=tf.python_io.TFRecordOptions(
#                compression_type=tf.python_io.TFRecordCompressionType.GZIP))
#
#    x=x_[t].astype(np.int64)
#    doy=doy_.astype(np.int64)
#    year=year_.astype(np.int64)
#
#        # Create a write feature
#    feature={
#        'x/data' : tf.train.Feature(bytes_list=tf.train.BytesList(value=[x.tobytes()])),
#        'x/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=x.shape)),
#        'dates/doy': tf.train.Feature(bytes_list=tf.train.BytesList(value=[doy.tobytes()])),
#        'dates/year': tf.train.Feature(bytes_list=tf.train.BytesList(value=[year.tobytes()])),
#        'dates/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=doy.shape))
#    }
#
#    example = tf.train.Example(features=tf.train.Features(feature=feature))
#
#    writer.write(example.SerializeToString())
#
#    writer.close()
#    sys.stdout.flush()  