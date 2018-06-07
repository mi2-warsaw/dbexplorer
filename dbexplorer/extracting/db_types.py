import abc
from typing import Mapping, Sequence, Any

QUARTILES = [0.25, 0.5, 0.75]


class ColumnType:
    """
    Simple column types
    """
    NUMERIC = 1
    TEXT = 2
    DATETIME = 3
    NONE = 4


def to_key_value(data: Mapping) -> Sequence[Mapping[str, Any]]:
    """
    converting dict to a form that will be used in visualizer (form: {"key": "name", "value", "hello"})
    :param data: data to be converted
    :return: converted data
    """
    ret = []
    for key, value in data.items():
        ret.append({
            "key": key,
            "value": value
        })
    return ret


class Column:
    """
    Base class for all columns.
    """

    def __init__(self, name: str, sql_type: str):
        """
        :param name: name of column
        :param sql_type: sql type of column
        """
        self._name = name
        self._sql_type = sql_type

    @property
    def name(self) -> str:
        """
        :return: name of column
        """
        return self._name

    @property
    def sql_type(self) -> str:
        """
        :return: sql type of column
        """
        return self._sql_type

    def to_dict(self) -> Mapping[str, Sequence[Mapping[str, Any]]]:
        """
        :return:  Representation of extracted column data
        """
        return {
            "data": to_key_value({
                "Name": self.name,
                "SQL Type": self.sql_type
            })
        }


class Table:
    """
    Table representation
    """

    def __init__(self, name: str, rows_count: int, columns: Sequence[Column]):
        """
        :param name: name of table
        :param rows_count: rows number in table
        :param columns: extracted columns
        """
        self._name = name
        self._rows_count = rows_count
        self._columns = columns

    @property
    def name(self) -> str:
        return self._name

    @property
    def rows_count(self) -> int:
        return self._rows_count

    @property
    def columns(self) -> Sequence[Column]:
        return self._columns

    def to_dict(self) -> Mapping:
        """
        :return:  Representation of extracted table data
        """
        return {
            "name": self.name,
            "records": self.rows_count,
            "columns": [column.to_dict() for column in self.columns]
        }


# all derived classes are properly explained by field names and full typing information

class TextColumn(Column):

    def __init__(self, name: str, sql_type: str, top: Sequence[str], top_values: Sequence[int]):
        super(TextColumn, self).__init__(name, sql_type)
        self._top = top
        self._top_values = top_values

    @property
    def top(self) -> Sequence[str]:
        return self._top

    @property
    def top_values(self) -> Sequence[str]:
        return self._top_values

    def to_dict(self) -> Mapping:
        ret = super(TextColumn, self).to_dict()
        ret["type"] = "character"
        ret["data"] += to_key_value({
            "The most common": self.top,
            "Counts of the most common values": self.top_values
        })
        return ret


class NumericColumn(Column):

    def __init__(self, name: str, sql_type: str, maximum: float, minimum: float, mean: float):
        super(NumericColumn, self).__init__(name, sql_type)
        self._maximum = maximum
        self._minimum = minimum
        self._mean = mean

    @property
    def max(self) -> float:
        return self._maximum

    @property
    def min(self) -> float:
        return self._minimum

    @property
    def mean(self) -> float:
        return self._mean

    def to_dict(self) -> Mapping:
        ret = super(NumericColumn, self).to_dict()
        ret["type"] = "numeric"
        ret["data"] += to_key_value({
            "Minimum": self.min,
            "Maximum": self.max,
            "Mean": self.mean
        })
        return ret


class DatetimeColumn(Column):

    def __init__(self, name: str, sql_type: str, maximum: str, minimum: str):
        super(DatetimeColumn, self).__init__(name, sql_type)
        self._maximum = maximum
        self._minimum = minimum

    @property
    def name(self) -> str:
        return self._name

    @property
    def max(self) -> str:
        return self._maximum

    @property
    def min(self) -> str:
        return self._minimum

    def to_dict(self) -> Mapping:
        ret = super(DatetimeColumn, self).to_dict()
        ret["type"] = "datetime"
        ret["data"] += to_key_value({
            "Minimum": self.min,
            "Maximum": self.max,
        })
        return ret


class ExtendedColumn(metaclass=abc.ABCMeta):

    def __init__(self, is_nullable: bool, nulls_percent: float, unique_count: int):
        self._is_nullable = is_nullable
        self._null_percent = nulls_percent
        self._unique_number = unique_count

    @property
    def is_nullable(self) -> bool:
        return self._is_nullable

    @property
    def null_percent(self) -> float:
        return self._null_percent

    @property
    def unique_number(self) -> int:
        return self._unique_number

    def to_dict(self) -> Mapping:
        return to_key_value({
            "Nulls possible": self.is_nullable,
            "Empty": f"{self.null_percent:.2f} %",
            "Distinct": self.unique_number
        })


class ExtendedNoneTypeColumn(ExtendedColumn, Column):
    def __init__(self, name: str, sql_type: str, is_nullable: bool, nulls_percent: float, unique_count: int):
        ExtendedColumn.__init__(self, is_nullable, nulls_percent, unique_count)
        Column.__init__(self, name, sql_type)

    def to_dict(self) -> Mapping:
        ret = Column.to_dict(self)
        ret["data"] += ExtendedColumn.to_dict(self)
        return ret


class ExtendedTextColumn(ExtendedColumn, TextColumn):

    def __init__(self, name: str, sql_type: str, top: Sequence[str], top_values: Sequence[str], is_nullable: bool,
                 nulls_percent: float, unique_count):
        ExtendedColumn.__init__(self, is_nullable, nulls_percent, unique_count)
        TextColumn.__init__(self, name, sql_type, top, top_values)

    def to_dict(self) -> Mapping:
        ret = TextColumn.to_dict(self)
        ret["data"] += ExtendedColumn.to_dict(self)
        return ret


class ExtendedNumericColumn(ExtendedColumn, NumericColumn):

    def __init__(self, name: str, sql_type: str, maximum: float, minimum: float, mean: float, is_nullable: bool,
                 nulls_percent: float, unique_count: int, quartiles: Sequence[float]):
        ExtendedColumn.__init__(self, is_nullable, nulls_percent, unique_count)
        NumericColumn.__init__(self, name, sql_type, maximum, minimum, mean)
        self._quartiles = quartiles

    @property
    def quartiles(self) -> Sequence[float]:
        return self._quartiles

    def to_dict(self) -> Mapping:
        ret = NumericColumn.to_dict(self)
        ret["data"] += ExtendedColumn.to_dict(self)
        quartiles = {}
        for i, quartile in enumerate(QUARTILES):
            quartiles[f"Quantile {quartile:.2f}"] = self.quartiles[i] if len(self.quartiles) else None
        ret["data"] += to_key_value(quartiles)
        return ret


class ExtendedDatetimeColumn(ExtendedColumn, DatetimeColumn):

    def __init__(self, name: str, sql_type: str, maximum: float, minimum: float, is_nullable: bool,
                 nulls_percent: float, unique_count: int):
        ExtendedColumn.__init__(self, is_nullable, nulls_percent, unique_count)
        DatetimeColumn.__init__(self, name, sql_type, maximum, minimum)

    def to_dict(self) -> Mapping:
        ret = DatetimeColumn.to_dict(self)
        ret["data"] += ExtendedColumn.to_dict(self)
        return ret
