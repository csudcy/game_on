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
        match_infos = db.Session.query(
            db.Match.uuid,
            db.Match.state,
            team_1.uuid,
            team_1.name,
            db.Match.team_1_won,
            team_2.uuid,
            team_2.name,
            db.Match.team_2_won,
        ).join(
            team_1,
            db.Match.team_1
        ).join(
            team_2,
            db.Match.team_2
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
        for uuid, state, t1_uuid, t1_name, t1_won, t2_uuid, t2_name, t2_won in match_infos:
            #Add it to the list of matches
            matches.append({
                'uuid': uuid,
                'team_1': t1_name,
                'team_2': t2_name,
                'state': state,
            })

            #Update some stats
            if state == 'PLAYED':
                matches_played += 1
            if t1_uuid not in teams:
                teams[t1_uuid] = {
                    'uuid': t1_uuid,
                    'name': t1_name,
                    'score': 0,
                }
            if t2_uuid not in teams:
                teams[t2_uuid] = {
                    'uuid': t2_uuid,
                    'name': t2_name,
                    'score': 0,
                }
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

        scoreboard = general.multikeysort(teams.values(), ('-score', 'name'))

        return {
            'tournament_uuid': tournament_uuid,
            'matches': matches,
            'matches_played': matches_played,
            'scoreboard': scoreboard,
        }


def mount_tree():
    return Tree()
