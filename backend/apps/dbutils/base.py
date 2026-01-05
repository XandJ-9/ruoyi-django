from datetime import datetime, date, time
from decimal import Decimal


class DataSourceExecutor:

    username = None
    password = None
    database = None
    params = None
    host = None
    port = None

    def __init__(self, info):
        self.info = info or {}
        self.conn = None

    def connect(self):
        raise NotImplementedError

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        finally:
            self.conn = None

    def test_connection(self):
        self.connect()
        return True

    def execute_query(self, sql, params=None, page_size=None, offset=None):
        self.connect()
        # 基础校验：仅允许查询类语句，禁止执行非查询（如 INSERT/UPDATE/DELETE/DDL）
        _sql = self._check_sql(sql)
        paginated = False
        if isinstance(page_size, int) and page_size > 0 and isinstance(offset, int) and offset >= 0:
            if not _sql.lower().startswith(('show', 'describe', 'explain')):
                _sql, paginated = self.build_pagination_sql(_sql, int(page_size), int(offset))
        cur = self.conn.cursor()
        try:
            cur.execute(_sql, params or [])
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                # 对返回结果进行时间戳/日期/时间等类型的格式化，遵循统一字符串输出规范
                fmt_rows = [
                    tuple(self._format_cell(v) for v in r)
                    for r in rows
                ]
                data = {"columns": cols, "rows": fmt_rows}
                if paginated:
                    has_more = len(rows) == int(page_size)
                    data["next"] = {"offset": int(offset) + int(page_size), "pageSize": int(page_size)} if has_more else None
                return data
            else:
                self.conn.commit()
                return {"columns": [], "rows": []}
        finally:
            cur.close()

    def build_pagination_sql(self, sql, page_size, offset):
        return sql, False

    def list_tables(self):
        raise NotImplementedError

    def get_table_schema(self, table):
        raise NotImplementedError

    def get_table_info(self, table):
        raise NotImplementedError

    def list_tables_info(self):
        raise NotImplementedError

    def get_databases(self):
        return None

    def _format_cell(self, v):
        # 统一时间戳/日期/时间格式化为字符串；数值保留原样，Decimal 转为 float
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        # 避免 datetime 命中 date 分支，需先判断 datetime
        if isinstance(v, date):
            return v.strftime('%Y-%m-%d')
        if isinstance(v, time):
            return v.strftime('%H:%M:%S')
        if isinstance(v, Decimal):
            return float(v)
        return v

    def _check_sql(self, sql):
        s_raw = (sql or '').strip()  
        if not s_raw:
            raise ValueError('SQL不能为空')
        # 移除注释并转换为小写
        s = '\n'.join([line for line in s_raw.split('\n') if not line.strip().startswith('--')]).strip().lower()
        allowed_prefixes = ('select', 'with', 'show', 'describe', 'explain')
        if s == '':
            raise ValueError('SQL不能为空')
        if not s.startswith(allowed_prefixes):
            raise ValueError('仅允许执行查询语句（SELECT/WITH/SHOW/DESCRIBE/EXPLAIN），禁止执行其他语句')
        return s
