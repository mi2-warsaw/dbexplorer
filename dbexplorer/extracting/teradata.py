from typing import Tuple, Type
from dbexplorer.extracting.base_extractors import DbExtractor, TableExtractor
import pyodbc
from collections import defaultdict
from dbexplorer.extracting.db_types import *
from dbexplorer.extracting.common import check_result_empty


class TeradataDbExtractor(DbExtractor):

    def __init__(self, server_address: str, port: int, db_name: str, user: str, password: str,
                 extended: bool, top_number: int, schema: str, odbc_driver: str):
        super(TeradataDbExtractor, self).__init__(server_address, port, db_name, user, password, extended, top_number,
                                                  schema, odbc_driver)

    def _get_tables_names(self) -> Sequence[str]:
        qry = f"SELECT TableName FROM dbc.tables WHERE tablekind = 'T' and databasename='{self.db_name}';"
        cursor = self.db_connection.cursor()
        results = cursor.execute(qry)
        tables = []
        for table in results:
            tables.append(table[0].strip())
        return tables

    def connect(self, server_address: str, port: int, db_name: str, user: str, password: str) -> Any:
        pyodbc.pooling = False
        connection_string = f"DRIVER={{{self.odbc_driver}}};DBCNAME={server_address};UID={user};PWD={password}"
        return pyodbc.connect(connection_string, autocommit=True)

    @property
    def table_extractor_class(self) -> Type:
        return TeradataTableExtractor


class TeradataTableExtractor(TableExtractor):

    def __init__(self, db_connection: Any, table_name: str, extended: bool, top_number: int, db_name: str):
        super(TeradataTableExtractor, self).__init__(db_connection, table_name, extended, top_number, db_name)
        self.rows_count = None

    def _map_sql_types(self, sql_type: str) -> ColumnType:
        types = {
            "TIME": ColumnType.DATETIME,
            "CHARACTER": ColumnType.TEXT,
            "VARCHAR": ColumnType.TEXT,
            "DECIMAL": ColumnType.NUMERIC,
            "DATE": ColumnType.DATETIME,
            "FLOAT": ColumnType.NUMERIC,
            "INTEGER": ColumnType.NUMERIC,
            "BYTEINT": ColumnType.NUMERIC,
            "SMALLINT": ColumnType.NUMERIC,
            "BIGINT": ColumnType.NUMERIC,
            "NUMBER": ColumnType.NUMERIC,
            "TIMESTAMP WITH TIME ZONE": ColumnType.DATETIME,
            "TIMESTAMP": ColumnType.DATETIME,
        }

        return types[sql_type] if sql_type in types else ColumnType.NONE

    def get_rows_count(self) -> int:
        if self.rows_count is None:
            cursor = self.db_connection.cursor()
            results = cursor.execute(f"select count(*) from {self.db_name}.{self.table_name}")
            self.rows_count = results.fetchone()[0]
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

    def _extract_column_names_and_types(self) -> Tuple[Sequence[str], Sequence[str]]:
        cursor = self.db_connection.cursor()
        cursor.execute(f"""select trim(ColumnName) AS colname, trim(ColumnType) AS coltype FROM DBC.COLUMNS 
                            where DatabaseName = '{self.db_name}' and TableName = '{self.table_name}'""")
        fetched = cursor.fetchall()
        return [info[0] for info in fetched], [self.convert_to_sql(info[1]) for info in fetched]

    @staticmethod
    def convert_to_sql(db_type):
        if db_type == "A1":
            return "ARRAY"
        elif db_type == "AN":
            return "MULTI-DIMENSIONAL ARRAY"
        elif db_type == "AT":
            return "TIME"
        elif db_type == "BF":
            return "BYTE"
        elif db_type == "BO":
            return "BLOB"
        elif db_type == "BV":
            return "VARBYTE"
        elif db_type == "CF":
            return "CHARACTER"
        elif db_type == "CO":
            return "CLOB"
        elif db_type == "CV":
            return "VARCHAR"
        elif db_type == "D":
            return "DECIMAL"
        elif db_type == "DA":
            return "DATE"
        elif db_type == "DH":
            return "INTERVAL DAY TO HOUR"
        elif db_type == "DM":
            return "INTERVAL DAY TO MINUTE"
        elif db_type == "DS":
            return "INTERVAL DAY TO SECOND"
        elif db_type == "DY":
            return "INTERVAL DAY"
        elif db_type == "F":
            return "FLOAT"
        elif db_type == "HM":
            return "INTERVAL HOUR TO MINUTE"
        elif db_type == "HS":
            return "INTERVAL HOUR TO SECOND"
        elif db_type == "HR":
            return "INTERVAL HOUR"
        elif db_type == "I":
            return "INTEGER"
        elif db_type == "I1":
            return "BYTEINT"
        elif db_type == "I2":
            return "SMALLINT"
        elif db_type == "I8":
            return "BIGINT"
        elif db_type == "JN":
            return "JSON"
        elif db_type == "MI":
            return "INTERVAL MINUTE"
        elif db_type == "MO":
            return "INTERVAL MONTH"
        elif db_type == "MS":
            return "INTERVAL MINUTE TO SECOND"
        elif db_type == "N":
            return "NUMBER"
        elif db_type == "PD":
            return "PERIOD(DATE)"
        elif db_type == "PM":
            return "PERIOD(TIMESTAMP WITH TIME ZONE)"
        elif db_type == "PS":
            return "PERIOD(TIMESTAMP)"
        elif db_type == "PT":
            return "PERIOD(TIME)"
        elif db_type == "PZ":
            return "PERIOD(TIME WITH TIME ZONE)"
        elif db_type == "SC":
            return "INTERVAL SECOND"
        elif db_type == "SZ":
            return "TIMESTAMP WITH TIME ZONE"
        elif db_type == "TS":
            return "TIMESTAMP"
        elif db_type == "TZ":
            return "TIME WITH TIME ZONE"
        elif db_type == "UT":
            return "UDT Type"
        elif db_type == "XM":
            return "XML"
        elif db_type == "YM":
            return "INTERVAL YEAR TO MONTH"
        elif db_type == "YR":
            return "INTERVAL YEAR"
        else:
            return "TD_ANYTYPE"

    @staticmethod
    def _get_basic_columns(columns: Sequence[Mapping[str, str]]) -> Sequence[Column]:
        ret = []
        for c in columns:
            ret.append(Column(c["name"], c["sql_type"]))
        return ret

    def _get_basic_text_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[TextColumn]:
        ret = []
        cursor = self.db_connection.cursor()
        for c in columns:
            cursor.execute(f"""SELECT top {self.top_number}  "{c["name"]}", count(*) from {self.db_name}.{self.table_name}
                        GROUP BY "{c["name"]}"
                        ORDER BY count(*) DESC ;""")
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
        cursor.execute(f"""SELECT {sql} from {self.db_name}.{self.table_name};""")
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
        cursor.execute(f"""SELECT {sql} from {self.db_name}.{self.table_name};""")
        result = cursor.fetchone()

        for i, c in enumerate(columns):
            ret.append(DatetimeColumn(c["name"], c["sql_type"],
                                      str(result[2 * i]),
                                      str(result[2 * i + 1])
                                      ))
        return ret

    def _extract_extended_stats(self, columns_names, columns_sql_types):
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

    def _get_extended_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedColumn]:
        ret = []

        for c in columns:
            cursor = self.db_connection.cursor()

            cursor.execute(f"""select NULLABLE from DBC.COLUMNS where DatabaseName = '{self.db_name}' 
                                and TableName = '{self.table_name}' and ColumnName ='{c["name"]}'; """)
            is_nullable = cursor.fetchone()[0] == 'Y'

            cursor.execute(f"""select count(*) from {self.db_name}.{self.table_name} where "{c["name"]}" is NULL;""")
            nulls_count = cursor.fetchone()[0]

            cursor.execute(f"""SELECT COUNT(*) FROM 
                            (SELECT DISTINCT "{c["name"]}" FROM {self.db_name}.{self.table_name}) AS temp;""")
            distinct_count = cursor.fetchone()[0]

            ret.append(ExtendedNoneTypeColumn(c["name"],
                                              c["sql_type"],
                                              is_nullable,
                                              0 if self.get_rows_count() == 0 else (100 * nulls_count
                                                                                    / self.get_rows_count()),
                                              distinct_count))
        return ret

    def _get_extended_numeric_columns(self, columns: Sequence[Mapping[str, str]]) -> Sequence[ExtendedNumericColumn]:
        ret = []
        for c in columns:
            basic_numeric = self._get_basic_numeric_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]
            extended_stats = self._get_extended_columns([{"name": c["name"], "sql_type": c["sql_type"]}])[0]

            cursor = self.db_connection.cursor()
            quartiles_sql = ", ".join(
                [f'percentile_cont({q}) WITHIN GROUP (ORDER BY "{c["name"]}")' for q in [0.25, 0.5, 0.75]])
            cursor.execute(f"""select {quartiles_sql} FROM {self.db_name}.{self.table_name}""")
            quartiles = cursor.fetchone()

            ret.append(ExtendedNumericColumn(c["name"], c["sql_type"],
                                             basic_numeric.max, basic_numeric.min, basic_numeric.mean,
                                             extended_stats.is_nullable,
                                             extended_stats.null_percent,
                                             extended_stats.unique_number,
                                             quartiles))
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
