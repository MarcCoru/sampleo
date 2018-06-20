# Tools

Functions and scripts that help setting up the system.

## Create Grid

Builds a SQL query to create a rectangular grid within a `--geometry` at `--table` of given `--height` and `--width`.
A `--margin` can be specified between the grid cells.
Each grid cell is attributed by a boolean `eval` at `--eval_ratio` and grid cells that are not `eval` are attributed by a boolean `train` at --train_ratio``

<img width=70% src=../doc/grid.png>


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
