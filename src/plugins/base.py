import asyncio
import time
from abc import abstractmethod
from typing import Any

from state import AppState
from utils.logger import logger

class Plugin:
    @abstractmethod
    async def run(self): ...

    @staticmethod
    def setup(s: AppState) -> Any: ...


    async def run_forever(self):
        fails = 0
        avg_fail_time = 0
        while True:
            start = time.time()
            try:
                await self.run()
            except Exception:
                logger.exception('Caught plugin error -- retrying')

            fails += 1
            fail_time = time.time()
            avg_fail_time = 0.75 * avg_fail_time + 0.25 * (fail_time - start)

            if fails > 3 and avg_fail_time < 60:
                raise Exception('Plugin continually failed. Giving up.')

            await asyncio.sleep(5)
