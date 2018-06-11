#from geotools import get_wms_credentials, build_wms_url
import geotools
import argparse
import os
import requests
from get_tile import get_tile
import geojson
import sys
import shapely.geometry
import ee
import time

#credentials = ee.ServiceAccountCredentials('docker@sampleo-206319.iam.gserviceaccount.com','/auth/google-service-account-key.json')
#ee.Initialize(credentials)

def parse_args():
        
    description="""
    Queries GEE and returns raster time series

    python get_srdatapy.py 'data/$id.geojson' -ts 2016-01-01 -te 2016-12-31 --collection "COPERNICUS/S2" -b 'sampleo' -f tiles/$id -r 10
    python get_srdatapy.py 'data/$id.geojson' -ts 2016-01-01 -te 2016-12-31 --collection "LANDSAT/LC08/C01/T1" -b 'sampleo' -f tiles/$id -r 30

    """

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--geojson', type=str,
                        help="jsonfile defining geojson location",
                        default='data/7777.geojson')              
    parser.add_argument('-ts','--startdate', type=str, 
                        default='2016-01-01', 
                        help='format YYYY-MM-DD')
    parser.add_argument('-te','--enddate', type=str, 
                        default='2016-12-31',
                        help='format YYYY-MM-DD')
    parser.add_argument('-b','--bucket', 
                        type=str, default="sampleo", 
                        help='folder name')
    parser.add_argument('-f','--folder', 
                        type=str, default="tiles/7777", 
                        help='folder name')
    parser.add_argument('-c','--collection', 
                        type=str, default='COPERNICUS/S2', 
                        help='GEE id as collection e.g., COPERNICUS/S2')
    parser.add_argument('-r','--resolution', 
                        type=int, default=10, 
                        help='ground resolution')
    #parser.add_argument('-s','--kernelsize', 
    #                    type=int, default=240, 
    #                    help='kernel size')

    return parser.parse_args()

def main(args):
    


    ee.Initialize()

    def kernelnb(img):
        return img.neighborhoodToArray(kernel).sampleRegions(collection= tile_point)

    def adddata(img):
        ## Get the date, convert to integer
        year = ee.Image.constant(img.date().get('year').add(0))
        day = ee.Image.constant(img.date().getRelative('day', 'year').add(1))
        img = img.addBands(day.rename('DOY').int()).addBands(year.rename('year').int()) 
        return img
        
    # query random tile geometry
    #wkt, zone, row, name = get_tile(args.sql, tilesize=240, decimal=-2, conn=None)

    with open(args.geojson) as f:
        gj = geojson.load(f)
    pt_list = gj['features'][0]["geometry"]["coordinates"][0]
    geom = ee.Geometry.Polygon(pt_list)

    # read basename name from geojson file
    name = os.path.basename(args.geojson).replace(".geojson","")

    # filter collection 
    collection = ee.ImageCollection(args.collection).filterDate(args.startdate, args.enddate).filterBounds(geom)

    # filter by first list of unique UTM
    # source https://groups.google.com/forum/#!search/granules$20sentinel/google-earth-engine-developers/ziFfkMya8js/436BpaoLBwAJ

    if args.collection == 'COPERNICUS/S2':

        utm_ids = collection.distinct(["MGRS_TILE"]).aggregate_array("MGRS_TILE")
        utm_ids = utm_ids.getInfo()
        collection = collection.filterMetadata('MGRS_TILE', 'starts_with', utm_ids[0])
        print("{name} tile contains {info} S2TOA images".format(name=name, info=collection.size().getInfo()))

        if args.resolution == 10:
            bands = ['B2','B3','B4','B8']
        elif args.resolution == 20:
            bands = ['B5','B6','B7','B8A','B11','B12']
        elif args.resolution == 60:
            bands = ['B1','B9','B10']
        else:
            raise ValueError("{} is not a valid resolution for {}. please insert 10, 20 or 60m".format(args.resolution, args.collection))
        ## approach: export TFrecords using neighborhoodToArray - return full timeseries by band (fast)
        # bands = ['B2','B3','B4','B8', #10m
                # 'B5','B6','B7','B8A','B11','B12', #02m
                # 'B1','B9','B10'] #60m
    else:
        raise ValueError("{} is Invalid collection did you mean COPERNICUS/S2".format(args.collection))

    #select target bands
    collection = collection.select(bands)

    #add date and year
    collection = collection.map(adddata)
    
    #get centroid polygon
    tile_point = ee.Feature(ee.Geometry.Point(geom.centroid().coordinates()))

    ##create kernel

    # convert over shapely geometry to wkt string
    geom = shapely.geometry.Polygon(pt_list)
    geom_utm, zone, row = geotools.wgs2utm(geom)
    xmin, ymin, xmax, ymax = geom_utm.bounds
    sizex = int(round((xmax-xmin)/args.resolution))
    sizey = int(round((ymax-ymin)/args.resolution))

    #size = args.kernelsize
    weights = ee.List.repeat(ee.List.repeat(1, sizex), sizey)
    kernel = ee.Kernel.fixed(sizex, sizey, weights)

    ##Sample pixels in the ImageCollection at these random points
    values = collection.map(kernelnb).flatten()

    #assert(values.size().getInfo() == collection.size().getInfo())

    #gs://sampleo/tiles/$id/S2raster10m.tfrecord
    # S2raster10m.tfrecord
    collection_str=args.collection.replace("/","")
    outfolder="{folder}/{collection}_{resolution}m_".format(folder=args.folder, collection=collection_str, resolution=args.resolution)
    #args.folder + '/raw/' + str(size) + '/sr_data/data' + args.startdate.split('-')[0][2:] + '/' + name
    bucket=args.bucket

    task= ee.batch.Export.table.toCloudStorage(
            collection= values,
            description= name,
            folder= None,
            fileNamePrefix= outfolder,
            fileFormat= 'TFRecord',
            bucket=bucket)
            
    try:
        task.start()
        print("Processing year: {outfolder} and block id {name} with size {sizex},{sizey}".format(outfolder=outfolder, name=name, sizex=sizex, sizey=sizey))
    #    time.sleep(15)
        print(task.status())
    except Exception as str_error:
        print("Error in year: {outfolder} and block id {name} with size {sizex},{sizey}".format(outfolder=outfolder, name=name, sizex=sizex, sizey=sizey))
    #   print("Error in year: ", args.folder,' and block id: ', name,' with size: ', size)
        print("Error type equal to ", str_error)

if __name__ == '__main__':
    args = parse_args()
    main(args)