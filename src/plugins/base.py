from abc import abstractmethod
from typing import Any

from state import AppState


class Plugin:
    @abstractmethod
    async def run(self): ...

    @staticmethod
    def setup(s: AppState) -> Any: ...
