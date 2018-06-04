import argparse
import sqltools

def parse_args():

    description="""
        prepares a sql query that creates a grid and assigns the grid cells to train/test/eval

        The database connection requires following environment variables:
        'PG_HOST', 'PG_USER', 'PG_PASS', 'PG_DATABASE' and 'PG_PORT')

        usage:
        # create sql
        python create_grid.py --table "grid" --geometry "from regions where name='bavaria'" > query.sql

        # execute sql
        psql -f query.sql

        """

    parser = argparse.ArgumentParser(description=description)
        
    parser.add_argument('--geometry', type=str,
                        default="from regions where name='bavaria'",
                        help="a sql from where term to define a geometry. e.g, from regions where name='bavaria'")
    parser.add_argument('--table', type=str,
                        default="grid",
                        help="database table to insert geometry")
    parser.add_argument('-W','--width', type=int,
                        default=30000,
                        help="cell width in meter")
    parser.add_argument('-H','--height', type=int,
                        default=30000,
                        help="cell height in meter")
    parser.add_argument('-m','--margin', type=int,
                        default=1000,
                        help="margin between cells in meter")
    parser.add_argument('-e','--eval_ratio', type=float,
                        default=.8,
                        help="ratio of assigning cell to eval vs train/test")
    parser.add_argument('-t','--train_ratio', type=float,
                        default=.5,
                        help="ratio of assigning cell to train vs test")

    return parser.parse_args()

def create_grid(table, sql, width, height, margin, eval_ratio, train_ratio):

    out=""

    # create table if not exists
    out+=sqltools.sql_create_table(table)

    sql_select_query = sqltools.build_sql_geom2grid(sql, height, width, margin)

    insert_sql="""
    Insert INTO {table}(geom, origin)
    {select_sql};
    """.format(
        table=table,
        select_sql=sql_select_query)
    out+=insert_sql

    sql_eval_column = """
    alter table {table} add COLUMN IF NOT EXISTS eval bool;
    UPDATE {table} SET eval=random()>{eval_ratio};
    """.format(table=table,eval_ratio=eval_ratio)
    out+=sql_eval_column

    sql_test_column = """
    alter table {table} add COLUMN IF NOT EXISTS train bool;
    UPDATE {table} SET train=random()>{train_ratio} where not eval;
    """.format(table=table, train_ratio=train_ratio)
    out+=sql_test_column

    return out

if __name__=='__main__':
    args=parse_args()
    sql = create_grid(
        args.table,
        args.geometry,
        args.width,
        args.height,
        args.margin,
        args.eval_ratio,
        args.train_ratio)

    print(sql)