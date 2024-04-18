import json
from typing import Any

_config: Any = None

def _get_config():
    global _config

    if _config is not None:
        return _config

    with open('secrets.json', 'r') as f:
        c = json.load(f)

    _config = c
    return c


def github_token() -> str:
    c = _get_config()
    return c['github_token']
