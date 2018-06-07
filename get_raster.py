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

args = parser.parse_args()

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

y = '2016'
tS = y + '-01-01'
tE = y + '-12-31'

# filter collection 
collection = ee.ImageCollection('COPERNICUS/S2').filterDate(tS, tE).filterBounds(geom)

# filter by first list of unique UTM
# source https://groups.google.com/forum/#!search/granules$20sentinel/google-earth-engine-developers/ziFfkMya8js/436BpaoLBwAJ
utm_ids = collection.distinct(["MGRS_TILE"]).aggregate_array("MGRS_TILE")
utm_ids = utm_ids.getInfo()
collection = collection.filterMetadata('MGRS_TILE', 'starts_with', utm_ids[0])
print(name + ' tile contains: ' + str(collection.size().getInfo()) + ' S2TOA images')

### approach 1: export by date(slow)
### source: https://groups.google.com/forum/#!searchin/google-earth-engine-developers/imagecollection|sort:date/google-earth-engine-developers/XP_gsnwI8cI/-N1CVryYCwAJ
### https://groups.google.com/forum/#!searchin/google-earth-engine-developers/distinct$20python%7Csort:date/google-earth-engine-developers/F34-_mIksZo/FhH9Nv0VCgAJ
### create export tasks
images = collection.limit(2)
images = collection

_size = images.size().getInfo()

img = images.distinct('system:time_start')
        
img_list = img.toList(img.size(), 0)

folder = "raster_240_bydate"

for index in range(0, _size-1):

    img = ee.Image(img_list.get(int(index)))

#    doy = ee.String(img.date().getRelative('day', 'year').add(1)).getInfo()                                  
#    print(doy)
                          
    date = ee.String(img.date().format('YYYY-MM-dd')).getInfo()
    
    task = 'image' + str(index)
    
    task = ee.batch.Export.image.toCloudStorage(
        image=img,
        description='',
        fileFormat='GeoTIFF',
        bucket='sampleo',
        fileNamePrefix=folder + '/' + name + "_" + str(date),
        scale=10,
        region=geom.getInfo()['coordinates']
        )

    # task = ee.batch.Export.image.toCloudStorage(image = img, description=name + "_" + str(date), 
    #                                             fileNamePrefix= folder + '/' + name + "_" + str(date),
    #                               scale = 10, fileFormat= 'TFRecord', region = geom.getInfo()['coordinates'], bucket='sampleo',
    #                               formatOptions = {'patchDimensions': [24, 24], 
    #                               'collapseBands': False, 'compressed': True})

    task.start() 
    print('Done.', task.status())

    time.sleep(1)

    state=task.status()['state'] 
    while state in ['READY', 'RUNNING']:
        print(state + '...')
        state = task.status()['state']
#        time.sleep(1)
    print('Done.', task.status())
#
## approach 2: export TFrecords using neighborhoodToArray - return all NOBS by band (faster)
#def kernelnb(img):
#    return img.neighborhoodToArray(kernel_10m).sampleRegions(collection= tile_point)
#
##tile_point = ee.Feature(ee.Geometry.Point(geom.centroid().coordinates()))
#tile_point = ee.Feature(ee.Geometry.Point(pt_list[4]))
#
##size = 24
##weights = ee.List.repeat(ee.List.repeat(1, size), size)
##kernel_10m = ee.Kernel.fixed(size, size, weights)
####Sample pixels in the ImageCollection at these random points
##values_10m = collection.map(kernelnb).flatten()
##        
##print(values_10m)
#
###create kernel
##kernel_10m = ee.Kernel.square(11) #square kernell
#size = 24
#weights = ee.List.repeat(ee.List.repeat(1, size), size)
#kernel_10m = ee.Kernel.fixed(size, size, weights)
#
###Sample pixels in the ImageCollection at these random points
#values_10m = collection.map(kernelnb).flatten()
##print(values_10m.size().getInfo())
#
#folder = "raster_240_all_kernelfixed"
#
#task= ee.batch.Export.table.toCloudStorage(
#        collection= values_10m,
#        description= name,
#        folder= None,
#        fileNamePrefix= folder + '/' + name + 'v4',
#        fileFormat= 'TFRecord',
#        bucket='sampleo')
#        
#try:
#    task.start()
#    #TODO: Implement log dump instead of print
#    print("Processing year: ", folder,' and tile: ', name)
#    time.sleep(15)
#    print(task.status())
#except Exception as str_error:
#    print("Error in year: ", folder,' and tile: ', name)
#    print("Error type equal to ", str_error)