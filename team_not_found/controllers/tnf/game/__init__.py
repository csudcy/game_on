import os

import cherrypy
from sqlalchemy import or_

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import match as match_utils
from team_not_found.utils import mount as mount_utils
from team_not_found.utils import team as team_utils
from team_not_found.utils import tournament as tournament_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2('game/index.html')
    def default(self, game_id):
        """
        Display the game info for <game_id>
        """
        # Find the game
        game = games.GAME_DICT[game_id]

        # Get teams/team_files
        teams = team_utils.get_teams(game_id)
        team_sections = team_utils.get_team_sections(teams)

        # Get matches
        matches = match_utils.get_matches(game_id)
        match_sections = match_utils.get_match_sections(matches)

        # Get tournaments
        tournaments = tournament_utils.get_tournaments(game_id)
        tournament_sections = tournament_utils.get_tournament_sections(tournaments)

        # Render
        return {
            'game_id': game_id,
            'game': game,
            'team_sections': team_sections,
            'match_sections': match_sections,
            'tournament_sections': tournament_sections,
        }

    @cherrypy.expose
    def static(self, game_id, filename):
        """
        Retrieve the game.js file for <game_id>
        """
        #Get the game
        game = games.GAME_DICT[game_id]

        #Find the path to load
        path = os.path.join(game.static_folder, filename)

        #Check we are not going outside the static_folder
        prefix = os.path.commonprefix([path, game.static_folder])
        if not prefix.startswith(game.static_folder):
            raise Exception('Cannot get static files outside the static_folder!')

        return cherrypy.lib.static.serve_file(path)


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
