import os

import cherrypy

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import match as match_utils
from team_not_found.utils import mount as mount_utils
from team_not_found.utils import team as team_utils
from team_not_found.utils import tournament as tournament_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template = 'index.html')
    def index(self):
        # Get teams/team_files
        teams = team_utils.get_teams()
        split_teams = team_utils.get_split_teams(teams)

        # Get matches
        matches = match_utils.get_matches()
        split_matches = match_utils.get_split_matches(matches)

        # Get tournaments
        tournaments = tournament_utils.get_tournaments()
        split_tournaments = tournament_utils.get_split_tournaments(tournaments)

        return {
            'games': games.GAME_LIST,
            'your_teams': split_teams['your_teams'],
            'your_matches': split_matches['your_matches'],
            'your_tournaments': split_tournaments['your_tournaments']
        }


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
