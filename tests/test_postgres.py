import os, sys
import psycopg2
import unittest
import geopandas as gpd

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from geotools import connect_postgres, read_postgres_credentials

class TestPostgres(unittest.TestCase):

    def test_connect(self):

        # read credentials
        try:
            credentials = read_postgres_credentials()
        except:
            self.fail("could not read postgres credentials")

        try:
            conn = connect_postgres(credentials)
        except:
            self.fail("could not connect to database")

if __name__ == '__main__':
    unittest.main()
