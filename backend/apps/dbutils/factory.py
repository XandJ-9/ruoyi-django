from .sqlite import SqliteExecutor
from .mysql import MysqlExecutor
from .postgres import PostgresExecutor
from .presto import PrestoExecutor


def get_executor(info):
    t = str((info or {}).get('type', '')).lower()
    if t == 'sqlite':
        return SqliteExecutor(info)
    if t in ('mysql', 'mariadb', 'starrocks'):
        return MysqlExecutor(info)
    if t in ('postgres', 'postgresql'):
        return PostgresExecutor(info)
    if t in ('presto', 'trino'):
        return PrestoExecutor(info)
    raise ValueError('unsupported datasource type')
