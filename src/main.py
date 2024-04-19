import asyncio
from github import Github
from github import Auth

from plugins.traffic import Traffic
from state import AppState
import utils.config as Config

async def run():
    await asyncio.sleep(25)

    token = Config.github_token()
    auth = Auth.Token(token)

    g = Github(auth=auth)

    state = AppState(g)
    traffic = Traffic.setup(state)

    await asyncio.gather(
        traffic.run(),
    )

    g.close()


asyncio.run(run())
