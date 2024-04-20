from dataclasses import dataclass
import tomllib

@dataclass
class TSDBConfig:
    host: str
    port: int
    username: str
    password: str

@dataclass
class Config:
    github_token: str
    timescaledb: TSDBConfig

def get_config():
    with open('config.toml', 'rb') as f:
        c = tomllib.load(f)

    conf = Config(
        github_token=c['github_token'],
        timescaledb=TSDBConfig(
            host=c['timescaledb']['host'],
            port=c['timescaledb']['port'],
            username=c['timescaledb']['username'],
            password=c['timescaledb']['password'],
        ),
    )
    return conf
