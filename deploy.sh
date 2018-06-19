#!/bin/bash

# Created using the readme files of the following repositories.
# variables are marked with <> e.g., <change-me>
# using https://github.com/kartoza/docker-postgis

# script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# Start PostGIS Server in Docker
mkdir -p data/postgresql

docker run -d	\
	-v $DIR/data/postgresql:/var/lib/postgresql \
	-p $PG_PORT:5432 \
	-e POSTGRES_DBNAME=$PG_DATABASE \
	-e POSTGRES_PASS=$PGPASSWORD \
	-e POSTGRES_USER=$PG_USER \
	-e ALLOW_IP_RANGE=0.0.0.0/0 \
	--name postgis \
	-t kartoza/postgis

# load required function for get_tile.py
psql -d $PG_DATABASE \
 	-U $PG_USER \
	-p $PG_PORT \
	-h $PG_HOST \
	-f $DIR/sql/randompointsinpolygon.sql

mkdir -p data/geoserver

# Start Geoserver in Docker

# using https://github.com/kartoza/docker-geoserver
docker run --name "geoserver" \
	--link postgis:postgis \
	-p 8080:8080 \
	-v $DIR/data/geoserver:/opt/geoserver/data_dir \
	-d \
	-e USERNAME=admin \
	-e PASS=adminpassword \
	-t kartoza/geoserver
