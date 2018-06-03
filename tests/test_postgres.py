import psycopg2
import unittest
import geopandas as gpd
import os

class TestPostgres(unittest.TestCase):

    def test_postgis_database(self):

        # read credentials
        try:
            host=os.environ["PG_HOST"]
            port=os.environ["PG_PORT"]
            user=os.environ["PG_USER"]
            database=os.environ["PG_DATABASE"]
            password = os.environ["PG_PASS"]
        except:
            self.fail("could not read postgis credentials from environment")

        # connect
        try:
            conn = psycopg2.connect(
                host=host,
                dbname=database,
                port=port,
                user=user,
                password=password)
        except:
            self.fail("could not connect to database")

        # read aois table
        try:
            sql = "select * from aois"
            df = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col='geom')
        except:
            self.fail("could not retrieve data from table 'aois'")

        # sample single point from aois table
        try:
            sql="select (st_dump(ST_GeneratePoints(geom, 1))).geom from aois where layer='bavaria' and partition='train'"
            geom = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col='geom').iloc[0].geom
        except:
            self.fail("Could not sample random single points with sql '{}'".format(sql))

if __name__ == '__main__':
    unittest.main()
