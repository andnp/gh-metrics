import asyncio

import utils.tsdb as tsdb
from plugins.base import Plugin
from state import AppState
from services.gh import get_repository_names, get_repo_stats

# -----------
# -- State --
# -----------
class RepoState:
    def __init__(self):
        self.con = tsdb.connect('gh_metrics')
        self.cur = self.con.cursor()

        self.cols = [
            'repo TEXT',
            'stars INTEGER',
            'watchers INTEGER',
            'forks INTEGER',
        ]
        self.table_name = 'gh_repo_stats'
        self.write = tsdb.make_writer(
            self.cur,
            self.table_name,
            ['repo', 'stars', 'watchers', 'forks'],
        )

# ------------
# -- Plugin --
# ------------
class RepoStatsPlugin(Plugin):
    def __init__(self, app_state: AppState):
        super().__init__()
        self._s = app_state

    async def run(self):
        self._run_once()
        while True:
            await asyncio.sleep(6 * 60 * 60)
            self._run_once()

    def _run_once(self):
        repo_names = get_repository_names(self._s)
        ps = self._s.get_plugin('repo_stats', RepoState)

        for name in repo_names:
            stats = get_repo_stats(self._s, name)

            sub_name = name.split('/')[-1]
            print(sub_name, 'stats', stats)

            ps.write([
                sub_name,
                stats.stars,
                stats.watchers,
                stats.forks,
            ])


    @staticmethod
    def setup(s: AppState):
        ps = RepoState()
        s.plugins['repo_stats'] = ps

        tables = tsdb.get_all_tables(ps.cur)
        if ps.table_name not in tables:
            tsdb.create_tsdb_table(ps.cur, ps.table_name, ps.cols)

        return RepoStatsPlugin(s)

# -----------
# -- utils --
# -----------
