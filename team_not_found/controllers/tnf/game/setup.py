import cherrypy

from team_not_found import database as db
from team_not_found import games

def get_teams(game_id):
    teams = db.Session.query(
        db.Team
    ).filter(
        db.Team.game == game_id
    ).order_by(
        db.Team.name
    )
    if not cherrypy.request.user.is_admin:
        #Current user is not an admin so they only see public teams and their own teams
        teams = teams.filter(
            db.sa.or_(
                db.Team.is_public == True,
                db.Team.creator == cherrypy.request.user
            )
        )
    return teams

def split_teams(teams):
    #Split teams into your, public, others
    your_team_files = []
    public_team_files = []
    other_team_files = []
    for team in teams:
        #Get the latest team_file
        team_file = team.get_team_file()
        #Create the team lists
        team_dict = {
            'id': team_file.uuid,
            'version': team_file.version,
            'team_name': team.name,
        }
        if team.is_public:
            public_team_files.append(team_dict)
        elif team.creator == cherrypy.request.user:
            your_team_files.append(team_dict)
        else:
            other_team_files.append(team_dict)

    return {
        'your_team_files': your_team_files,
        'public_team_files': public_team_files,
        'other_team_files': other_team_files,
    }

class Tree(object):

    @cherrypy.expose
    @cherrypy.tools.jinja2('game/setup_match.html')
    def match(self, game_id, team_file_1_uuid=None, team_file_2_uuid=None):
        """
        Display the setup page for a match of <game_id>
        """
        if cherrypy.request.method == 'POST':
            #Create the match
            match = games.start_match(
                game_id,
                team_file_1_uuid,
                team_file_2_uuid,
                cherrypy.request.user,
            )

            #Go wait for/replay the match!
            raise cherrypy.HTTPRedirect('/tnf/match/%s/' % match.uuid)

        #Find the game
        game = games.GAME_DICT[game_id]

        #Get team_files for this game
        teams = get_teams(game_id)
        context = split_teams(teams)

        #Render the setup template
        context.update({
            'game': game,
            'static_url': '/tnf/game/static/%s' % game_id,
        })
        return context

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
        teams = get_teams(game_id)
        context = split_teams(teams)

        #Render the setup template
        context.update({
            'game': game,
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
        })
        return context


def mount_tree():
    return Tree()
