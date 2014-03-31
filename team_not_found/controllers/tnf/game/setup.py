import cherrypy

from team_not_found import database as db
from team_not_found import games


class Tree(object):
    def get_teams(self, game_id):
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

    @cherrypy.expose
    @cherrypy.tools.jinja2('game_setup.html')
    def default(self, game_id, team_1=None, team_2=None):
        """
        Display the setup page for a match of <game_id>
        """
        #Find the game
        game = games.GAME_DICT[game_id]

        #Get teams for this game
        teams = self.get_teams(game_id)

        #Split teams into your, public, others
        your_teams = []
        public_teams = []
        other_teams = []
        for team in teams:
            #Create the team lists
            team_dict = {
                'id': team.uuid,
                'name': team.name,
            }
            if team.is_public:
                public_teams.append(team_dict)
            elif team.creator == cherrypy.request.user:
                your_teams.append(team_dict)
            else:
                other_teams.append(team_dict)

        if cherrypy.request.method == 'POST':
            #Create the match
            match = games.start_match(
                game_id,
                team_1,
                team_2,
                cherrypy.request.user,
            )

            #Go wait for/replay the match!
            raise cherrypy.HTTPRedirect('/tnf/game/replay/%s/' % match.uuid)

        #Render the setup template
        return {
            'game_id': game_id,
            'game_name': game.name,
            'static_url': '/tnf/game/static/%s' % game_id,
            'your_teams': your_teams,
            'public_teams': public_teams,
            'other_teams': other_teams,
        }


def mount_tree():
    return Tree()
