from typing import NamedTuple
from state import AppState

def get_repository_names(s: AppState):
    repos = (
        s.github
        .get_organization('Amii-Open-Source')
        .get_repos(type='public')
    )
    return [r.full_name for r in repos]


class RepoStats(NamedTuple):
    stars: int
    watchers: int
    forks: int

def get_repo_stats(s: AppState, name: str):
    repo = s.github.get_repo(name, lazy=True)

    return RepoStats(
        stars=repo.stargazers_count,
        watchers=repo.watchers_count,
        forks=repo.forks_count,
    )
