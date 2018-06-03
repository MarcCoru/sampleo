import psycopg2
import unittest
import os

class TestPostgres(unittest.TestCase):

    def test_read_credientials(self):

        try:
            host=os.environ["PG_HOST"]
            port=os.environ["PG_PORT"]
            user=os.environ["PG_USER"]
            database=os.environ["PG_DATABASE"]
            password = os.environ["PG_PASS"]
        except:
            self.fail("could not read postgis credentials from environment")

        return host,port,user,database,password

    def test_connect(self):

        host,port,user,database,password = self.test_read_credientials()

        try:
            conn = psycopg2.connect(
                host=host,
                dbname=database,
                port=port,
                user=user,
                password=password)
        except:
            self.fail("could not connect to database with host:{}, dbname:{}, port:{}, user:{} and password from environment")

if __name__ == '__main__':
    unittest.main()
