from .sqlite import SqliteExecutor
from .mysql import MysqlExecutor
from .postgres import PostgresExecutor


def get_executor(info):
    t = str((info or {}).get('type', '')).lower()
    if t == 'sqlite':
        return SqliteExecutor(info)
    if t in ('mysql', 'mariadb'):
        return MysqlExecutor(info)
    if t in ('postgres', 'postgresql'):
        return PostgresExecutor(info)
    raise ValueError('unsupported datasource type')

