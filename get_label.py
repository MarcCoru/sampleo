#from geotools import get_wms_credentials, build_wms_url
import geotools
import argparse
import os
import requests
from get_tile import get_tile
import geojson
import sys
import shapely.geometry

description="""
queries a geoserver WMS to rasterize a preconfigured WMS layer over a geojson defined geometry
"""

parser = argparse.ArgumentParser(description=description)

parser.add_argument('geojson', type=str,
                    default="jsonfile defining geojson location",
                    help="")
parser.add_argument('--outfolder', type=str,
                    default="data",
                    help="folder to store tif images")
parser.add_argument('-l','--layers',type=str, default="demo:osm_buildings", help="WMS layer")
parser.add_argument('--workspace',type=str, default="demo", help="WMS workspace")
parser.add_argument('-W','--width',type=int, default=240, help="width in pixel")
parser.add_argument('-H','--height',type=int, default=240, help="height in pixel")
parser.add_argument('-s','--style',type=str, default="", help="WMS style")
parser.add_argument('-f','--format',type=str, default="image/geotiff", help="WMS format")

parser.add_argument('-d','--debug',action="store_true", help="debug option: print the wms request")

args = parser.parse_args()

layers=args.layers
workspace=args.workspace
height=args.width
width=args.height
styles=args.style
img_format=args.format

# create dir to store data if needed
if not os.path.exists(args.outfolder):
    os.makedirs(args.outfolder)

# query random tile geometry
#wkt, zone, row, name = get_tile(args.sql, tilesize=240, decimal=-2, conn=None)

geom = geotools.load_geojson(args.geojson)

# read basename name from geojson file
name = os.path.basename(args.geojson).replace(".geojson","")

# project wgs -> utm
geom, zone, row = geotools.wgs2utm(geom)

# prepare wms request
host, user, password = geotools.get_wms_credentials()

request = geotools.build_wms_url(
        wkt=geom.wkt,
        zone=zone,
        row=row,
        host=host,
        layers=layers,
        workspace=workspace,
        height=height,
        width=width,
        user=user,
        password=password,
        styles=styles,
        img_format=img_format)

if args.debug:
    print(request)

outpath=os.path.join(args.outfolder,name+".tif")

# send wms request, authenticate and write tif
with open(outpath, 'wb') as f:

    if user and password: # if WMS_USER and WMS_PASS is defined
        ret = requests.get(request,
                           stream=True,
                           auth=requests.auth.HTTPBasicAuth(user, password))
    else:
        ret = requests.get(request,
                           stream=True)

    for data in ret.iter_content(1024):
        f.write(data)

print(outpath)
