from typing import Any, Dict, Type, TypeVar
from github import Github
from psycopg2._psycopg import connection

from utils.config import Config

T = TypeVar('T')

class AppState:
    def __init__(self, config: Config, con: connection, github: Github):
        self.config = config
        self.github = github
        self.con = con
        self.cur = con.cursor()

        self.plugins: Dict[str, Any] = {}

    def get_plugin(self, name: str, t: Type[T]) -> T:
        s = self.plugins[name]
        assert isinstance(s, t)
        return s
