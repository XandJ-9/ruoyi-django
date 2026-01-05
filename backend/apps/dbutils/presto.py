from .base import DataSourceExecutor
import re
import time


class PrestoExecutor(DataSourceExecutor):
    def connect(self):
        if self.conn:
            return
        host = self.info.get('host')
        port = int(self.info.get('port') or 8080)
        user = self.info.get('username') or 'anonymous'
        password = self.info.get('password')
        database = str(self.info.get('database') or '')
        params = self.info.get('params') or {}
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except Exception:
                raise ValueError('Invalid params format, must be a valid JSON string')
        catalog = params.get('catalog')
        schema = params.get('schema')

        if database:
            parts = database.split('.', 1)
            if len(parts) == 2:
                catalog, schema = parts[0], parts[1]
            else:
                schema = parts[0]

        if not catalog:
            catalog = params.get('catalog') or 'hive'
        if not schema:
            schema = params.get('schema') or 'default'

        self.catalog = catalog
        self.schema = schema

        try:
            self.connect_pyhive(host, port, user, catalog, schema)
            self.driver = 'trino'
            return
        except Exception:
            try:
                self.connect_trino(host, port, user, password, catalog, schema, params)
                self.driver = 'presto'
                return
            except Exception:
                raise RuntimeError('presto/trino driver not installed')

    def connect_trino(self, host, port, user, password, catalog, schema, params):
        import trino
        auth = None
        if password:
            BasicAuthentication = getattr(getattr(trino, 'auth', None), 'BasicAuthentication', None)
            if BasicAuthentication is not None:
                auth = BasicAuthentication(user, password)
        self.conn = trino.dbapi.connect(
            host=host,
            port=port,
            user=user,
            catalog=catalog,
            schema=schema,
            http_scheme=params.get('http_scheme', 'http'),
            auth=auth,
        )

    def connect_pyhive(self, host, port, user, catalog, schema):
        from pyhive import presto as _presto
        self.conn = _presto.connect(
            host=host,
            port=port,
            username=user,
            catalog=catalog,
            schema=schema,
        )

    def build_pagination_sql(self, sql, page_size, offset):
        if int(offset) > 0:
            return f"{sql} OFFSET {int(offset)} LIMIT {int(page_size)}", True
        return f"{sql} LIMIT {int(page_size)}", True

    def test_connection(self):
        # 覆盖基础实现：Presto/Trino 连接通常在第一次执行查询时才真正握手
        # 因此仅创建连接对象不足以判断可用性，这里执行一个轻量查询进行校验
        self.connect()
        cur = None
        try:
            cur = self.conn.cursor()
            # 不依赖具体表，仅验证 catalog/schema 与认证/网络是否正常
            cur.execute("SELECT 1")
            cur.fetchone()
            return True
        except Exception as e:
            # 出错时关闭连接，便于后续重试，并抛出明确错误信息
            self.close()
            raise RuntimeError(f"Presto/Trino 连接失败: {e}")
        finally:
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass

    def list_tables(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (self.schema,)
            )
            return [r[0] for r in cur.fetchall()]
        finally:
            cur.close()

    def list_tables_info(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(
                    """
                    SELECT table_name, table_schema, COALESCE(table_comment,'')
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                    """,
                    (self.schema,)
                )
                rs = cur.fetchall()
                rows = []
                for tname, schema, comment in rs:
                    ctime, utime = self._get_table_times(schema, tname)
                    rows.append({
                        'tableName': tname,
                        'databaseName': f"{self.catalog}.{schema}",
                        'comment': comment or '',
                        'createTime': ctime,
                        'updateTime': utime
                    })
                return rows
            except Exception:
                cur.execute(
                    """
                    SELECT table_name, table_schema
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                    """,
                    (self.schema,)
                )
                rs = cur.fetchall()
                rows = []
                for tname, schema in rs:
                    comment = self._get_table_comment(schema, tname)
                    ctime, utime = self._get_table_times(schema, tname)
                    rows.append({
                        'tableName': tname,
                        'databaseName': f"{self.catalog}.{schema}",
                        'comment': comment,
                        'createTime': ctime,
                        'updateTime': utime
                    })
                return rows
        finally:
            cur.close()

    def get_databases(self):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                ORDER BY schema_name
                """
            )
            return [s for (s,) in cur.fetchall()]
        finally:
            cur.close()

    def get_table_schema(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, ordinal_position
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                (self.schema, table)
            )
            cols = []
            for name, dtype, is_nullable, ordinal in cur.fetchall():
                cols.append({
                    'order': int(ordinal),
                    'name': name,
                    'type': dtype,
                    'notnull': str(is_nullable).upper() == 'NO',
                    'default': None,
                    'primary': False,
                    'comment': '',
                })
            return cols
        finally:
            cur.close()

    def get_table_info(self, table):
        self.connect()
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(
                    """
                    SELECT table_name, table_schema, COALESCE(table_comment,'')
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (self.schema, table)
                )
                row = cur.fetchone()
                if not row:
                    comment = ''
                    ctime, utime = '', ''
                    return {
                        'tableName': table,
                        'databaseName': f"{self.catalog}.{self.schema}",
                        'comment': comment,
                        'createTime': ctime,
                        'updateTime': utime
                    }
                tname, schema, comment = row
                ctime, utime = self._get_table_times(schema, tname)
                return {
                    'tableName': tname,
                    'databaseName': f"{self.catalog}.{schema}",
                    'comment': comment or '',
                    'createTime': ctime,
                    'updateTime': utime
                }
            except Exception:
                comment = self._get_table_comment(self.schema, table)
                ctime, utime = self._get_table_times(self.schema, table)
                return {
                    'tableName': table,
                    'databaseName': f"{self.catalog}.{self.schema}",
                    'comment': comment,
                    'createTime': ctime,
                    'updateTime': utime
                }
        finally:
            cur.close()
    def _get_table_comment(self, schema, table):
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(
                    """
                    SELECT COALESCE(table_comment,'')
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (schema, table)
                )
                r = cur.fetchone()
                if r:
                    return r[0] or ''
            except Exception:
                pass
        finally:
            cur.close()
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(f"SHOW CREATE TABLE {schema}.{table}")
                ddl_rows = cur.fetchall()
                ddl = '\n'.join([row[0] if isinstance(row, (list, tuple)) else str(row) for row in ddl_rows])
                m = re.search(r"COMMENT\s*=\s*'([^']*)'", ddl)
                if not m:
                    m = re.search(r"COMMENT\s+'([^']*)'", ddl)
                return m.group(1) if m else ''
            except Exception:
                return ''
        finally:
            cur.close()

    def _get_table_times(self, schema, table):
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(f"SHOW CREATE TABLE {schema}.{table}")
                ddl_rows = cur.fetchall()
                ddl = '\n'.join([row[0] if isinstance(row, (list, tuple)) else str(row) for row in ddl_rows])
                ctime = ''
                utime = ''
                m = re.search(r"'transient_lastDdlTime'\s*=\s*'([0-9]+)'", ddl)
                if not m:
                    m = re.search(r"'transient_lastDdlTime'\s*'([0-9]+)'", ddl)
                if m:
                    try:
                        ts = int(m.group(1))
                        utime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
                    except Exception:
                        utime = ''
                m2 = re.search(r"'created_at'\s*=\s*'([0-9]+)'", ddl)
                if m2:
                    try:
                        ts2 = int(m2.group(1))
                        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts2))
                    except Exception:
                        ctime = ''
                return ctime, utime
            except Exception:
                return '', ''
        finally:
            cur.close()
