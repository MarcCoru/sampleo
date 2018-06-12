import geotools
import psycopg2
import geopandas as gpd
import geojson
import os
import argparse


def parse_args():

    description="""
    get a geojson representation of a tile selected by the --sql query.
    e.g., --sql 'from geegrid where id=7527'
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('sql', type=str,
                        default="from geegrid where id=7527",
                        help="select the tile by sql query. e.g., from geegrid where id=7527")
    parser.add_argument('geojson', type=str,
                        default="data/tile.geojson",
                        help="ouput path e.g., data/tile.geojson")

    return parser.parse_args()

def query_tile(sql, outpath):

    credentials = geotools.read_postgres_credentials()
    conn = geotools.connect_postgres(credentials)

    geom = gpd.GeoDataFrame.from_postgis("select geom "+sql, conn, geom_col='geom').iloc[0].geom
        

    feat = geojson.Feature(geometry=geom)
    collection=geojson.FeatureCollection([feat])

    outdir=os.path.dirname(outpath)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # write geojson file
    with open(outpath, 'w') as outfile:
        geojson.dump(collection, outfile)

    # print to stdout to be used for further processing
    print(outpath)

if __name__=='__main__':
    args=parse_args()
    query_tile(args.sql, args.geojson)
