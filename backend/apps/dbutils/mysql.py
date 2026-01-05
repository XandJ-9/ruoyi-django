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

    def list_tables_info(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT TABLE_NAME, TABLE_SCHEMA, TABLE_COMMENT, CREATE_TIME, UPDATE_TIME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME
                """
            )
            rows = []
            for tname, dbname, comment, ctime, utime in cur.fetchall():
                rows.append({
                    'tableName': tname,
                    'databaseName': dbname,
                    'comment': comment or '',
                    'createTime': self._format_cell(ctime) if ctime else '',
                    'updateTime': self._format_cell(utime) if utime else ''
                })
            return rows
        finally:
            cur.close()

    def get_databases(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute('SHOW DATABASES')
            system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
            return [db for (db,) in cur.fetchall() if db not in system_dbs]
        finally:
            cur.close()

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, COLUMN_COMMENT
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
                """,
                (table,)
            )
            cols = []
            rows = cur.fetchall()
            for idx, (name, ctype, is_nullable, default, key, comment) in enumerate(rows, start=1):
                cols.append({
                    'order': idx,
                    'name': name,
                    'type': ctype,
                    'notnull': (is_nullable == 'NO'),
                    'default': default,
                    'primary': (key == 'PRI'),
                    'comment': comment or '',
                })
            return cols
        finally:
            cur.close()

    def get_table_info(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT TABLE_NAME, TABLE_SCHEMA, TABLE_COMMENT, CREATE_TIME, UPDATE_TIME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                """,
                (table,)
            )
            row = cur.fetchone()
            if not row:
                return {
                    'tableName': table,
                    'databaseName': self.info.get('database') or '',
                    'comment': '',
                    'createTime': '',
                    'updateTime': ''
                }
            tname, dbname, comment, ctime, utime = row
            return {
                'tableName': tname,
                'databaseName': dbname,
                'comment': comment or '',
                'createTime': self._format_cell(ctime) if ctime else '',
                'updateTime': self._format_cell(utime) if utime else ''
            }
        finally:
            cur.close()

    def build_pagination_sql(self, sql, page_size, offset):
        return f"{sql} LIMIT {int(offset)},{int(page_size)}", True
