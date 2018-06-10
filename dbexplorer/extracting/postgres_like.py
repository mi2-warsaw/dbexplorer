from typing import Tuple, Type
from dbexplorer.extracting.base_extractors import DbExtractor, TableExtractor
from dbexplorer.extracting.db_types import *
import psycopg2
from collections import defaultdict
from dbexplorer.extracting.common import *


class PostgresLikeDbExtractor(DbExtractor):

    def __init__(self, server_address: str, port: int, db_name: str, user: str, password: str,
                 extended: bool, top_number: int, schema: str, odbc_driver: str, max_text_len: int):
        super(PostgresLikeDbExtractor, self).__init__(server_address, port, db_name, user, password, extended,
                                                      top_number, schema, odbc_driver, max_text_len)

    def _get_tables_names(self) -> Sequence[str]:
        cursor = self.db_connection.cursor()
        cursor.execute(f"""SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.schema}' 
                              AND table_type='BASE TABLE';""")
        return [name[0] for name in cursor.fetchall()]

    def connect(self, server_address: str, port: int, db_name: str, user: str, password: str) -> Any:
        return psycopg2.connect(
            f"dbname='{db_name}' port= '{port}' user='{user}' host='{server_address}' password='{password}'")

    @property
    def table_extractor_class(self) -> Type:
        return PostgresTableExtractor


class PostgresTableExtractor(TableExtractor):

    def __init__(self, db_connection: Any, table_name: str, extended: bool, top_number: int, db_name: str,
                 max_text_len: int):
        super(PostgresTableExtractor, self).__init__(db_connection, table_name, extended, top_number, db_name,
                                                     max_text_len)
        self.rows_count = None

    def _map_sql_types(self, sql_type: str) -> ColumnType:
        types = {
            "integer": ColumnType.NUMERIC,
            "smallint": ColumnType.NUMERIC,
            "numeric": ColumnType.NUMERIC,
            "bigint": ColumnType.NUMERIC,
            "decimal": ColumnType.NUMERIC,
            "real": ColumnType.NUMERIC,
            "double precision": ColumnType.NUMERIC,

            "character varying": ColumnType.TEXT,
            "character": ColumnType.TEXT,
            "char": ColumnType.TEXT,
            "varchar": ColumnType.TEXT,
            "text": ColumnType.TEXT,
            "boolean": ColumnType.TEXT,

            "timestamp without time zone": ColumnType.DATETIME,
            "timestamp": ColumnType.DATETIME,
            "timestamptz": ColumnType.DATETIME,
            "date": ColumnType.DATETIME,
            # "USER-DEFINED": ColumnType.NONE,
            # "bytea": ColumnType.NONE,
            # "ARRAY": ColumnType.NONE
        }

        return types[sql_type] if sql_type in types else ColumnType.NONE

    def get_rows_count(self) -> int:
        if self.rows_count is None:
            cursor = self.db_connection.cursor()
            cursor.execute(f"""SELECT COUNT(*) FROM {self.table_name}""")
            result = cursor.fetchone()
            self.rows_count = result[0]
        return self.rows_count

    def get_columns_by_simple_types(self, columns_names: Sequence[str], columns_sql_types: Sequence[str]) \
            -> Mapping[str, Sequence[Mapping[str, str]]]:
        columns_by_simple_types = defaultdict(list)
        for name, sql_type in zip(columns_names, columns_sql_types):
            columns_by_simple_types[self._map_sql_types(sql_type)].append({
                "name": name,
                "sql_type": sql_type
            })
        return columns_by_simple_types

    @staticmethod
    def _get_basic_columns(columns: Sequence[Mapping[str, str]]) -> Sequence[Column]:
        ret = []
        for c in columns:
            ret.append(Column(c["name"], c["sql_type"]))
        return ret

    def _are_texts_longer_than_max(self, column: Mapping[str, str]) -> bool:
        if column['sql_type'] == "boolean":
            return False
        max_len = get_text_len(column["name"], self.table_name, self.db_connection)
        return max_len is not None and max_len > self.max_text_len

    def _get_basic_text_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[TextColumn]:
        ret = []
        cursor = self.db_connection.cursor()
        for c in columns:
            if self._are_texts_longer_than_max(c):
                ret.append(TextColumn(c["name"], c["sql_type"], [TOO_LONG_TEXT_WARNING], []))
            else:
                cursor.execute(f"""SELECT "{c["name"]}", count(*) from {self.table_name}
                            GROUP BY "{c["name"]}"
                            ORDER BY count(*) DESC LIMIT {self.top_number};""")
                result = cursor.fetchall()
                ret.append(TextColumn(c["name"], c["sql_type"], [r[0] for r in result], [r[1] for r in result]))

        return ret

    def _get_basic_numeric_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[NumericColumn]:
        ret = []
        sql = ""
        for i, c in enumerate(columns):
            sql += f'max("{c["name"]}"), min("{c["name"]}"), avg("{c["name"]}")'
            if i < len(columns) - 1:
                sql += ", "
        cursor = self.db_connection.cursor()
        cursor.execute(f"""SELECT {sql} from {self.table_name};""")
        result = cursor.fetchone()

        for i, c in enumerate(columns):
            if check_result_empty(result[3 * i:3 * i + 2]):
                ret.append(NumericColumn(c["name"], c["sql_type"], None, None, None))
                continue

            ret.append(NumericColumn(c["name"], c["sql_type"],
                                     float(result[3 * i]),
                                     float(result[3 * i + 1]),
                                     float(result[3 * i + 2])))
        return ret

    def _get_basic_datetime_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[DatetimeColumn]:
        ret = []
        sql = ""
        for i, c in enumerate(columns):
            sql += f'max("{c["name"]}"), min("{c["name"]}")'
            if i < len(columns) - 1:
                sql += ", "
        cursor = self.db_connection.cursor()
        cursor.execute(f"""SELECT {sql} from {self.table_name};""")
        result = cursor.fetchone()

        for i, c in enumerate(columns):
            ret.append(DatetimeColumn(c["name"], c["sql_type"],
                                      str(result[2 * i]),
                                      str(result[2 * i + 1])
                                      ))
        return ret

    def _extract_basic_stats(self, columns_names: Sequence[str], columns_sql_types: Sequence[str]) -> Sequence[Column]:
        columns_by_simple_types = self.get_columns_by_simple_types(columns_names, columns_sql_types)

        ret = []
        for simple_type, columns in columns_by_simple_types.items():
            if simple_type == ColumnType.NONE:
                ret += self._get_basic_columns(columns)
            elif simple_type == ColumnType.TEXT:
                ret += self._get_basic_text_columns(columns)
            elif simple_type == ColumnType.NUMERIC:
                ret += self._get_basic_numeric_columns(columns)
            elif simple_type == ColumnType.DATETIME:
                ret += self._get_basic_datetime_columns(columns)
            else:
                raise ValueError("Unknown ColumnType")
        return ret

    def _get_extended_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedColumn]:
        ret = []
        for c in columns:
            cursor = self.db_connection.cursor()

            cursor.execute(f"""select IS_NULLABLE from INFORMATION_SCHEMA.COLUMNS
                                 where table_name = '{self.table_name}' and column_name ='{c["name"]}'; """)

            is_nullable = cursor.fetchone()[0]

            cursor.execute(f"""select count(*) from {self.table_name} where "{c["name"]}" is NULL;""")
            nulls_count = cursor.fetchone()[0]

            if self._map_sql_types(c["sql_type"]) == ColumnType.TEXT and self._are_texts_longer_than_max(c):
                distinct_count = None
            else:
                cursor.execute(
                    f"""SELECT COUNT(*) FROM (SELECT DISTINCT "{c["name"]}" FROM {self.table_name}) AS temp;"""
                )
                distinct_count = cursor.fetchone()[0]

            ret.append(ExtendedNoneTypeColumn(c["name"],
                                              c["sql_type"],
                                              is_nullable,
                                              0 if self.get_rows_count() == 0 else (100 * nulls_count
                                                                                    / self.get_rows_count()),
                                              distinct_count))
        return ret

    def _get_extended_text_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedTextColumn]:
        ret = []
        for c in columns:
            basic_text = self._get_basic_text_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            extended_stats = self._get_extended_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            ret.append(ExtendedTextColumn(c["name"], c["sql_type"],
                                          basic_text.top,
                                          basic_text.top_values,
                                          extended_stats.is_nullable,
                                          extended_stats.null_percent,
                                          extended_stats.unique_number))
        return ret

    def _get_extended_numeric_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedNumericColumn]:
        ret = []
        for c in columns:
            basic_numeric = self._get_basic_numeric_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            extended_stats = self._get_extended_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]

            quartiles = self._get_quartiles(c["name"], self.get_rows_count()*(1 - extended_stats.null_percent/100))
            ret.append(ExtendedNumericColumn(c["name"], c["sql_type"],
                                             basic_numeric.max, basic_numeric.min, basic_numeric.mean,
                                             extended_stats.is_nullable,
                                             extended_stats.null_percent,
                                             extended_stats.unique_number,
                                             quartiles))
        return ret

    def _get_extended_datetime_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedDatetimeColumn]:
        ret = []
        for c in columns:
            basic_datetime = self._get_basic_datetime_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            extended_stats = self._get_extended_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            ret.append(ExtendedDatetimeColumn(c["name"], c["sql_type"],
                                              basic_datetime.max,
                                              basic_datetime.min,
                                              extended_stats.is_nullable,
                                              extended_stats.null_percent,
                                              extended_stats.unique_number))
        return ret

    def _extract_extended_stats(self, columns_names: Sequence[str], columns_sql_types: Sequence[str]) \
            -> Sequence[ExtendedColumn]:
        columns_by_simple_types = self.get_columns_by_simple_types(columns_names, columns_sql_types)

        ret = []
        for simple_type, columns in columns_by_simple_types.items():
            if simple_type == ColumnType.NONE:
                ret += self._get_extended_columns(columns)
            elif simple_type == ColumnType.TEXT:
                ret += self._get_extended_text_columns(columns)
            elif simple_type == ColumnType.NUMERIC:
                ret += self._get_extended_numeric_columns(columns)
            elif simple_type == ColumnType.DATETIME:
                ret += self._get_extended_datetime_columns(columns)
            else:
                raise ValueError("Unknown ColumnType")
        return ret

    def _extract_column_names_and_types(self) -> Tuple[Sequence[str], Sequence[str]]:
        cursor = self.db_connection.cursor()
        cursor.execute(f"""
        select
        column_name, data_type
        from information_schema.columns
        where
        table_name = '{self.table_name}';""")
        fetched = cursor.fetchall()
        return [info[0] for info in fetched], [info[1] for info in fetched]

    def _get_quartiles(self, column_name: str, count: int) -> Sequence[float]:
        def quartile_sql(quart, even):
            even_shift = 1 if even else 2
            return f"""(select {column_name} """ \
                   f"""from {self.table_name} """ \
                   f"""where {column_name} is not null order by {column_name} """ \
                   f"""limit {even_shift} offset {int(min(int(quart * (count - 1)), max(count-even_shift, 0)))})"""

        return get_quartiles(column_name, count, quartile_sql, self.db_connection)
