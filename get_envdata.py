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
    img = img.addBands(bio01).addBands(bio12)
    return img
    
def downscale(img):
  
  ##Load a S210m image.
    S210mband = ee.Image(ee.ImageCollection('COPERNICUS/S2').first()).select('B2')
  
    ##Get information about the S2 band projection.
    S210mprojection = S210mband.projection();

    img_downscale = img.reduceResolution(
        reducer= ee.Reducer.mode(),
        maxPixels= 65535
      ).reproject(
        crs= S210mprojection
      )

    return(img_downscale)
    
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

# env data
bio = ee.Image('WORLDCLIM/V1/BIO')
srtm = ee.Image('CGIAR/SRTM90_V4')

bio01 = bio.select('bio01')
bio12 = bio.select('bio12')

# downscale env data
bio01 = downscale(bio01).unmask(0)
bio12 = downscale(bio12).unmask(0)
srtm = downscale(srtm).unmask(0)

## merge env data
envdata = adddata(srtm)

 #get centroid polygon
tile_point = ee.Feature(ee.Geometry.Point(geom.centroid().coordinates()))

##create kernel
size = args.kernelsize
weights = ee.List.repeat(ee.List.repeat(1, size), size)
kernel = ee.Kernel.fixed(size, size, weights)

##Sample pixels in the ImageCollection at these random points
values = kernelnb(envdata)

task= ee.batch.Export.table.toCloudStorage(
        collection= values,
        description= name,
        folder= None,
        fileNamePrefix= args.folder + '/raw/' + str(size) + '/env_data/' + name,
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