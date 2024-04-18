from github import Github
from github import Auth

import utils.config as Config

token = Config.github_token()
auth = Auth.Token(token)

g = Github(auth=auth)

u = g.get_user()
print(u.name)
