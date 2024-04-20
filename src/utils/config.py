import tomllib
from typing import Any

_config: Any = None

def _get_config():
    global _config

    if _config is not None:
        return _config

    with open('config.toml', 'rb') as f:
        c = tomllib.load(f)

    _config = c
    return c


def github_token() -> str:
    c = _get_config()
    return c['github_token']

def timescaledb_host() -> str:
    c = _get_config()
    return c['timescaledb']['host']

def timescaledb_port() -> str:
    c = _get_config()
    return c['timescaledb']['port']

def timescaledb_username() -> str:
    c = _get_config()
    return c['timescaledb']['username']

def timescaledb_password() -> str:
    c = _get_config()
    return c['timescaledb']['password']
