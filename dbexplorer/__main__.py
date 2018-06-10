import argparse

from dbexplorer.extracting.postgres_like import PostgresLikeDbExtractor
from dbexplorer.extracting.mysql import MysqlDbExtractor
from dbexplorer.extracting.teradata import TeradataDbExtractor

from dbexplorer.visualizing import DbVisualizer

parser = argparse.ArgumentParser(description='Database explorer')
parser.add_argument('-e', '--extended', action='store_true', help='Generate extended report')
parser.add_argument('-s', '--server', help='Server\'s address', type=str, required=True)
parser.add_argument('-p', '--port', help='Server\'s port', type=int)
parser.add_argument('-n', '--database_name', help='Database name', type=str, required=True)
parser.add_argument('-u', '--user', help='Username', type=str, required=True)
parser.add_argument('-pass', '--password', help='Password', type=str, required=True)
parser.add_argument('-t', '--database_type', help='Database type (Postgres, MySQL, Redshift, Teradata', type=str,
                    required=True)
parser.add_argument('-o', '--output', help='Output HTML path', type=str, required=True)
parser.add_argument('-top', '--top_number', help='Number of desired most frequent values', type=int, default=5)
parser.add_argument('-m', '--max_text_length',
                    help='Max length of text in given column that will be taken into account', type=int, default=100)
parser.add_argument('-sc', '--schema', help='Schema for postgres', type=str, default='public')
parser.add_argument('-d', '--odbc_driver', help='ODBC driver name for teradata', type=str)

args = parser.parse_args()


def main():
    db_type = args.database_type.lower()
    if db_type == 'postgres':
        extractor = PostgresLikeDbExtractor
    elif db_type == 'mysql':
        extractor = MysqlDbExtractor
    elif db_type == 'redshift':
        extractor = PostgresLikeDbExtractor
    elif db_type == 'teradata':
        extractor = TeradataDbExtractor
    else:
        raise ValueError
    if db_type == 'teradata' and args.odbc_driver is None:
        raise Exception("Please provide odbc driver for teradata")
    elif db_type != 'teradata' and args.port is None:
        raise Exception("Please provide port for connection")

    extractor = extractor(server_address=args.server,
                          port=args.port,
                          db_name=args.database_name,
                          user=args.user,
                          password=args.password,
                          extended=args.extended,
                          top_number=args.top_number,
                          schema=args.schema,
                          odbc_driver=args.odbc_driver,
                          max_text_len=args.max_text_length,
                          )
    visualizer = DbVisualizer(extractor.extract_to_dict(), args.output)
    visualizer.generate_report()


if __name__ == "__main__":
    main()
