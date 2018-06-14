# Sampleo

A dockerized module to sample raster-label pairs for Earth Observation data

<img src="doc/node_diagram.png">

**important**: these scripts require the environment variables `PG_HOST`, `PG_PORT`,`PG_USER`, `PG_DATABASE`, `PG_PASS` to be set for the PostgreSQL/Postgis connection.
And `WMS_HOST`, `WMS_USER` and `WMS_PASS` to be set for the WMS label query.
Connection to the Google Project requires `GOOGLE_PROJECT_ID` to be set and `auth/google-service-account-key.json` to be generated and located in `auth`
These environment variables can be passed via `--env-file credentials.env` to the docker image.

## First Steps

## Query munich

make sure that auth/google-service-account-key.geojson is present
```
docker run -v $HOME/.config/earthengine:/root/.config/earthengine -v $PWD/auth:/auth --env-file auth/credentials.env sampleo bash get_munich.sh
```

clone repository
```
git clone https://gitlab.com/MarcCoru/sampleo.git
```

build docker image
```
bash build_docker.sh
```

authenticate earthengine
```
docker run -ti -v $HOME/.config/earthengine:/root/.config/earthengine sampleo
root@c98349e14a4d:/sampleo# earthengine authenticate
```

main script:
```
docker run -v $PWD/auth:/auth --env-file auth/credentials.env sampleo \
  bash get.sh
```

run tests from the docker image
```
docker run --env-file credentials.env sampleo \
  bash selftest.sh
```
## Structure

the main script `get.sh` calls python scripts
  1. to generate a tile-geojson (`get_tile.py`)
  2. to query labels form a `WMS Server` (`get_label.py`)
  3. (tbd) to query raster data from `Google Earth Engine` (`get_raster.py`)
  4. (tbd) to load everything on Google Cloud storage

### Get Tile

Requires the `RandomPointsInPolygon.sql` SQL function.
The code is stored in `./sql`.
It needs to be executed once on the PostGIS server to register the function.

query a tile from the grid cells that are attributed with
```
docker run --env-file credentials.env sampleo \
  python get_tile.py --sql "from grid where origin='bavaria' and train=true"
```

writes geojson representation to output folder (default `data`).
naming format: `"E{e}N{n}UTM{zone}{row}"` e.g, `E557000N5569100UTM32U`
e.g., geojson output: `data/E557000N5569100UTM32U.geojson`

### Get Label

reads a geojson tile representation and queries a `Geotiff` from a defined WMS Server

requires environment variables `WMS_HOST`, `WMS_USER` and `WMS_PASS`

```
docker run --env-file credentials.env sampleo \
  python get_label.py `data/E557000N5569100UTM32U.geojson`
```

## Tools

Functions and scripts meant to be run once for initial setup.

### Create Grid

Builds a SQL query to create a rectangular grid within a `--geometry` at `--table` of given `--height` and `--width`.
A `--margin` can be specified between the grid cells.
Each grid cell is attributed by a boolean `eval` at `--eval_ratio` and grid cells that are not `eval` are attributed by a boolean `train` at --train_ratio``

<img width=70% src=doc/grid.png>


the `--geometry` table requires `geom::geometry, native_srs::integer, name::test` fields.
The generated `--table` contains `id::serial`, `origin::test`, `eval::bool`, `train::bool`

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

### Convert Tif to Tfrecord

```
python tif2tfrecord.py <tiffolder> <target>.tfrecord
```

raster images are organized in `<tiffolder>/x/*.tif` and label image(s) in `<tiffolder>/y/*.tif`.
the output `<target>` will be `gzipped` if it ends with `.gz` 

## Quicktests

check google connectivity
```
docker run -v $PWD/auth:/auth --env-file auth/credentials.env sampleo bash google_init.sh /auth/google-service-account-key.json
```

## Notes

```
docker run -v $HOME/.config/earthengine:/root/.config/earthengine -v $PWD/auth:/auth --env-file auth/credentials.env sampleo bash get_tif.sh
```
