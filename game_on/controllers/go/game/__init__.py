import os

import cherrypy
from sqlalchemy import or_

from game_on import database as db
from game_on import games
from game_on.utils import mount as mount_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2('game_matches.html')
    def default(self, game_id):
        """
        Display the list of matches for <game_id>
        """
        #Find the game
        game = games.GAME_DICT[game_id]

        #Find your matches
        your_matches = db.Session.query(
            db.Match
        ).filter(
            db.Match.creator == cherrypy.request.user
        )

        #Find matches your team has been used in (that aren't your matchs)
        your_teams = db.Session.query(
            db.Team
        ).filter(
            db.Team.creator == cherrypy.request.user,
        )
        team_matches = db.Session.query(
            db.Match
        ).filter(
            or_(
                db.Match.team_1 in your_teams,
                db.Match.team_2 in your_teams,
            )
        )

        #Transform for rendering
        def get_matches_list(matches):
            matches = matches.order_by(db.Match.create_date.desc())
            match_list = []
            for match in matches:
                match_list.append({
                    'uuid': match.uuid,
                    'team_1': match.team_1.name,
                    'team_2': match.team_2.name,
                })
            return match_list

        #Render
        return {
            'game_id': game_id,
            'game': game,
            'match_sections': [
                {
                    'type': 'Your Matches',
                    'matches': get_matches_list(your_matches),
                },
                {
                    'type': 'Team Matches',
                    'matches': get_matches_list(team_matches),
                },
            ],
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
