"""
common methods to be used in any db type
"""

from typing import Sequence, Any, Callable

TOO_LONG_TEXT_WARNING = "(Text length is longer than specified max)"


def check_result_empty(result: Sequence[Any]) -> bool:
    return any(map(lambda x: x is None, result))


def get_quartiles(column_name: str, count: int, quartile_sql: Callable, db_connection: Any):
    count = count - 1

    q1 = quartile_sql(0.25, (count % 4) == 0)
    q2 = quartile_sql(0.50, (count % 2) == 0)
    q3 = quartile_sql(0.75, (count % 4) == 0)

    final_sql = q1 + " union all " + q2 + " union all " + q3

    cursor = db_connection.cursor()
    cursor.execute(final_sql)
    results = cursor.fetchall()

    if not len(results):
        return []

    results = [float(r[0]) for r in results]

    quartiles = []
    if count % 4 == 0:
        quartiles.append(results[0])
        if (count % 2) == 0:
            quartiles.append(results[1])
            quartiles.append(results[2])
        else:
            quartiles.append((results[1] + results[2]) / 2)
            quartiles.append(results[3])
    else:
        weight1 = 4 - (count % 4)
        weight3 = count % 4
        quartiles.append(((weight1 * results[0]) + (weight3 * results[1])) / 4)
        if (count % 2) == 0:
            quartiles.append(results[2])
            quartiles.append((weight3 * results[3] + weight1 * results[4]) / 4)
        else:
            quartiles.append((results[2] + results[3]) / 2)
            quartiles.append((weight3 * results[4] + weight1 * results[5]) / 4)
    return quartiles


def get_text_len(column_name: str, table_name: str, db_connection: Any) -> bool:
    cursor = db_connection.cursor()
    check_sql = f"""select max(length("{column_name}")) from {table_name};"""
    cursor.execute(check_sql)
    return cursor.fetchone()[0]
