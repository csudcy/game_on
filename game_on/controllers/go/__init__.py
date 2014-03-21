import os

import cherrypy

from game_on import games
from game_on.utils import mount as mount_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template = 'index.html')
    def index(self):
        #TODO: Get the list of teams for the current user
        teams = []

        return {
            'games': games.GAME_LIST,
            'teams': teams,
        }


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
