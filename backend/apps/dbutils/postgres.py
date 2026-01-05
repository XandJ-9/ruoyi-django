from .base import DataSourceExecutor


class PostgresExecutor(DataSourceExecutor):
    def connect(self):
        if self.conn:
            return
        try:
            import psycopg2
        except Exception:
            raise RuntimeError('postgres driver not installed')
        self.conn = psycopg2.connect(
            host=self.info.get('host'),
            port=int(self.info.get('port') or 5432),
            user=self.info.get('username'),
            password=self.info.get('password'),
            dbname=self.info.get('database'),
        )

    def list_tables(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY tablename")
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()

    def list_tables_info(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT c.relname,
                       current_database() AS dbname,
                       obj_description(c.oid, 'pg_class') AS comment
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind IN ('r','p') AND n.nspname NOT IN ('pg_catalog','information_schema')
                ORDER BY c.relname
                """
            )
            rows = []
            for tname, dbname, comment in cur.fetchall():
                rows.append({
                    'tableName': tname,
                    'databaseName': dbname,
                    'comment': comment or '',
                    'createTime': '',
                    'updateTime': ''
                })
            return rows
        finally:
            cur.close()

    def get_databases(self):
        # Postgres 在连接上下文使用单库，跨库需新连接；此处返回 None 表示无数据库选择
        # return None
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT current_database()")
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT a.attname, t.typname, a.attnotnull,
                       a.attnum IN (
                           SELECT i.indkey[0] FROM pg_index i WHERE i.indrelid = a.attrelid AND i.indisprimary
                       ) AS is_primary,
                       col_description(c.oid, a.attnum) AS comment
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_type t ON a.atttypid = t.oid
                WHERE c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped
                ORDER BY a.attnum
                """,
                (table,)
            )
            cols = []
            rows = cur.fetchall()
            for idx, (name, typ, notnull, primary, comment) in enumerate(rows, start=1):
                cols.append({
                    'order': idx,
                    'name': name,
                    'type': typ,
                    'notnull': bool(notnull),
                    'default': None,
                    'primary': bool(primary),
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
                SELECT c.relname,
                       current_database() AS dbname,
                       obj_description(c.oid, 'pg_class') AS comment
                FROM pg_class c
                WHERE c.relkind IN ('r','p') AND c.relname = %s
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
            tname, dbname, comment = row
            return {
                'tableName': tname,
                'databaseName': dbname,
                'comment': comment or '',
                'createTime': '',
                'updateTime': ''
            }
        finally:
            cur.close()

    def build_pagination_sql(self, sql, page_size, offset):
        return f"{sql} LIMIT {int(page_size)} OFFSET {int(offset)}", True
