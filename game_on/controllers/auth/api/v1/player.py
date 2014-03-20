from game_on import database as db
from game_on.controllers.auth.api import base_api

class PlayerAPI(base_api.RestAPI):
    db = db
    model = db.Player


def mount_tree():
    return PlayerAPI()
