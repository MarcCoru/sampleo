import psycopg2
from geotools import rectangular_buffer
import shapely
import utm
import geopandas as gpd
import geotools



def build_sql_geom2grid(sql, height, width, margin=0):
    """
    <sql> clause defines a target geometry that will be separated in grids.
    e.g, from regions where name='bavaria';

    creates a regular grid matrix of given cell <height> and cell <width> [m].
    optional <margin> can be defined (defaults to zero).
    requires table with fields geom::geometry, name::text, native_srs::integer
    """

    query_sql="""
        select 
            st_intersection(
            st_transform(
            st_buffer(
                (
                ST_PixelAsPolygons(
                    ST_AsRaster(
                        st_transform(geom,native_srs), -- transform to nearest utm to get meter
                        cast({width} as double precision), -- width
                        cast({height} as double precision), -- height
                        '8BSI'::text,
                        1,0,NULL,NULL,0,0,true -- follow defaults until touched=true
                        )
                    )
                ).geom,
                -{margin}),4326),
            st_transform(geom,4326)) as geom,
            name as origin
        {from_where_cause}
    """.format(width=width, height=height, margin=margin, from_where_cause=sql)

    return query_sql

def sql_create_table(table):

    sql="CREATE TABLE IF NOT EXISTS {table}(id SERIAL NOT NULL PRIMARY KEY,geom geometry, origin text);".format(table=table)

    return sql

# def build_sql_insert(table,wkt,srid):
#     """
#     returns a insert sql statement
#     """
    
#     sql = "INSERT INTO {table}(geom, origin) VALUES (ST_GeomFromText('{wkt}', {srid}));".format(
#         table=table,
#         wkt=wkt,
#         srid=srid)
    
#     return sql

# def get_extent(sql, conn=None):
#     """
#     query the extent of the data from a postgis feature
#     always returns in epsg:4326
#     """

#     if conn is None:
#         credentials = geotools.read_postgres_credentials()
#         conn = geotools.connect_postgres(credentials)

#     query_sql="select ST_Transform(ST_Envelope(geom),4326) as geom {}".format(sql)
#     bbox = gpd.GeoDataFrame.from_postgis(query_sql, conn, geom_col='geom' )

#     minlon, minlat, maxlon, maxlat = bbox.iloc[0,0].bounds

#     return minlon, minlat, maxlon, maxlat

