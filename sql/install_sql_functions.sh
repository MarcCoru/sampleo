#!/bin/bash

# installs required postgis functions

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

psql -d $PG_DATABASE -U $PG_USER -h $PG_HOST -p $PG_PORT -f $DIR/randompointsinpolygon.sql
