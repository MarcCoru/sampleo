import geotools
import argparse
import geopandas as gpd
import utm
import geojson
import shapely.wkt
import os

def parse_args():

    description="""
    queries a postgres database for a random tile within an area of interest (aoi).
    The aoi table can be defined by --sql
    The database connection requires following environment variables:
    'PG_HOST', 'PG_USER', 'PG_PASS', 'PG_DATABASE' and 'PG_PORT')
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--sql', type=str,
                        default="from grid where origin='bavaria' and train=true",
                        help="sql from and where clause to define region in which the tile is sampled. Defaults to: from aois where layer='bavaria' and partition='train'")
    parser.add_argument('--tilesize', type=int,
                        default=240,
                        help="size of rectangular tile (defaults to 240m)")
    parser.add_argument('--outfolder', type=str,
                        default="data",
                        help="folder to store geojson tiles")

    return parser.parse_args()

#wkt, zone, row, name = query_tile(sql=args.sql)

def get_tile(sql, tilesize, decimal=-2, conn=None):

    if conn is None:
        credentials = geotools.read_postgres_credentials()
        conn = geotools.connect_postgres(credentials)

    sql_query="""
        select
            st_transform(
                (
                    st_dump(
                        RandomPointsInPolygon(st_union(geom), 1))
                ).geom,
                4326) as geom
                {from_where_clause}
            """.format(from_where_clause=sql)

    try:
        geom = gpd.GeoDataFrame.from_postgis(sql_query, conn, geom_col='geom').iloc[0].geom
    except:
        raise ValueError("Dataset query not successfull! full sql query: {}".format(sql_query))

    lon, lat = (geom.x, geom.y)

    # project center (wgs) to center (utm)
    easting, northing, zone, row = utm.from_latlon(lat,lon)

    easting, northing = geotools.discretize(easting,northing,decimal=decimal)

    name = geotools.format_name(easting, northing, zone, row)

    # create rectangle around center
    wkt = geotools.create_tile(easting,northing,tilesize=tilesize)

    return wkt, zone, row, name

if __name__ == '__main__':
    args = parse_args()

    wkt, zone, row, name = get_tile(args.sql, args.tilesize)

    # loat coordinate in UTM
    geom = shapely.wkt.loads(wkt)

    # utm -> latlon wg84
    geom = geotools.utm2wgs(geom,zone,row)

    # create feature object and feature collection
    feat = geojson.Feature(geometry=geom)
    collection=geojson.FeatureCollection([feat])

    # create folder if not exists
    if not os.path.exists(args.outfolder):
        os.makedirs(args.outfolder)

    # write geojson file
    outpath=os.path.join(args.outfolder, name+".geojson")
    with open(outpath, 'w') as outfile:
        geojson.dump(collection, outfile)

    # print to stdout to be used for further processing
    print(outpath)
