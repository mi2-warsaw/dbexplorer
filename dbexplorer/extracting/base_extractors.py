from abc import ABCMeta, abstractmethod
from dbexplorer.extracting.db_types import Table, Column, ColumnType
from typing import Sequence, Mapping, Any, Tuple, Type
import logging


class DbExtractor(metaclass=ABCMeta):
    """
    Base class for any database extractor. It states all methods that extractor needs to implement.
    If an extractor derives from this class and implements all abstract methods it can be used in the whole workflow.
    If new db type needs to be taken into account, one must create a derived class.
    All already create derived classes follow this structure.
    """

    def __init__(self, server_address: str, port: int, db_name: str, user: str, password: str, extended: bool,
                 top_number: int, schema: str, odbc_driver: str):
        """
        :param server_address: address of db server (in form: "192.168.1.1")
        :param port: port of the database
        :param db_name: database name
        :param user: on behalf of this user the connection will be established
        :param password: password for the user
        :param extended: if the info should be in the extended form
        :param top_number: number of most common values to extract
        :param schema: schema name (may be ignored if db type does not use it)
        :param odbc_driver: driver (may be ignored if db type does not use it)
        """
        self.db_name = db_name
        self.odbc_driver = odbc_driver
        self.db_connection = self.connect(server_address, port, db_name, user, password)
        self.extended = extended
        self.top_number = top_number
        self.schema = schema

    def get_tables(self) -> Sequence[Table]:
        """
        Method extract all tables in the database
        :return: sequence of Tables
        """

        ret = []

        for table_name in self._get_tables_names():
            try:
                ret.append(self._get_table(table_name))
            except Exception as e:
                logging.warning(f'Failed to extract info from table {table_name}: ' + str(e))

        return ret

    def _get_table(self, name: str) -> Table:
        """
        Method controls the workflow of extracting single db info
        :param name: name of table to be extracted
        :return: Single table info
        """
        extractor = self.table_extractor_class(self.db_connection, name, self.extended, self.top_number, self.db_name)
        return Table(name, extractor.get_rows_count(), extractor.get_columns())

    def extract_to_dict(self) -> Mapping:
        """
        Getting dictionary that can be interpreted by the visualizer
        :return: Dictionary of extracted database info
        """
        return {
            "scheme": "SchemeName",
            "database": self.db_name,
            "tables": [table.to_dict() for table in self.get_tables()]
        }

    @abstractmethod
    def connect(self, server_address: str, port: int, db_name: str, user: str, password: str) -> Any:
        """
        create a connection to db with given params
        :param server_address: address of db server (in form: "192.168.1.1")
        :param port: port of the database
        :param db_name: database name
        :param user: on behalf of this user the connection will be established
        :param password: password for the user
        :return: connection object, proper for db type
        """
        raise NotImplemented

    @abstractmethod
    def _get_tables_names(self) -> Sequence[str]:
        """
        get all table names in db
        :return: List of table names
        """
        raise NotImplemented

    @property
    @abstractmethod
    def table_extractor_class(self) -> Type['TableExtractor']:
        """
        getting proper extractor for db type
        :return: type of proper table extractor
        """
        raise NotImplemented


class TableExtractor(metaclass=ABCMeta):
    """
    Base class for any table extractor. It states all methods that table extractor needs to implement.
    It is used by database extractor to extract single table.
    All already create derived classes follow this structure.
    """

    def __init__(self, db_connection: Any, table_name: str, extended: bool, top_number: int, db_name: str):
        """
        :param db_connection: object of db connection proper for db type
        :param table_name: table name to be extracted
        :param extended:  if the info should be in the extended form
        :param top_number: number of most common values to extract
        :param db_name: database name
        """
        self.db_connection = db_connection
        self.table_name = table_name
        self.extended = extended
        self.top_number = top_number
        self.db_name = db_name

    def get_columns(self) -> Sequence[Column]:
        """
        get all columns infos in the table
        :return: Sequence of column infos
        """
        return self._extract_columns_stats()

    def _extract_columns_stats(self) -> Sequence[Column]:
        """
        Private extracting method, to be overridden if required
        :return: Sequence of column infos
        """
        columns_names, columns_sql_types = self._extract_column_names_and_types()

        if self.extended:
            return self._extract_extended_stats(columns_names, columns_sql_types)

        return self._extract_basic_stats(columns_names, columns_sql_types)

    @abstractmethod
    def _map_sql_types(self, sql_type: str) -> ColumnType:
        """
        Mapping sql to one of (ColumnType - NUMERIC, TEXT, DATETIME)
        given sql_type should return simple type
        :param sql_type: type to be converted
        :return: Simple column for given sql type
        """
        raise NotImplementedError

    @abstractmethod
    def get_rows_count(self) -> int:
        """
        Extract number of rows for table
        :return: number of rows in the table
        """
        raise NotImplementedError

    @abstractmethod
    def _extract_basic_stats(self, columns_names: Sequence[str], columns_sql_types: Sequence[str]) \
            -> Sequence[Column]:
        """
        Extract basic info form db and return list of appropriate columns
        (types NumericColumn, TextColumn, DatetimeColumn)
        :param columns_names:
        :param columns_sql_types:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _extract_extended_stats(self, columns_names: Sequence[str], columns_sql_types: Sequence[str]) \
            -> Sequence[Column]:
        """
        Extract extended info from db and return list of appropriate columns
        (types ExtendedNumericColumn, ExtendedTextColumn, ExtendedDatetimeColumn)
        """
        raise NotImplementedError

    @abstractmethod
    def _extract_column_names_and_types(self) -> Tuple[Sequence[str], Sequence[str]]:
        """
        # extract names and sql_types of columns
        :return: tuple of column names and corresponding types
        """
        raise NotImplementedError
