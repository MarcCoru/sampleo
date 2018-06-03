import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import geotools
import unittest

class TestGeotools(unittest.TestCase):

    def test_create_tile(self):

        lat = 12.86367927221085
        lon = 48.34203965643974

        wkt, zone, row = geotools.create_tile(lat,lon)

        wkt_ref = 'POLYGON ((12.86258297371284 48.34093457517496, 12.86475089733545 48.34091172856528, 12.86477330602003 48.34312133128834, 12.86260537849616 48.34314415896795, 12.86258297371284 48.34093457517496))'
        self.assertTrue(wkt==wkt_ref)

        self.assertTrue(zone==39)

        self.assertTrue(row=='P')

if __name__ == '__main__':
    unittest.main()
