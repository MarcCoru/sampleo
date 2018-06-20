#!/bin/bash

width=5000
height=5000
margin=500
eval_ratio=0.33
train_ratio=0.5
table=dev.grid


sqlfile="regions.sql"

# drop table if exists
psql -d $PG_DATABASE -h $PG_HOST -U $PG_USER -p $PG_PORT -c "drop table if exists $table"

# append sqlfile with sql
python create_grid.py \
    --geometry "from regions" \
    --table $table \
     -W $width \
     -H $height \
     -m $margin \
     -e $eval_ratio \
     -t $train_ratio >> $sqlfile

# execute sql query
psql -d $PG_DATABASE -h $PG_HOST -U $PG_USER -p $PG_PORT -f $sqlfile

# (optional) cleanup
rm $sqlfile
