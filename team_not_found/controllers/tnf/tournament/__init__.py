import json

import cherrypy

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import general


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template='tournament/index.html')
    def default(self, tournament_uuid):
        """
        Show results for the selected <tournament_uuid>
        """
        #Get the tournament
        tournament = db.Session.query(
            db.Tournament
        ).filter(
            db.Tournament.uuid == tournament_uuid
        ).one()

        #Get the game
        game = games.GAME_DICT[tournament.game]

        #Render the tournament template
        return {
            'game': game,
            'tournament_uuid': tournament_uuid,
            'data_url': '/tnf/tournament/results/%s/' % tournament_uuid,
            'game_info_url': '/tnf/game/%s/' % tournament.game,
        }


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def results(self, tournament_uuid):
        """
        Retrieve the results for the selected <tournament_uuid>
        """
        #Get the tournament
        tournament = db.Session.query(
            db.Tournament
        ).filter(
            db.Tournament.uuid == tournament_uuid
        ).one()

        #Get the matches for this tournament
        team_1 = db.sa_orm.aliased(db.Team)
        team_2 = db.sa_orm.aliased(db.Team)
        team_file_1 = db.sa_orm.aliased(db.TeamFile)
        team_file_2 = db.sa_orm.aliased(db.TeamFile)
        match_infos = db.Session.query(
            db.Match.uuid,
            db.Match.state,
            team_1.uuid,
            team_1.name,
            team_file_1.uuid,
            team_file_1.version,
            db.Match.team_1_won,
            team_2.uuid,
            team_2.name,
            team_file_2.uuid,
            team_file_2.version,
            db.Match.team_2_won,
        ).join(
            team_file_1,
            db.Match.team_file_1
        ).join(
            team_file_2,
            db.Match.team_file_2
        ).join(
            team_1,
            team_file_1.team
        ).join(
            team_2,
            team_file_2.team
        ).filter(
            db.Match.tournament == tournament
        ).order_by(
            team_1.name,
            team_2.name,
            db.Match.uuid,
        ).all()

        #Process them
        matches = []
        matches_played = 0
        teams = {}
        def check_team(team_uuid, team_name, team_file_uuid, team_file_version):
            if team_uuid not in teams:
                teams[team_uuid] = {
                    'team_uuid': team_uuid,
                    'team_name': team_name,
                    'team_file_uuid': team_file_uuid,
                    'team_file_version': team_file_version,
                    'score': 0,
                }
        for uuid, state, t1_uuid, t1_name, tf1_uuid, tf1_version, t1_won, t2_uuid, t2_name, tf2_uuid, tf2_version, t2_won in match_infos:
            #Add it to the list of matches
            matches.append({
                'uuid': uuid,
                'team_1_uuid': t1_uuid,
                'team_1_name': t1_name,
                'team_file_1_uuid': tf1_uuid,
                'team_file_1_version': tf1_version,
                'team_2_uuid': t2_uuid,
                'team_2_name': t2_name,
                'team_file_2_uuid': tf2_uuid,
                'team_file_2_version': tf2_version,
                'state': state,
            })

            #Update some stats
            if state == 'PLAYED':
                matches_played += 1
            check_team(
                t1_uuid,
                t1_name,
                tf1_uuid,
                tf1_version,
            )
            check_team(
                t2_uuid,
                t2_name,
                tf2_uuid,
                tf2_version,
            )

            if t1_won and t2_won:
                #Draw
                teams[t1_uuid]['score'] += 1
                teams[t2_uuid]['score'] += 1
            elif t1_won:
                #Team 1 won
                teams[t1_uuid]['score'] += 3
            elif t2_won:
                #Team 2 won
                teams[t2_uuid]['score'] += 3
            #else noone won

        #Sort it out...
        scoreboard = general.multikeysort(teams.values(), ('-score', 'team_name'))

        return {
            'tournament_uuid': tournament_uuid,
            'matches': matches,
            'matches_played': matches_played,
            'scoreboard': scoreboard,
        }


def mount_tree():
    return Tree()
