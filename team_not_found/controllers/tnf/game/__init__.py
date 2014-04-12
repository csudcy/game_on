import os

import cherrypy
from sqlalchemy import or_

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import mount as mount_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2('game/index.html')
    def default(self, game_id):
        """
        Display the game info for <game_id>
        """
        #Find the game
        game = games.GAME_DICT[game_id]

        #Find your matches
        your_matches = db.Session.query(
            db.Match
        ).filter(
            db.Match.creator == cherrypy.request.user,
            db.Match.tournament == None,
        )

        #Find matches your team has been used in (that aren't your matchs)
        your_team_files = db.Session.query(
            db.TeamFile
        ).filter(
            db.TeamFile.team.has(creator = cherrypy.request.user),
        )
        team_matches = db.Session.query(
            db.Match
        ).filter(
            or_(
                db.Match.team_file_1 in your_team_files,
                db.Match.team_file_2 in your_team_files,
            )
        )

        #Transform for rendering
        def get_matches_list(matches):
            matches = matches.order_by(db.Match.create_date.desc())
            match_list = []
            for match in matches:
                match_list.append({
                    'uuid': match.uuid,
                    'team_1': match.team_file_1.team.name,
                    'team_2': match.team_file_2.team.name,
                })
            return match_list


        # Now get tournaments for the current user
        tournament_infos = db.Session.query(
            db.Tournament.uuid,
        ).filter(
            db.Tournament.game == game_id,
            db.Tournament.creator == cherrypy.request.user,
        )

        # Process them into a usable format
        tournaments = []
        for tournament_info in tournament_infos:
            tournaments.append({
                'uuid': tournament_info[0],
            })


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
            'tournaments': tournaments
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
