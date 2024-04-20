from dataclasses import dataclass
import tomllib

@dataclass
class GithubConfig:
    token: str
    organization: str

@dataclass
class TSDBConfig:
    host: str
    port: int
    username: str
    password: str

@dataclass
class Config:
    github: GithubConfig
    timescaledb: TSDBConfig

def get_config():
    with open('config.toml', 'rb') as f:
        c = tomllib.load(f)

    conf = Config(
        github=GithubConfig(
            token=c['github']['token'],
            organization=c['github']['organization'],
        ),
        timescaledb=TSDBConfig(
            host=c['timescaledb']['host'],
            port=c['timescaledb']['port'],
            username=c['timescaledb']['username'],
            password=c['timescaledb']['password'],
        ),
    )
    return conf
