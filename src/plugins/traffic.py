import asyncio
import psycopg2
from datetime import datetime, timedelta

import utils.tsdb as tsdb
import utils.config as Config
from plugins.base import Plugin
from state import AppState

# -----------
# -- State --
# -----------
class TrafficState:
    def __init__(self):
        user = Config.timescaledb_username()
        password = Config.timescaledb_password()
        host = Config.timescaledb_host()
        port = Config.timescaledb_port()

        conn_url = f'postgres://{user}:{password}@{host}:{port}/gh_metrics'
        self.con = psycopg2.connect(conn_url)
        self.cur = self.con.cursor()

        self.cols = [
            'repo TEXT',
            'unique_views INTEGER',
            'total_views INTEGER',
        ]
        self.table_name = 'gh_traffic'
        self.write = tsdb.make_writer(self.cur, self.table_name, ['repo', 'unique_views', 'total_views'])

# ------------
# -- Plugin --
# ------------
class Traffic(Plugin):
    def __init__(self, app_state: AppState):
        super().__init__()
        self._s = app_state

    async def run(self):
        self._fill_old()
        while True:
            tom = time_til_tomorrow()
            await asyncio.sleep(tom + 600)
            self._run_once()

    def _run_once(self):
        repo_names = get_repository_names(self._s)

        for name in repo_names:
            v = get_yesterday_views(self._s, name)
            print(name, v)
            if v is None:
                continue

            self._save_view(name, v)

    def _fill_old(self):
        ps = self._s.get_plugin('traffic', TrafficState)
        old_data = tsdb.get_all_rows(ps.cur, ps.table_name)
        print('old_data', len(old_data))

        if len(old_data) > 0:
            return

        print('grabbing old data')
        repo_names = get_repository_names(self._s)
        for name in repo_names:
            views = get_all_views(self._s, name)
            for v in views:
                print(name, v)
                self._save_view(name, v)

    def _save_view(self, name: str, v):
        ps = self._s.get_plugin('traffic', TrafficState)

        sub_name = name.split('/')[-1]
        ps.write([sub_name, v.uniques, v.count], time=v.timestamp)


    @staticmethod
    def setup(s: AppState):
        ps = TrafficState()
        s.plugins['traffic'] = ps

        tables = tsdb.get_all_tables(ps.cur)
        if ps.table_name not in tables:
            tsdb.create_tsdb_table(ps.cur, ps.table_name, ps.cols)

        return Traffic(s)

# -----------
# -- utils --
# -----------
def time_til_tomorrow(hour: int = 1):
    dt = datetime.now()
    tom = dt + timedelta(days=1)
    tom = tom.replace(hour=hour, minute=0, second=0)

    d = tom - dt
    return d.total_seconds()

def get_repository_names(s: AppState):
    repos = (
        s.github
        .get_organization('Amii-Open-Source')
        .get_repos(type='public')
    )
    return [r.full_name for r in repos]

def get_yesterday_views(s: AppState, name: str):
    views = get_all_views(s, name)
    today = datetime.now()
    for v in views:
        timestamp = v.timestamp.replace(tzinfo=None)
        d = today - timestamp

        if d.days == 1:
            return v

    return

def get_all_views(s: AppState, name: str):
    r = s.github.get_repo(name, lazy=True)

    # TODO: this can raise an exception if user is not read/write
    # on repo
    traffic_data = r.get_views_traffic()
    if traffic_data is None:
        # TODO: do logging and handle gracefully
        raise Exception()

    views = traffic_data['views']
    assert isinstance(views, list)

    return views
