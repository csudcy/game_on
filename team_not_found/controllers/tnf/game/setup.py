import cherrypy

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import team as team_utils

class Tree(object):

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.jinja2('game/setup_match.html')
    def match(self, game_id):
        """
        Display the setup page for a match of <game_id>
        """
        #Find the game
        game = games.GAME_DICT[game_id]

        #Get team_files for this game
        teams = team_utils.get_teams(game_id)
        team_sections = team_utils.get_team_sections(teams)

        #Render the setup template
        return {
            'game': game,
            'team_sections': team_sections,
            'static_url': '/tnf/game/static/%s' % game_id,
        }

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def match_create(self, game_id, team_file_1_uuid, team_file_2_uuid):
        """
        Display the setup page for a match of <game_id>
        """
        #Create the match
        match = games.start_match(
            game_id,
            team_file_1_uuid,
            team_file_2_uuid,
            cherrypy.request.user,
        )

        #Let the frontend know where to go to replay the match
        return {
            'replay_url': '/tnf/match/%s/' % match.uuid,
            'replay_data_url': '/tnf/match/json/%s/' % match.uuid,
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2('game/setup_tournament.html')
    def tournament(self, game_id, team_file_uuids=None, tournament_type=None, best_of=None):
        """
        Display the setup page for a tournament of <game_id>
        """
        if cherrypy.request.method == 'POST':
            #Create the match
            tournament = games.start_tournament(
                game_id,
                team_file_uuids,
                tournament_type,
                int(best_of),
                cherrypy.request.user,
            )

            #Go wait for/replay the match!
            raise cherrypy.HTTPRedirect('/tnf/tournament/%s/' % tournament.uuid)

        #Find the game
        game = games.GAME_DICT[game_id]

        #Get teams for this game
        teams = team_utils.get_teams(game_id)
        team_sections = team_utils.get_team_sections(teams)

        #Render the setup template
        return {
            'game': game,
            'team_sections': team_sections,
            'tournament_types': [
                {
                    'type': 'bracket',
                    'name': 'Bracket',
                },
                {
                    'type': 'matrix',
                    'name': 'Matrix',
                },
            ],
            'best_ofs': (1, 3, 5),
            'static_url': '/tnf/game/static/%s' % game_id,
        }


def mount_tree():
    return Tree()
