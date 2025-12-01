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

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT a.attname, t.typname, a.attnotnull, a.attnum IN (
                    SELECT i.indkey[0] FROM pg_index i WHERE i.indrelid = a.attrelid AND i.indisprimary
                ) AS is_primary
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_type t ON a.atttypid = t.oid
                WHERE c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped
                ORDER BY a.attnum
                """,
                (table,)
            )
            cols = []
            for name, typ, notnull, primary in cur.fetchall():
                cols.append({
                    'name': name,
                    'type': typ,
                    'notnull': bool(notnull),
                    'default': None,
                    'primary': bool(primary),
                })
            return cols
        finally:
            cur.close()

