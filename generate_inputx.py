"""
TODO: Fix bug nb and script results
Import and  band and label for target pixel and neighbours for list of fracs

Example invocation::

    python MODIS/0_import_geedata.py
        -i=/home/xx/
        -o=/home/xx/
        -n 30
        
acocac@gmail.com
"""
import os
import sys
import numpy as np
import time
import tensorflow as tf
import argparse
import joblib

parser = argparse.ArgumentParser(description='Import gee data by input dir')

parser.add_argument('-i','--indir', type=str, required=True, help='Input directory with tfrecords from GEE by tile')
parser.add_argument('-o','--outdir', type=str, required=True, help='Output directory')
parser.add_argument('-y','--tyear', type=str, required=True, help='Target year')
parser.add_argument('-m','--maxobs', type=int, required=True, help='Maximum number of observations')
parser.add_argument('-k','--kernelsize', type=int, required=True, help='Kernel size')
parser.add_argument('-b','--maxblocks', type=int, required=True, help='Maximum number of blocks')
parser.add_argument('-n','--nworkers', type=int, default=None, help='Number of workers (by default all)')
parser.add_argument('--noconfirm', action='store_true', help='Skip confirmation')

def confirm(prompt=None, resp=False):
    """
    Prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    """
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print ('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
        
def list2array(l, n_max_obs):
    """
    a function to convert list to array with padding
    """
    return [pad2D(np.array(frag).astype(int), n_max_obs) for frag in l]    
    
def pad1D(arr, n_max_obs):
    """
        Helper function padds 1D array up zo n_max_obs in direction axis=0
    """
    obs = arr.shape[0]
    pa =np.full((n_max_obs - obs,1), -1)
    if obs != n_max_obs-1:
        arr_out = np.concatenate((arr.astype(int), pa.squeeze()), axis=0)
    else: 
        arr_out = np.concatenate((arr.astype(int), pa[0]), axis=0)
    return arr_out

def pad2D(arr, n_max_obs):
    """
        Helper function padds 2D array up zo n_max_obs in direction axis=0
    """
    obs, i = arr.shape
    pa =np.full((n_max_obs - obs,arr.shape[1]), -1)
    return np.concatenate((arr, pa), axis=0)

def conv2_4D(array, size):
    """
        Helper function convert 2D array to 4D
    """    
    return array.reshape(array.shape[0], size, size, int(array.shape[1]/(size*size)))

def trans(array):
    z = np.asarray(array).transpose(1,2,0,3)
    return z

def split_2d(array, splits):
    x, y = splits
    return np.split(np.concatenate(np.split(array, y, axis=1)), x*y)

def retrans(array):
    z = np.asarray(array).transpose(2,0,1,3)
    return z

def import_data(fn, size, maxblocks, exportblocks, n_max_obs, outdir, dataset, indir, tyear):
    
    indir_data = os.path.join(indir,str(size),"sr_data","data"+ tyear[2:])

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

    for serialized_example in tf.python_io.tf_record_iterator(os.path.join(indir_data,fn), options=tf.python_io.TFRecordOptions(
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
    
    _bio01 = []
    _bio12 = []
    _srtm = []
    
    indir_aux = os.path.join(indir,str(size),"env_data")

    for serialized_example in tf.python_io.tf_record_iterator(os.path.join(indir_aux,fn), options=tf.python_io.TFRecordOptions(
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

    if len(year) <= n_max_obs:

        b1_ = pad2D(np.array(b1).astype(int), n_max_obs)
        b2_ = pad2D(np.array(b2).astype(int), n_max_obs)
        b3_ = pad2D(np.array(b3).astype(int), n_max_obs)
        b4_ = pad2D(np.array(b4).astype(int), n_max_obs)
        b5_ = pad2D(np.array(b5).astype(int), n_max_obs)
        b6_ = pad2D(np.array(b6).astype(int), n_max_obs)
        b7_ = pad2D(np.array(b7).astype(int), n_max_obs)
        b8_ = pad2D(np.array(b8).astype(int), n_max_obs)
        b8a_ = pad2D(np.array(b8a).astype(int), n_max_obs)
        b9_ = pad2D(np.array(b9).astype(int), n_max_obs)
        b10_ = pad2D(np.array(b10).astype(int), n_max_obs)
        b11_ = pad2D(np.array(b11).astype(int), n_max_obs)
        b12_ = pad2D(np.array(b12).astype(int), n_max_obs)
        bio01_ = pad2D(np.array(bio01).astype(int), n_max_obs)
        bio12_ = pad2D(np.array(bio12).astype(int), n_max_obs)
        srtm_ = pad2D(np.array(srtm).astype(int), n_max_obs)

#TODO
#        blue_ = blue_.reshape(blue_.shape[0], size, size, int(blue_.shape[1]/(size*size)))
#        green_ = green_.reshape(green_.shape[0], size, size, int(green_.shape[1]/(size*size)))
#        red_ = red_.reshape(red_.shape[0], size, size, int(red_.shape[1]/(size*size)))
#        nir_ = nir_.reshape(nir_.shape[0], size, size, int(nir_.shape[1]/(size*size)))
#        swir1_ = swir1_.reshape(swir1_.shape[0], size, size, int(swir1_.shape[1]/(size*size)))
#        swir2_ = swir2_.reshape(swir2_.shape[0], size, size, int(swir2_.shape[1]/(size*size)))
#        swir3_ = swir3_.reshape(swir3_.shape[0], size, size, int(swir3_.shape[1]/(size*size)))
#        bio01_ = bio01_.reshape(bio01_.shape[0], size, size, int(bio01_.shape[1]/(size*size)))
#        bio12_ = bio12_.reshape(bio12_.shape[0], size, size, int(bio12_.shape[1]/(size*size)))
#        srtm_ = srtm_.reshape(srtm_.shape[0], size, size, int(srtm_.shape[1]/(size*size)))
#        
#        x500_l = [blue_, green_, red_, nir_, swir1_, swir2_, swir3_]
#        x500_ = np.concatenate(x500_l, axis = 3)        
#
#        labels = pad2D(np.array(labels),n_max_obs)  
#        
#        if dataset == 'ESA_6classes':
#            labels = aggregate_ESA_6classes(labels)
#
#        elif dataset == 'MODIS_6classes':
#            labels = aggregate_MODIS_6classes(labels)
#
#        elif dataset == 'MODIS_5classes':
#            labels = aggregate_MODIS_5classes(labels)
#
#        elif dataset == 'MODIS_allnonforest':
#            labels = MODIS_allnonforest(labels)
#
#        elif dataset == 'MODIS_savanna':
#            labels = MODIS_savanna(labels)
#
#        elif dataset == 'MODIS_savcrop':
#            labels = MODIS_savcrop(labels)
#            
#        labels_ = conv2_4D(labels, size) ##transform for desired format    
#        #labels_ = labels_[:, :, :, 0]    
#
#        if year.shape[0] < n_max_obs:
#            year_ = pad1D(year, n_max_obs)
#        else:
#            year_ = year
#
#        if doy.shape[0] < n_max_obs:
#            doy_ = pad1D(doy, n_max_obs)  
#        else:
#            doy_ = doy
#        
#        #preprocessing big block to small blocks
#        x500_r = trans(x500_)
#        labels_r = trans(labels_)
#        
#        x500_chunk_data = split_2d(x500_r,(maxblocks,maxblocks))  
#        labels_chunk_data = split_2d(labels_r,(maxblocks,maxblocks))  
#    
#        all_blocks = range(0,maxblocks*maxblocks,1)
#        
#        if exportblocks == "train":
#
#            if maxblocks == 9:
#                ignore = [8, 17, 26, 35, 44, 53, 62, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80] #
#            elif maxblocks == 3:
#                ignore = [4, 9, 14, 19, 20, 21, 22, 23, 24]
#                
#            good_indices = list(set(all_blocks).difference(ignore))
#
#            x500_ = [retrans(x500_chunk_data[i]) for i in good_indices]
#            labels_ = [retrans(labels_chunk_data[i]) for i in good_indices]
#
#        elif exportblocks == "eval":
#
#            x500_ = [retrans(x500_chunk_data[i]) for i in all_blocks]
#            labels_ = [retrans(labels_chunk_data[i]) for i in all_blocks]
#        
#        for t in range(0, len(x500_), 1):
#
#            #write results with GZ format
#            filename_out = str(t) + "_" + fn  
#            
#            outdir_file = os.path.join(outdir,filename_out)
#
#            writer = tf.python_io.TFRecordWriter(outdir_file, options=tf.python_io.TFRecordOptions(
#                        compression_type=tf.python_io.TFRecordCompressionType.GZIP))
#
#            x500=x500_[t].astype(np.int64)
#            doy=doy_.astype(np.int64)
#            year=year_.astype(np.int64)
#            labels = labels_[t][:,:,:,0].astype(np.int64)
#
#                # Create a write feature
#            feature={
#                'x500/data' : tf.train.Feature(bytes_list=tf.train.BytesList(value=[x500.tobytes()])),
#                'x500/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=x500.shape)),
#                'labels/data': tf.train.Feature(bytes_list=tf.train.BytesList(value=[labels.tobytes()])),
#                'labels/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=labels.shape)),
#                'dates/doy': tf.train.Feature(bytes_list=tf.train.BytesList(value=[doy.tobytes()])),
#                'dates/year': tf.train.Feature(bytes_list=tf.train.BytesList(value=[year.tobytes()])),
#                'dates/shape': tf.train.Feature(int64_list=tf.train.Int64List(value=doy.shape))
#            }
#
#            example = tf.train.Example(features=tf.train.Features(feature=feature))
#
#            writer.write(example.SerializeToString())
#
#            writer.close()
#            sys.stdout.flush()  
#            
#            #export class
#            labels_class = np.max(labels,axis=0).flatten()
#            tile_id = os.path.splitext((os.path.basename(fn)))[0]
#            filename_out = str(t) + "_" + tile_id  
#            np.save(class_path + "/" + filename_out + ".npy", labels_class)
#
#    else:
#        tile_id = os.path.splitext((os.path.basename(fn)))[0]
#        z = 0
#        np.save(log_path_bad + "/" + tile_id + ".npy", z)
#
#if __name__ == '__main__':
#    args = parser.parse_args()
#    indir = args.indir
#    outdir = args.outdir
#    tyear = args.tyear
#    ksize = args.kernelsize
#    maxblocks = args.maxblocks
#    exportblocks = args.exportblocks
#    maxobs = args.maxobs
#    nworkers = args.nworkers
#    dataset = args.dataset
#    preprocessing = args.preprocessing
#    
#    if preprocessing == True:
#        outdir = os.path.join(outdir,str(int(ksize/maxblocks)),dataset + "_cleaned","data" + tyear[2:])
#    else:
#        outdir = os.path.join(outdir,str(int(ksize/maxblocks)),dataset + "_all","data" + tyear[2:])
#        
#    if not os.path.exists(outdir):
#        os.makedirs(outdir)    
#
#    indir_data = os.path.join(indir,str(ksize),"sr_data","data"+ tyear[2:])
#
#    tiles = [file for r,d,f in os.walk(os.path.join(indir_data)) for file in f]
#
#    if len(tiles) == 0:
#        print ('No tiles to process... Terminating')
#        sys.exit(0)
#   
#    print ()
#    print ('Will process the following :')
#    print ('Number of tiles : %d' % len(tiles))
#    print ('nworkers : %s' % str(nworkers))
#    print ('Input data dir : %s' % str(indir_data))
#    print ('Output data dir : %s' % str(outdir))
#    print ()
#
#    if not args.noconfirm:
#        if not confirm(prompt='Proceed?', resp=True):
#            sys.exit(0)
#            
#    root_dir = os.path.dirname(outdir)
#    dirname = os.path.basename(outdir)
#
#    log_path_bad = os.path.join(root_dir,'failedtiles',dirname)
#    if not os.path.exists(log_path_bad):
#        os.makedirs(log_path_bad)
#
#    class_path = os.path.join(root_dir,'classes',dirname)
#    if not os.path.exists(class_path):
#        os.makedirs(class_path)
#        
#    # Launch the process
#    if nworkers is not None and nworkers > 1:
#        print ('Using joblib.Parallel with nworkers=%d' % nworkers)
#        joblib.Parallel(n_jobs=nworkers)(
#            joblib.delayed(import_data)(tile, ksize, maxblocks, exportblocks, maxobs, outdir, log_path_bad, class_path, dataset, indir, tyear, preprocessing)
#            for tile in tiles
#        )
#        
#    else:
#        for tile in tiles:
#            import_data(tile, ksize, maxblocks, exportblocks, maxobs, outdir, log_path_bad, class_path, dataset, indir, tyear, preprocessing)