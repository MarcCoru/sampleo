from shapely import geometry
import shapely.wkt
import utm
import geopandas as gpd
import os
import psycopg2
import requests
import geojson

def read_postgres_credentials():

    host=os.environ["PG_HOST"]
    port=os.environ["PG_PORT"]
    user=os.environ["PG_USER"]
    database=os.environ["PG_DATABASE"]
    password = os.environ["PG_PASS"]

    return host, port, user, database, password

def get_wms_credentials():
    host = os.environ["WMS_HOST"]
    user = os.environ["WMS_USER"]
    password = os.environ["WMS_PASS"]

    return host, user, password

def connect_postgres(credentials):

    host, port, user, database, password = credentials

    conn = psycopg2.connect(
        host=host,
        dbname=database,
        port=port,
        user=user,
        password=password)

    return conn

def query_random_point(
        sql="from aois where layer='bavaria' and partition='train'",
        conn=None):

    if conn is None:
        credentials = read_postgres_credentials()
        conn = connect_postgres(credentials)

    sql="select st_transform((st_dump(ST_GeneratePoints(geom, 1))).geom,4326) as geom {}".format(sql)
    geom = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col='geom').iloc[0].geom

    return geom.x, geom.y

def format_name(e,n,zone,row):
    return "E{e}N{n}UTM{zone}{row}".format(e=e,n=n,zone=zone,row=row)

def discretize(easting,northing,decimal=-2):
    """
    discretize floating coordinates to a grid (e.g., 10m, 100m or 1000m)
    """
    easting = int(round(easting,decimal))
    northing = int(round(northing,decimal))
    return easting, northing

def rectangular_buffer(centerx, centery, buffer):
    """
    returns a wkb_hex representation of a box around a rectangular buffered center point
    """

    minx = centerx - buffer
    maxx = centerx + buffer
    miny = centery - buffer
    maxy = centery + buffer

    return minx, maxx, miny, maxy

def create_tile(easting, northing, tilesize):
    """
    gets center point of tile
    returns rectangular tile projected to nearest UTM strip
    discretized to nearest utm grid (defined by decimal rounding)
    """

    buffer=tilesize/2
    minx, maxx, miny, maxy = rectangular_buffer(easting,northing,buffer)

    pts = [(minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)]

    #pts_wgs = [utm.to_latlon(x,y, utm_zone, utm_row) for x,y in pts]

    geom = shapely.geometry.Polygon(pts)

    return geom.wkt

def utmzone2epsg(zone, row):

    def epsgformat(code):
        return "EPSG:{}".format(code)

    if row in "CDEFGHJKLM": # southern hemisphere
        return epsgformat('327'+str(zone)) # epsg:32701 to epsg:32760
    elif row in "NPQRSTUVWXX": # northern hemisphere
        return epsgformat('326'+str(zone)) # epsg:32601 to epsg:32660
    else:
        raise ValueError("row letter {} not handled correctly".format(row))


def bounds_to_utm(minlat,minlon,maxlat,maxlon):
    """
    takes wgs85
    
    determines the appropiate utm zone and row by the center of points min and max
    projects min and max coordinates to utm and ouputs zone and row
    """
    
    centerlat = (minlat+maxlat)/2
    centerlon = (minlon+maxlon)/2
    
    # get center zone and row numbers
    _,_,zone,row = utm.from_latlon(centerlat, centerlon)
    
    # convert min and max
    minx, miny, _, _ = utm.from_latlon(minlat, minlon, force_zone_number=zone)
    maxx, maxy, _, _ = utm.from_latlon(maxlat, maxlon, force_zone_number=zone)
        
    return minx, miny, maxx, maxy, zone, row

def utm2wgs(geom, zone, row):
    pts=list()
    for e,n in geom.exterior.coords:
        lat,lon = utm.to_latlon(e,n,zone,row)
        pts.append((lon, lat))

    return shapely.geometry.Polygon(pts)

def wgs2utm(geom):
    pts=list()
    for lon, lat in geom.exterior.coords:
        easting,northing,zone,row = utm.from_latlon(lat,lon)
        pts.append((easting, northing))

    return shapely.geometry.Polygon(pts), zone, row


# def latlonwkt_to_utmwkt(latlonwkt):
#     """
#     converts wkt from latlon coordinates to nearest utm coordinates
#     """
#
#     # create geometry
#     geom = shapely.wkt.loads(latlonwkt)
#
#     # latlon -> utm
#     east_north=list()
#     for lon, lat in geom.exterior.coords:
#         e,n,zone,row = utm.from_latlon(lat,lon)
#         east_north.append((e,n))
#
#     # create geometry and return wkt in utm
#     return shapely.geometry.Polygon(east_north).wkt, zone, row

def wkt_to_bbox(wkt):
    bbox = shapely.wkt.loads(wkt).bounds
    return ",".join(str(el) for el in bbox)


def build_wms_url(
        wkt,
        zone,
        row,
        host,
        layers,
        workspace,
        height,
        width,
        user="",
        password="",
        styles="",
        img_format="image/geotiff"):

    #utm_wkt, zone, row = latlonwkt_to_utmwkt(wkt)
    bbox = wkt_to_bbox(wkt)
    srs = utmzone2epsg(zone,row)


    query="""
        http://{host}:8080/geoserver/{workspace}/
        wms?service=WMS&
        version=1.1.0&
        request=GetMap&
        layers={layers}&
        styles={styles}&
        bbox={bbox}&
        width={width}&
        height={height}&
        srs={srs}&
        format={format}
        """.format(
        host=host,
        workspace=workspace,
        layers=layers,
        styles=styles,
        bbox=bbox,
        width=width,
        height=height,
        srs=srs,
        format=img_format)

    return query.replace("\n","").replace(" ","") # clean up
    #http://knecht:8080/geoserver/mula18/wms?service=WMS&version=1.1.0&request=GetMap&layers=mula18:bavaria2016&styles=&bbox=4282923.0,5237524.0,4636731.5,5604831.5&width=739&height=768&srs=EPSG:31468&format=image%2Fgeotiff8


def load_geojson(geojson_file):

    with open(geojson_file) as f:
        gj = geojson.load(f)
    pt_list = gj['features'][0]["geometry"]["coordinates"][0]

    # convert point list (wgs) to shapely geometry object
    return shapely.geometry.Polygon(pt_list)

def build_wcs_url_landsat(host,datefrom,dateto, bbox, row, path, coverage):

    #utm_wkt, zone, row = latlonwkt_to_utmwkt(wkt)
    # bbox = wkt_to_bbox(wkt)
    # srs = utmzone2epsg(zone,row)

    minlat, minlon, maxlat, maxlon = bbox


    query="""
        http://{host}/wcs?
        service=WCS&
        Request=GetCoverage&
        version=2.0.0&
        subset=Long({minlon},{maxlon})&
        subset=Lat({minlat},{maxlat})&
        subset=unix({datefrom}T00:00:00,{dateto}T23:59:59)&
        path={path}&
        row={row}&
        format=application/tar&
        CoverageId={coverage}
        """.format(
            host=host, 
            datefrom=datefrom, 
            dateto=dateto,
            minlon=minlon,
            maxlon=maxlon,
            minlat=minlat,
            maxlat=maxlat,
            path=path,
            row=row,
            coverage=coverage)

    # query="""
    #     http://{host}:8080/geoserver/{workspace}/
    #     wms?service=WMS&
    #     version=1.1.0&
    #     request=GetMap&
    #     layers={layers}&
    #     styles={styles}&
    #     bbox={bbox}&
    #     width={width}&
    #     height={height}&
    #     srs={srs}&
    #     format={format}
    #     """.format(
    #     host=host,
    #     workspace=workspace,
    #     layers=layers,
    #     styles=styles,
    #     bbox=bbox,
    #     width=width,
    #     height=height,
    #     srs=srs,
    #     format=img_format)

    return query.replace("\n","").replace(" ","") # clean up
