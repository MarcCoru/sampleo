from shapely import geometry
import utm

def create_tile(lat,lon, tilesize=240, decimal=2):
    """
    gets center point of tile in wgs84 latitude and longitude
    returns rectangular tile projected to nearest UTM strip
    discretized to nearest utm grid (defined by decimal rounding)
    """

    def rectangular_buffer(centerx, centery, buffer):
        """
        returns a wkb_hex representation of a box around a rectangular buffered center point
        """

        minx = centerx - buffer
        maxx = centerx + buffer
        miny = centery - buffer
        maxy = centery + buffer

        return minx, maxx, miny, maxy

    # project center (wgs) to center ()
    easting, northing, utm_zone, utm_row = utm.from_latlon(lat,lon)

    easting = int(round(easting,decimal))
    northing = int(round(northing,decimal))

    buffer=tilesize/2
    minx, maxx, miny, maxy = rectangular_buffer(easting,northing,buffer)

    pts = [(minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)]

    pts_wgs = [utm.to_latlon(x,y, utm_zone, utm_row) for x,y in pts]

    geom = geometry.Polygon(pts_wgs)

    return geom.wkt, utm_zone, utm_row
