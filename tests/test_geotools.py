import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import geotools
import unittest

class TestGeotools(unittest.TestCase):

    def test_create_tile(self):

        lat, lon = (47.777922478833936, 12.111875292345331)

        wkt, zone, row = geotools.create_tile(lat, lon)

        wkt_ref = 'POLYGON ((283480 5295580, 283480 5295820, 283720 5295820, 283720 5295580, 283480 5295580))'

        self.assertTrue(wkt==wkt_ref)
        self.assertTrue(zone==33)
        self.assertTrue(row=='T')

    def test_query_random_point(self):

        sql = "from aois where layer='bavaria' and partition='train'"

        try:
            x,y = geotools.query_random_point("from aois where layer='bavaria' and partition='train'")
        except:
            self.fail("could not query random point with sql: {}".format(sql))

    def test_get_wms_credentials(self):

        try:
            geotools.get_wms_credentials()
        except:
            self.fail("could not retrieve WMS credentials. This requires environment variables 'WMS_HOST', 'WMS_USER' and 'WMS_PASS' to be set")

    def test_query_tile(self):

        sql = "from aois where layer='bavaria' and partition='train'"

        try:
            wkt = geotools.query_tile("from aois where layer='bavaria' and partition='train'")
        except:
            self.fail("could not query random tile with sql: {}".format(sql))

    def test_wkt(self):
        import shapely.wkt

        try:
            wkt="POLYGON ((49.17222000889514 49.17172099789813, 49.17437779130425 49.17164150531155, 49.17442986628672 49.17493260845946, 49.17227207993952 49.17501195815076, 49.17222000889514 49.17172099789813))"

            geom = shapely.wkt.loads(wkt)
        except:
            self.fail("")

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
