from game_on import database as db
from game_on.controllers.go.api import base_api

class TeamAPI(base_api.RestAPI):
    db = db
    model = db.Team


def mount_tree():
    return TeamAPI()
