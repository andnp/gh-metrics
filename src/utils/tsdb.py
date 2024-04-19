from datetime import datetime
import psycopg2
from typing import Any, List
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import utils.config as Config

# -------------
# -- writers --
# -------------
def record(
    cur: Any,
    table_name: str,
    cols: List[str],
    data: List[Any],
    time: datetime | None = None
):
    if time is None:
        time = datetime.now()

    timestamp = time.isoformat()
    data = [maybe_quote(timestamp)] + [ maybe_quote(d) for d in data ]

    cols = ['time'] + cols

    data_str = ','.join(['%s'] * len(data))
    cols_str = ','.join(cols)

    query = f'INSERT INTO {table_name} ({cols_str}) VALUES ({data_str});'
    cur.execute(query, data)
    cur.connection.commit()

def make_writer(cur: Any, table_name: str, cols: List[str]):
    def _writer(data: List[Any], time: datetime | None = None):
        return record(cur, table_name, cols, data, time=time)

    return _writer


# --------------
# -- builders --
# --------------
def create_database(
    db_name: str,
):
    user = Config.timescaledb_username()
    host = Config.timescaledb_host()
    password = Config.timescaledb_password()
    port = Config.timescaledb_port()

    con = psycopg2.connect(f'postgres://{user}:{password}@{host}:{port}')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    try:
        cur.execute(f"CREATE DATABASE {db_name};")
        cur.close()
    except Exception as e:
        print(e)

def create_tsdb_table(
    cur: Any,
    table_name: str,
    cols: List[str],
):
    cols = ['time TIMESTAMPTZ NOT NULL'] + cols
    col_str = ','.join(cols)

    query_str = f'CREATE TABLE {table_name} ({col_str});'
    cur.execute(query_str)

    hyper_query_str = f"SELECT create_hypertable('{table_name}', by_range('time'));"
    cur.execute(hyper_query_str)

    cur.connection.commit()

# -------------
# -- getters --
# -------------
def get_all_tables(cur: Any):
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return [t[0] for t in cur.fetchall()]

def get_all_rows(cur: Any, table_name: str):
    cur.execute(f'SELECT * FROM {table_name}')
    return cur.fetchall()

# -----------
# -- utils --
# -----------
def maybe_quote(d: Any):
    if isinstance(d, str):
        return f"'{d}'"

    return d
