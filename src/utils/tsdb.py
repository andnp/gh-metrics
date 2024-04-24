import psycopg2
from datetime import datetime
from typing import Any, List
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2._psycopg import cursor

from utils.config import Config

# -------------
# -- writers --
# -------------
def record(
    cur: cursor,
    table_name: str,
    cols: List[str],
    data: List[Any],
    time: datetime | None = None
):
    if time is None:
        time = datetime.now()

    timestamp = time.isoformat()
    data = [timestamp] + data

    cols = ['time'] + cols

    data_str = ','.join(['%s'] * len(data))
    cols_str = ','.join(cols)

    query = f'INSERT INTO {table_name} ({cols_str}) VALUES ({data_str});'
    cur.execute(query, data)
    cur.connection.commit()

def make_writer(cur: cursor, table_name: str, cols: List[str]):
    def _writer(data: List[Any], time: datetime | None = None):
        return record(cur, table_name, cols, data, time=time)

    return _writer


# --------------
# -- builders --
# --------------
def create_database(
    config: Config,
    db_name: str,
):
    con = connect(config)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    try:
        cur.execute(f"CREATE DATABASE {db_name};")
        cur.close()
    except Exception as e:
        print(e)

def create_tsdb_table(
    cur: cursor,
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

def connect(config: Config, db_name: str | None = None):
    if db_name is None:
        db_name = ''
    else:
        db_name = '/' + db_name

    c = config.timescaledb
    con = psycopg2.connect(f'postgres://{c.username}:{c.password}@{c.host}:{c.port}{db_name}')
    return con

# -------------
# -- getters --
# -------------
def get_all_tables(cur: cursor):
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return [t[0] for t in cur.fetchall()]

def get_all_rows(cur: cursor, table_name: str):
    cur.execute(f'SELECT * FROM {table_name}')
    return cur.fetchall()

def row_exists(
    cur: cursor,
    table_name: str,
    cols: List[str],
    data: List[Any],
    timestamp: datetime | None = None,
    time_fuzz: str | None = None,
):
    rows = get_rows(
        cur=cur,
        table_name=table_name,
        cols=cols,
        data=data,
        timestamp=timestamp,
        time_fuzz=time_fuzz,
    )

    if len(rows) > 1:
        print('WARNING: more than one row exists', table_name, data)

    return len(rows) > 0

def get_rows(
    cur: cursor,
    table_name: str,
    cols: List[str],
    data: List[Any],
    timestamp: datetime | None = None,
    time_fuzz: str | None = None,
):
    cond = make_cond_with_time(cols, timestamp, time_fuzz)
    query = f'SELECT * FROM {table_name} WHERE {cond}'
    cur.execute(query, data)
    rows = cur.fetchall()

    return rows

# -----------
# -- utils --
# -----------
def maybe_quote(d: Any):
    if isinstance(d, str):
        return f"'{d}'"

    return d

def make_cond(cols: List[str]):
    parts = []
    for c in cols:
        p = f'{c}=%s'
        parts.append(p)

    return ' AND '.join(parts)

def make_cond_with_time(
    cols: List[str],
    timestamp: datetime | None = None,
    time_fuzz: str | None = None,
):
    cond = make_cond(cols)

    if timestamp is not None and time_fuzz is None:
        cond += f" AND time=timestamp '{timestamp}'"
    elif timestamp is not None and time_fuzz is not None:
        cond += f" AND time BETWEEN (timestamp '{timestamp}' - interval '{time_fuzz}') AND (timestamp '{timestamp}' + interval '{time_fuzz}')"

    return cond
