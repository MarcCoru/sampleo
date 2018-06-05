import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import unittest
from get_tile import get_tile

class TestSqltools(unittest.TestCase):

    def test_get_tile_one_aoi(self):
        decimal=-2
        tilesize=240
        sql="from aois where layer='bavaria'"
        conn=None
        try:
            get_tile(sql, tilesize, decimal, conn)
        except:
            self.fail("could not run get_tile({sql}, {tilesize}, {decimal}, {conn})".format(sql,tilesize,decimal,conn))

    def test_get_tile_grid(self):
        decimal=-2
        tilesize=240
        sql="from grid where origin='bavaria'"
        conn=None
        try:
            get_tile(sql, tilesize, decimal, conn)
        except:
            self.fail("could not run get_tile({sql}, {tilesize}, {decimal}, {conn})".format(sql,tilesize,decimal,conn))


if __name__ == '__main__':
    unittest.main()
