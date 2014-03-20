import os

import cherrypy

from game_on import games
from game_on.utils import mount as mount_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template = 'index.html')
    def index(self):
        #Get the list of games
        game_list = []
        for id, game in games.get_games().items():
            game_list.append({
                'id': id,
                'name': game.name,
                'description': game.description,
            })

        #TODO: Get the list of players for the current user
        players = []

        return {
            'games': game_list,
            'players': players,
        }


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
