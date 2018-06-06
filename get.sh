#!/bin/bash

# init google project connection
bash google_init.sh /auth/google-service-account-key.json

# data store
bucket=gs://sampleo/test

sql="from grid where train=true"

# this script combines get_tile, get_label and get_raster
# to query data from all sources

# query tile and retrieve geojson path
geojson=`python get_tile.py --sql "$sql"`
echo $geojson

#echo "copy $geojson to $bucket"
gsutil cp $geojson $bucket

# take geojson and query label from wms server
labeltif=$(python get_label.py $geojson)

#echo "copy $labeltif to $bucket"
gsutil cp $labeltif $bucket

# take geojson and query raster from google earth engine
# tbd

# merge everything to one tfrecord
# tbd

# push to google storage
# tbd

# cleanup
# tbd
