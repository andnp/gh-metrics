import asyncio
from github import Github
from github import Auth

from plugins.traffic import Traffic
from plugins.repo_stats import RepoStatsPlugin

from state import AppState
from utils.config import get_config
import utils.tsdb as tsdb

async def run():
    await asyncio.sleep(25)

    config = get_config()
    auth = Auth.Token(config.github_token)

    g = Github(auth=auth)

    tsdb.create_database(config, 'gh_metrics')
    con = tsdb.connect(config, 'gh_metrics')

    state = AppState(config, con, g)
    traffic = Traffic.setup(state)
    repo_stats = RepoStatsPlugin.setup(state)

    await asyncio.gather(
        traffic.run(),
        repo_stats.run(),
    )

    g.close()


asyncio.run(run())
