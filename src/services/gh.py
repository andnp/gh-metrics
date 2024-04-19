from state import AppState

def get_repository_names(s: AppState):
    repos = (
        s.github
        .get_organization('Amii-Open-Source')
        .get_repos(type='public')
    )
    return [r.full_name for r in repos]
