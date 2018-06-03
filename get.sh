#!/bin/bash

# this script combines get_tile, get_label and get_raster
# to query data from all sources

# query tile and retrieve geojson path
geojson=$(python get_tile.py)
echo $geojson

# take geojson and query label from wms server
labeltif=$(python get_label.py $geojson)
echo $labeltif

# take geojson and query raster from google earth engine
# tbd

# merge everything to one tfrecord
# tbd

# push to google storage
# tbd

# cleanup
# tbd
