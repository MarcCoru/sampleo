#!/bin/bash

# init google project connection
#bash google_init.sh /auth/google-service-account-key.json

# data store

# psql -tA -h knecht -U mulapostgres -p 25432 -d geo -c "select id from geegrid where origin='bavaria'" > bavaria.ids

bavariaids=$(psql -tA -h knecht -U mulapostgres -p 25432 -d geo -c "select id from geegrid where origin='bavaria' order by random()")


# earthengine task list | grep RUNNING | wc -l

# later iterate
for id in $bavariaids; do

    # skip if folder already exists:
    if [ $(gsutil ls gs://sampleo/tiles | grep tiles/$id/) ]; 
    then 
        echo "skipping $id. tile already in gs://sampleo/tiles" 
        continue 
    fi

    # dummy check number of running tasks
    max_num_tasks=1
    num_running=$(earthengine task list | grep RUNNING | wc -l)
    while [ "$num_running" -gt "$max_num_tasks" ]
    do
        echo "waiting for $num_running GEE tasks to finish..."
        sleep 5
        num_running=$(earthengine task list | grep RUNNING | wc -l)
    done

    already_downloaded_ids=$(gsutil ls gs://sampleo/tiles | grep -o [0-9]*)

    python get_geojson.py "from geegrid where id=$id" data/$id.geojson

    python get_srdata.py --geojson data/$id.geojson -ts 2016-01-01 -te 2016-12-31 --collection "COPERNICUS/S2" -b 'sampleo' -f tiles/$id -r 10 > /dev/null &
    python get_srdata.py --geojson data/$id.geojson -ts 2016-01-01 -te 2016-12-31 --collection "COPERNICUS/S2" -b 'sampleo' -f tiles/$id -r 20 > /dev/null &
    python get_srdata.py --geojson data/$id.geojson -ts 2016-01-01 -te 2016-12-31 --collection "COPERNICUS/S2" -b 'sampleo' -f tiles/$id -r 60 > /dev/null &

    #python get_srdatapy.py 'data/$id.geojson' -ts 2016-01-01 -te 2016-12-31 --collection "LANDSAT/LC08/C01/T1" -f gs://sampleo/tiles/$id/LSraster30m.tfrecord -r 30

    python get_label.py data/$id.geojson
    gsutil mv data/$id.tif gs://sampleo/tiles/$id/label.tif

done
