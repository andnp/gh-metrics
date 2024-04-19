from typing import Any, Dict, Type, TypeVar
from github import Github

T = TypeVar('T')

class AppState:
    def __init__(self, github: Github):
        self.github = github

        self.plugins: Dict[str, Any] = {}

    def get_plugin(self, name: str, t: Type[T]) -> T:
        s = self.plugins[name]
        assert isinstance(s, t)
        return s
