from game_on import database as db
from game_on.controllers.go.api import base_api

class UserAPI(base_api.RestAPI):
    db = db
    model = db.User


def mount_tree():
    return UserAPI()
