#from geotools import get_wms_credentials, build_wms_url
import geotools
import argparse
import os
import requests
from get_tile import get_tile
import geojson
import sys
import shapely.geometry

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
parser.add_argument('--outfolder', type=str,
                    default="data",
                    help="folder to store tif images")

args = parser.parse_args()

# create dir to store data if needed
if not os.path.exists(args.outfolder):
    os.makedirs(args.outfolder)

# query random tile geometry
#wkt, zone, row, name = get_tile(args.sql, tilesize=240, decimal=-2, conn=None)

with open(args.geojson) as f:
    gj = geojson.load(f)
pt_list = gj['features'][0]["geometry"]["coordinates"][0]

# convert point list (wgs) to shapely geometry object
geom = shapely.geometry.Polygon(pt_list)

# read basename name from geojson file
name = os.path.basename(args.geojson).replace(".geojson","")

# project wgs -> utm
geom, zone, row = geotools.wgs2utm(geom)

# prepare wms request
host, user, password = geotools.get_wms_credentials()
request = geotools.build_wms_url(geom.wkt, zone, row, host=host)

outpath=os.path.join(args.outfolder,name+".tif")

# send wms request, authenticate and write tif
with open(outpath, 'wb') as f:

    ret = requests.get(request,
                       stream=True,
                       auth=requests.auth.HTTPBasicAuth(user, password))

    for data in ret.iter_content(1024):
        f.write(data)

print(outpath)
