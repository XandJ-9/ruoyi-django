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

    def list_tables_info(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            rows = []
            dbname = self.info.get('database') or self.info.get('path') or ''
            for (tname,) in cur.fetchall():
                rows.append({
                    'tableName': tname,
                    'databaseName': dbname,
                    'comment': '',
                    'createTime': '',
                    'updateTime': ''
                })
            return rows
        finally:
            cur.close()

    def get_databases(self):
        # SQLite 无数据库列表概念
        return None

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(f"PRAGMA table_info({table})")
            cols = []
            rows = cur.fetchall()
            for idx, (cid, name, ctype, notnull, dflt_value, pk) in enumerate(rows, start=1):
                cols.append({
                    'order': idx,
                    'name': name,
                    'type': ctype,
                    'notnull': bool(notnull),
                    'default': dflt_value,
                    'primary': bool(pk),
                    'comment': '',
                })
            return cols
        finally:
            cur.close()

    def get_table_info(self, table):
        # SQLite 不提供表级创建/修改时间与注释，尽量返回基本信息
        dbname = self.info.get('database') or self.info.get('path') or ''
        return {
            'tableName': table,
            'databaseName': dbname,
            'comment': '',
            'createTime': '',
            'updateTime': ''
        }

    def build_pagination_sql(self, sql, page_size, offset):
        return f"{sql} LIMIT {int(page_size)} OFFSET {int(offset)}", True
