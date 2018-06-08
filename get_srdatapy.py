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

ee.Initialize()
                        
"""
queries a postgres database for a random tile within an area of interest (aoi)
and returns a representation
"""

description="""
queries a postgres database for a random tile within an area of interest (aoi).
The aoi table can be defined by --sql
The database connection requires following environment variables:
'PG_HOST', 'PG_USER', 'PG_PASS', 'PG_DATABASE' and 'PG_PORT')
"""

parser = argparse.ArgumentParser(description=description)

parser.add_argument('geojson', type=str,
                    default="jsonfile defining geojson location",
                    help="")              
parser.add_argument('-ts','--startdate', type=str, 
                    default=None, 
                    help='format YYYY-MM-DD')
parser.add_argument('-te','--enddate', type=str, 
                    default=None,
                    help='format YYYY-MM-DD')
parser.add_argument('-f','--folder', 
                    type=str, default=None, 
                    help='folder name')
parser.add_argument('-s','--kernelsize', 
                    type=int, default=240, 
                    help='kernel size')

args = parser.parse_args()

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

# convert point list (wgs) to shapely geometry object
#geom = shapely.geometry.Polygon(pt_list)
geom = ee.Geometry.Polygon(pt_list)

# read basename name from geojson file
name = os.path.basename(args.geojson).replace(".geojson","")

# filter collection 
collection = ee.ImageCollection('COPERNICUS/S2').filterDate(args.startdate, args.enddate).filterBounds(geom)

# filter by first list of unique UTM
# source https://groups.google.com/forum/#!search/granules$20sentinel/google-earth-engine-developers/ziFfkMya8js/436BpaoLBwAJ
utm_ids = collection.distinct(["MGRS_TILE"]).aggregate_array("MGRS_TILE")
utm_ids = utm_ids.getInfo()
collection = collection.filterMetadata('MGRS_TILE', 'starts_with', utm_ids[0])
print(name + ' tile contains: ' + str(collection.size().getInfo()) + ' S2TOA images')

## approach: export TFrecords using neighborhoodToArray - return full timeseries by band (fast)
bands = ['B2','B3','B4','B8', #10m
          'B5','B6','B7','B8A','B11','B12', #02m
          'B1','B9','B10'] #60m
          
#select target bands
collection = collection.select(bands)

#add date and year
collection = collection.map(adddata)
 
 #get centroid polygon
tile_point = ee.Feature(ee.Geometry.Point(geom.centroid().coordinates()))

##create kernel
size = args.kernelsize
weights = ee.List.repeat(ee.List.repeat(1, size), size)
kernel = ee.Kernel.fixed(size, size, weights)

##Sample pixels in the ImageCollection at these random points
values = collection.map(kernelnb).flatten()

assert(values.size().getInfo() == collection.size().getInfo())

task= ee.batch.Export.table.toCloudStorage(
        collection= values,
        description= name,
        folder= None,
        fileNamePrefix= args.folder + '/raw/' + str(size) + '/sr_data/data' + args.startdate.split('-')[0][2:] + '/' + name,
        fileFormat= 'TFRecord',
        bucket='sampleo')
        
try:
    task.start()
    print("Processing year: ", args.folder,' and block id: ', name,' with size: ', size)
#    time.sleep(15)
    print(task.status())
except Exception as str_error:
    print("Error in year: ", args.folder,' and block id: ', name,' with size: ', size)
    print("Error type equal to ", str_error)