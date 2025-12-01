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
        # 自动在 SELECT 语句后追加 LIMIT/OFFSET 以实现简单分页
        paginated = False
        _sql = sql
        if isinstance(page_size, int) and page_size > 0 and isinstance(offset, int) and offset >= 0:
            s = (sql or '').strip().lower()
            if s.startswith('select'):
                _sql = f"{sql} LIMIT {int(page_size)} OFFSET {int(offset)}"
                paginated = True
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

    def list_tables(self):
        raise NotImplementedError

    def get_table_schema(self, table):
        raise NotImplementedError

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

