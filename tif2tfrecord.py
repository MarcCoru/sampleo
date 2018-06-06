import os
import argparse
import sys
from tfrecordutils import write, tif2tfrecord

def parse_args():

    description="""
    merges tif data to tfrecord.gz files.
    A tile is provided by a folder <tile> containing subfolders 'x' an 'y'.
    All images within these subfolders are merged to one tfrecord file
    """

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('tiffolder', type=str,
                        help="path to tif folder. requires files in <fld>/x/*.tif and <fld>/y/*.tif structure")

    parser.add_argument('tfrecord', type=str,
                        help="output tfrecord file. will be gzipped if it ends with .gz")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    tif2tfrecord(args.tiffolder, args.tfrecord)


#arr = np.array(im)


