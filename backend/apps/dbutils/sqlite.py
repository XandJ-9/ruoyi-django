import sqlite3
from .base import DataSourceExecutor


class SqliteExecutor(DataSourceExecutor):
    def connect(self):
        if self.conn:
            return
        db = self.info.get('database') or self.info.get('path')
        if not db:
            raise ValueError('sqlite requires database path')
        self.conn = sqlite3.connect(db)

    def list_tables(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(f"PRAGMA table_info({table})")
            cols = []
            for cid, name, ctype, notnull, dflt_value, pk in cur.fetchall():
                cols.append({
                    'name': name,
                    'type': ctype,
                    'notnull': bool(notnull),
                    'default': dflt_value,
                    'primary': bool(pk),
                })
            return cols
        finally:
            cur.close()

