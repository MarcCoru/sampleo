#!/bin/bash

# init google project connection
bash google_init.sh /auth/google-service-account-key.json

# data store

# psql -tA -h knecht -U mulapostgres -p 25432 -d geo -c "select id from geegrid where origin='bavaria'" > bavaria.ids

bavariaids=$(psql -tA -h $PG_HOST -U $PG_USER -p $PG_PORT -d $PG_DATABASE -c "select id from munich.tiles order by id desc")


# earthengine task list | grep RUNNING | wc -l

# later iterate
for id in $bavariaids; do

    # dummy check number of running tasks
    max_num_tasks=50
    num_running=$(earthengine task list | grep -E "RUNNING|READY" | wc -l)
    while [ "$num_running" -gt "$max_num_tasks" ]
    do
        echo "waiting for $num_running GEE tasks to finish..."
        sleep 5
        num_running=$(earthengine task list | grep -E "RUNNING|READY" | wc -l)
    done


    # skip if folder already exists:
    if [ $(gsutil ls gs://sampleo/munich | grep munich/$id/) ];
    then
        echo "skipping $id. tile already in gs://sampleo/munich" 
        continue
    fi

    exit 0

    python get_geojson.py "from munich.tiles where id=$id" data/$id.geojson
    gsutil cp data/$id.geojson gs://sampleo/munich/$id/

    for scale in 10 20 60; do
        python get_raster_tifs.py \
            --geojson "data/$id.geojson" \
            --bucket 'sampleo' \
            --folder munich/$id \
            --startdate 2016-01-01 \
            --enddate 2017-12-31 \
            --collection "COPERNICUS/S2" \
            --scale $scale > /dev/null &
    done

    for scale in 30 100; do
        python get_raster_tifs.py \
            --geojson "data/$id.geojson" \
            --bucket 'sampleo' \
            --folder munich/$id \
            --startdate 2016-01-01 \
            --enddate 2017-12-31 \
            --collection "LANDSAT/LC08/C01/T1_SR" \
            --scale $scale > /dev/null &
    done
    
    wait

    python get_label.py data/$id.geojson
    gsutil mv data/$id.tif gs://sampleo/munich/$id/label.tif

done
