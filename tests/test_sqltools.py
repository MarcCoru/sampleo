import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

import geotools
import sqltools
import create_grid
import unittest
import utm

class TestSqltools(unittest.TestCase):

    def test_query_landsat_row_path(self):

        lat=48
        lon=12

        try:
            path, row = sqltools.query_landsat_row_path(lat=lat, lon=lon)
        except:
            self.fail("Could not query path row from postgis server. is postgis connected? does the postgis database contain a wrs2_descending table with attributes geom, path and row?")
        
        path_ref=192
        row_ref=27

        self.assertEqual(path,path_ref)
        self.assertEqual(row,row_ref)

    def test_build_sql_geom2grid(self):

        sql="from regions where name='bavaria'"
        height=30000
        width=30000
        margin=20000

        sql_query = sqltools.build_sql_geom2grid(
                sql,
                height,
                width,
                margin)

        sql_query_ref="\n        select \n            st_intersection(\n            st_transform(\n            st_buffer(\n                (\n                ST_PixelAsPolygons(\n                    ST_AsRaster(\n                        st_transform(geom,native_srs), -- transform to nearest utm to get meter\n                        cast(30000 as double precision), -- width\n                        cast(30000 as double precision), -- height\n                        '8BSI'::text,\n                        1,0,NULL,NULL,0,0,true -- follow defaults until touched=true\n                        )\n                    )\n                ).geom,\n                -20000),4326),\n            st_transform(geom,4326)) as geom,\n            name as origin\n        from regions where name='bavaria'\n    "
        
        self.assertEqual(sql_query,sql_query_ref)

    def test_sql_create_table(self):
        ref_sql = 'CREATE TABLE IF NOT EXISTS test(id SERIAL NOT NULL PRIMARY KEY,geom geometry, origin text);'
        sql = sqltools.sql_create_table("test")
        self.assertEqual(sql,ref_sql)

    def test_create_grid(self):

        table = "test"
        geometry = "from regions where name='bavaria'"
        width = 30000
        height =30000
        margin =1000
        eval_ratio = .8
        train_ratio = .5

        sql = create_grid.create_grid(
            table,
            geometry,
            width,
            height,
            margin,
            eval_ratio,
            train_ratio)
        
        ref_sql = "CREATE TABLE IF NOT EXISTS test(id SERIAL NOT NULL PRIMARY KEY,geom geometry, origin text);\n    Insert INTO test(geom, origin)\n    \n        select \n            st_intersection(\n            st_transform(\n            st_buffer(\n                (\n                ST_PixelAsPolygons(\n                    ST_AsRaster(\n                        st_transform(geom,native_srs), -- transform to nearest utm to get meter\n                        cast(30000 as double precision), -- width\n                        cast(30000 as double precision), -- height\n                        '8BSI'::text,\n                        1,0,NULL,NULL,0,0,true -- follow defaults until touched=true\n                        )\n                    )\n                ).geom,\n                -1000),4326),\n            st_transform(geom,4326)) as geom,\n            name as origin\n        from regions where name='bavaria'\n    ;\n    \n    alter table test add COLUMN IF NOT EXISTS eval bool;\n    UPDATE test SET eval=random()>0.8;\n    \n    alter table test add COLUMN IF NOT EXISTS train bool;\n    UPDATE test SET train=random()>0.5 where not eval;\n    "
        
        self.assertEqual(sql,ref_sql)

    # def test_build_sql_insert(self):
    #     wkt="POLYGON ((49.17222000889514 49.17172099789813, 49.17437779130425 49.17164150531155, 49.17442986628672 49.17493260845946, 49.17227207993952 49.17501195815076, 49.17222000889514 49.17172099789813))"
    #     sql = sqltools.build_sql_insert("test", wkt, "4326")
    #     sql_ref = "INSERT INTO test(geom) VALUES (ST_GeomFromText('POLYGON ((49.17222000889514 49.17172099789813, 49.17437779130425 49.17164150531155, 49.17442986628672 49.17493260845946, 49.17227207993952 49.17501195815076, 49.17222000889514 49.17172099789813))', 4326));"

    #     self.assertEqual(sql,sql_ref)

    # def test_get_extent(self):
    #     sql = "from aois where layer='bavaria'"
    #     try:
    #         sqltools.get_extent(sql=sql)
    #     except:
    #         self.fail("could not query the extent using: "+sql)

if __name__ == '__main__':
    unittest.main()
