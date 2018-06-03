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

query a tile randomly from the area of interest
```
docker run --env-file credentials.env sampleo \
  python get_tile.py --sql "from aois where layer='brazil and partition='eval'"
```
