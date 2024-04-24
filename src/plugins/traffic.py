import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, List

import utils.tsdb as tsdb
from plugins.base import Plugin
from state import AppState
from services.gh import get_repository_names
from github.View import View

# -----------
# -- State --
# -----------
class TrafficState:
    def __init__(self):
        self.cols = [
            'repo TEXT',
            'unique_views INTEGER',
            'total_views INTEGER',
        ]
        self.col_names = [c.split(' ')[0] for c in self.cols]
        self.table_name = 'gh_traffic'

# ------------
# -- Plugin --
# ------------
class Traffic(Plugin):
    def __init__(self, app_state: AppState):
        super().__init__()
        self._s = app_state
        ps = self._s.get_plugin('traffic', TrafficState)
        self.write = tsdb.make_writer(self._s.cur, ps.table_name, ps.col_names)

    async def run(self):
        self._fill_old()
        while True:
            tom = time_til_tomorrow()
            print('Logging views in ', tom)
            await asyncio.sleep(tom + 600)
            self._fill_old()

    def _fill_old(self):
        repo_names = get_repository_names(self._s)
        for name in repo_names:
            views = get_all_views(self._s, name)
            for v in views:
                print(name, v)
                self._save_view(name, v)

    def _save_view(self, name: str, v: View):
        ps = self._s.get_plugin('traffic', TrafficState)

        sub_name = name.split('/')[-1]

        row_exists = tsdb.row_exists(
            self._s.cur,
            ps.table_name,
            cols=['repo'],
            data=[sub_name],
            timestamp=v.timestamp,
            time_fuzz='10 hours',
        )

        if not row_exists:
            print('Adding row', name, v)
            return self.write(
                [sub_name, v.uniques, v.count],
                v.timestamp,
            )

        modified_rows = tsdb.modify_row(
            self._s.cur,
            ps.table_name,
            id_cols=['repo'],
            id_values=[sub_name],
            mod_cols=['unique_views', 'total_views'],
            mod_values=[v.uniques, v.count],
            timestamp=v.timestamp,
            time_fuzz='10 hours',
        )

        if len(modified_rows) > 1:
            print(f'WARNING: found multiple rows {sub_name} {v.timestamp}')

    @staticmethod
    def setup(s: AppState):
        ps = TrafficState()
        s.plugins['traffic'] = ps

        tables = tsdb.get_all_tables(s.cur)
        if ps.table_name not in tables:
            tsdb.create_tsdb_table(s.cur, ps.table_name, ps.cols)

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
    if len(views) == 0:
        return views

    views = sorted(views, key=lambda v: v.timestamp)
    all_views: List[View] = []
    last_time = views[0].timestamp
    for v in views:
        all_views.append(v)

        d = v.timestamp - last_time
        if d.days < 2:
            continue

        for i in range(1, d.days - 1, 1):
            view: Any = MyView(
                timestamp=v.timestamp - timedelta(days=i),
                count=0,
                uniques=0,
            )
            all_views.append(view)

        last_time = v.timestamp

    return all_views

@dataclass
class MyView:
    timestamp: datetime
    count: int
    uniques: int
