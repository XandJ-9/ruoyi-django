from .base import DataSourceExecutor


class MysqlExecutor(DataSourceExecutor):
    def connect(self):
        if self.conn:
            return
        try:
            import pymysql as mysql
        except Exception:
            try:
                import mysql.connector as mysql
            except Exception:
                raise RuntimeError('mysql driver not installed')
        self.conn = mysql.connect(
            host=self.info.get('host'),
            port=int(self.info.get('port') or 3306),
            user=self.info.get('username'),
            password=self.info.get('password'),
            database=self.info.get('database'),
        )

    def list_tables(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute('SHOW TABLES')
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(f'DESCRIBE `{table}`')
            cols = []
            for name, ctype, null, key, default, extra in cur.fetchall():
                cols.append({
                    'name': name,
                    'type': ctype,
                    'notnull': (null == 'NO'),
                    'default': default,
                    'primary': (key == 'PRI'),
                    'extra': extra,
                })
            return cols
        finally:
            cur.close()

