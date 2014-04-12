import os

import cherrypy
from sqlalchemy import or_

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import mount as mount_utils
from team_not_found.utils import team as team_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2('game/index.html')
    def default(self, game_id):
        """
        Display the game info for <game_id>
        """
        #Find the game
        game = games.GAME_DICT[game_id]

        #Get team_files for this game
        teams = team_utils.get_teams(game_id)
        team_sections = team_utils.get_team_sections(teams)

        # Find your matches
        matches = db.Session.query(
            db.Match
        ).filter(
            db.Match.creator == cherrypy.request.user,
            db.Match.game == game_id,
            db.Match.tournament == None,
        ).order_by(
            db.Match.create_date.desc()
        )

        # Transform for rendering
        match_list = []
        for match in matches:
            match_list.append({
                'uuid': match.uuid,
                'team_1_uuid': match.team_file_1.team.uuid,
                'team_1_name': match.team_file_1.team.name,
                'team_file_1_version': match.team_file_1.version,
                'team_2_uuid': match.team_file_2.team.uuid,
                'team_2_name': match.team_file_2.team.name,
                'team_file_2_version': match.team_file_2.version,
            })

        # Find your tournaments or tournaments involving one of your teams
        tournament_infos = db.Session.query(
            db.Tournament.uuid,
            db.Tournament.creator_uuid,
        ).join(
            db.TournamentTeamFile
        ).join(
            db.TeamFile
        ).join(
            db.Team
        ).filter(
            db.Tournament.game == game_id,
            or_(
                db.Tournament.creator == cherrypy.request.user,
                db.Team.creator == cherrypy.request.user,
            )
        ).distinct()

        # Process them into a usable format
        tournament_sections = []
        if tournament_infos:
            your_tournaments = []
            match_tournaments = []
            for tournament_uuid, creator_uuid in tournament_infos:
                tournament_dict = {
                    'uuid': tournament_uuid,
                }
                if creator_uuid == cherrypy.request.user.uuid:
                    your_tournaments.append(tournament_dict)
                else:
                    match_tournaments.append(tournament_dict)
            tournament_sections = [
                {
                    'type': 'Your Tournaments',
                    'tournaments': your_tournaments,
                },
                {
                    'type': 'Your Team Tournaments',
                    'tournaments': match_tournaments,
                },
            ]

        #Render
        return {
            'game_id': game_id,
            'game': game,
            'team_sections': team_sections,
            'matches': match_list,
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
