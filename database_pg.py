from sqlalchemy import create_engine, text
from config import PG_URI

_engine = create_engine(PG_URI, echo=False)

def exec_script(path):
    with open(path, encoding="latin-1") as f:
        sql = f.read()
    with _engine.begin() as conn:
        conn.exec_driver_sql(sql)

def fetch_all(sql, params=None):
    with _engine.connect() as conn:
        res = conn.execute(text(sql), params or {})
        return [dict(r) for r in res]
