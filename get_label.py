from geotools import query_label
import argparse

"""
queries a postgres database for a random tile within an area of interest (aoi)
and returns a representation
"""

description="""
queries a postgres database for a random tile within an area of interest (aoi).
The aoi table can be defined by --sql
The database connection requires following environment variables:
'PG_HOST', 'PG_USER', 'PG_PASS', 'PG_DATABASE' and 'PG_PORT')
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('outfile', type=str,
                    default="test.tif",
                    help="outtifimage")

parser.add_argument('--sql', type=str,
                    default="from aois where layer='bavaria' and partition='train'",
                    help="sql from and where clause to define region in which the tile is sampled. Defaults to: from aois where layer='bavaria' and partition='train'")

args = parser.parse_args()

query_label(args.outfile)
