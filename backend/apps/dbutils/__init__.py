from .factory import get_executor


def execute_query(info, sql, params=None):
    ex = get_executor(info)
    try:
        return ex.execute_query(sql, params)
    finally:
        ex.close()


def list_tables(info):
    ex = get_executor(info)
    try:
        return ex.list_tables()
    finally:
        ex.close()


def get_table_schema(info, table):
    ex = get_executor(info)
    try:
        return ex.get_table_schema(table)
    finally:
        ex.close()


def test_connection(info):
    ex = get_executor(info)
    try:
        return ex.test_connection()
    finally:
        ex.close()

