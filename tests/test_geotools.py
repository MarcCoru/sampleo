import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import geotools
import sqltools
import unittest
import utm
import shapely.wkt

class TestGeotools(unittest.TestCase):

    def test_create_tile(self):

        lat, lon = (47.777922478833936, 12.111875292345331)

        easting, northing, zone, row = utm.from_latlon(lat,lon)

        easting, northing = geotools.discretize(easting,northing,decimal=-2)

        wkt = geotools.create_tile(easting, northing, tilesize=240)

        wkt_ref = 'POLYGON ((283480 5295580, 283480 5295820, 283720 5295820, 283720 5295580, 283480 5295580))'

        self.assertTrue(wkt==wkt_ref)
        self.assertTrue(zone==33)
        self.assertTrue(row=='T')

    def test_rectangular_buffer(self):

        minx, maxx, miny, maxy = geotools.rectangular_buffer(0,0, 1)

        self.assertTrue(minx==-1)
        self.assertTrue(miny==-1)
        self.assertTrue(maxx==1)
        self.assertTrue(maxy==1)

    # def test_query_random_point(self):
    #
    #     sql = "from aois where layer='bavaria' and partition='train'"
    #
    #     try:
    #         geotools.query_random_point("from aois where layer='bavaria' and partition='train'")
    #     except:
    #         self.fail("could not query random point with sql: {}".format(sql))

    def test_get_wms_credentials(self):

        try:
            geotools.get_wms_credentials()
        except:
            self.fail("could not retrieve WMS credentials. This requires environment variables 'WMS_HOST', 'WMS_USER' and 'WMS_PASS' to be set")

    # def test_query_tile(self):
    #
    #     sql = "from aois where layer='bavaria' and partition='train'"
    #
    #     try:
    #         wkt, zone, row, name = geotools.query_tile("from aois where layer='bavaria' and partition='train'")
    #     except:
    #         self.fail("could not query random tile with sql: {}".format(sql))

    def test_format_name(self):
        easting=557000
        northing=5569100
        zone=32
        row='U'
        name = geotools.format_name(easting, northing, zone, row)

        ref_name='E557000N5569100UTM32U'
        self.assertEqual(ref_name,name)


    # def test_latlonwkt_to_utmwkt(self):
    #     latlonwkt="POLYGON ((49.17222000889514 49.17172099789813, 49.17437779130425 49.17164150531155, 49.17442986628672 49.17493260845946, 49.17227207993952 49.17501195815076, 49.17222000889514 49.17172099789813))"
    #
    #     utm_wkt, zone, row = geotools.latlonwkt_to_utmwkt(latlonwkt)
    #
    #     ref_wkt = 'POLYGON ((366739.9790677647 5448209.999917955, 366739.9790695914 5448449.999918112, 366979.9791826151 5448449.999919109, 366979.9791807987 5448209.99991895, 366739.9790677647 5448209.999917955))'
    #     ref_row = 'U'
    #     ref_zone = 39
    #
    #     self.assertTrue(utm_wkt==ref_wkt)
    #     self.assertTrue(zone==ref_zone)
    #     self.assertTrue(row==ref_row)

    # def test_build_wms_request(self):
    #     wkt = "POLYGON ((9.171442817249709 47.48385544131508, 9.173611565899373 47.48387053328839, 9.173596560612923 47.48605305277751, 9.171427815569659 47.4860379475766, 9.171442817249709 47.48385544131508))"
    #
    #     request = geotools.build_wms_url(
    #         wkt,
    #         layers="mula18:bavaria2016",
    #         workspace="mula18",
    #         styles="",
    #         height=240,
    #         width=240,
    #         format="image/geotiff8")
    #
    #     ref_request = "http://"+os.environ["WMS_HOST"]+":8080/geoserver/mula18/wms?service=WMS&version=1.1.0&request=GetMap&layers=mula18:bavaria2016&styles=&bbox=772962.4116460793,1014749.999659653,773202.4127387364,1014989.999664698&width=240&height=240&srs=EPSG:32638&format=image/geotiff8"
    #     self.assertTrue(request==ref_request)

    def test_utmzone2epsg(self):
        zone=39
        row='U'
        epsg = geotools.utmzone2epsg(zone,row)

        ref_epsg = 'EPSG:32639'

        self.assertTrue(epsg==ref_epsg)

    def test_load_geojson(self):
        geom = geotools.load_geojson("tests/data/tile.geojson")

        wkt_ref='POLYGON ((9.482452043886109 49.85463343881894, 9.482473535305088 49.85679198904913, 9.48581232614336 49.85677804579602, 9.485790686014679 49.85461949662469, 9.482452043886109 49.85463343881894))'

        self.assertEqual(geom.wkt, wkt_ref)

    def test_bounds_bounds_to_utm(self):

        minlon=8.936117736731113
        maxlon=13.928324974888927
        minlat=47.240412610307
        maxlat=50.56321539603782

        ext = geotools.bounds_to_utm(minlat,minlon,maxlat,maxlon)

        minx, miny, maxx, maxy, zone, row = ext

        self.assertEqual(minx, 495165.14233676565)
        self.assertEqual(miny, 5231882.834194369)
        self.assertEqual(maxx, 848972.1925248313)
        self.assertEqual(maxy, 5612859.060998418)
        self.assertEqual(zone, 32)
        self.assertEqual(row, 'U')


    def test_wkt_to_bbox(self):
        wkt = 'POLYGON ((366739.9790677647 5448209.999917955, 366739.9790695914 5448449.999918112, 366979.9791826151 5448449.999919109, 366979.9791807987 5448209.99991895, 366739.9790677647 5448209.999917955))'
        bbox = geotools.wkt_to_bbox(wkt)

        ref_bbox='366739.9790677647,5448209.999917955,366979.9791826151,5448449.999919109'
        self.assertTrue(bbox==ref_bbox)


        # test within a centimeter
        #self.assertTrue(round(bbox[0],2)==round(ref_bbox[0],2))
        #self.assertTrue(round(bbox[2],2)==round(ref_bbox[2],2))
        #self.assertTrue(round(bbox[3],2)==round(ref_bbox[3],2))
        #self.assertTrue(round(bbox[1],2)==round(ref_bbox[1],2))

if __name__ == '__main__':
    unittest.main()
