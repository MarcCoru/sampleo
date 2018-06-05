# Sampleo

A dockerized module to sample raster-label pairs for Earth Observation data

<img src="doc/node_diagram.png">

## Usage

build docker
```
bash build_docker.sh
```

main script:
```
docker run --env-file credentials.env sampleo \
  bash get.sh
```

run tests from the docker image
```
docker run --env-file credentials.env sampleo \
  bash selftest.sh
```

**important**: these scripts require the environment variables `PG_HOST`, `PG_PORT`,`PG_USER`, `PG_DATABASE`, `PG_PASS` to be set for the PostgreSQL/Postgis connection.
And `WMS_HOST`, `WMS_USER` and `WMS_PASS` to be set for the WMS label query.
These environment variables can be passed via `--env-file credentials.env` to the docker image.

Requires the `RandomPointsInPolygon.sql` SQL function.
The code is stored in `./sql`. 
It needs to be executed once on the PostGIS server to register the function.

query a tile randomly from the area of interest
```
docker run --env-file credentials.env sampleo \
  python get_tile.py --sql "from aois where layer='brazil and partition='eval'"
```

## Tools

### Create Grid

Builds a SQL query to create a rectangular grid within a `--geometry` at `--table` of given `--height` and `--width`.
A `--margin` can be specified between the grid cells.
Each grid cell is attributed by a boolean `eval` at `--eval_ratio` and grid cells that are not `eval` are attributed by a boolean `train` at --train_ratio``

<img width=70% src=doc/grid.png>

Example call (query is written to `query.sql`):
```bash
python create_grid.py \
    --geometry "from regions where name='bavaria'" \
    --table "dev.testgrid" \
    --width 3000 \
    --height 3000 \
    --margin 500 \
    --eval_ratio 0.8 \
    --train_ratio 0.5 > query.sql
```

`query.sql` can be executed via `psql`
```bash
psql -d $PG_DATABASE -U $PG_USER -h $PG_HOST -p $PG_PORT -f query.sql
```
