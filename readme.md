# Sampleo

A dockerized module to sample raster label pairs for Earth Observation data

<img src="doc/node_diagram.png">

## Usage

run tests
```
docker run --env-file=credentials.env sampleo selftest"
```

sample random tile (tbd)
```
docker run --env-file=credentials.env sampleo random "from aoi where name='bavaria'"
```

run self test
```
docker run samplEO test
```

requires following envirnment variables to be set on local machine
```
PG_HOST, PG_PORT, PG_USER, PG_DATABASE, PG_PASS
```
or provided as environment file `credentials.env` to the docker container
