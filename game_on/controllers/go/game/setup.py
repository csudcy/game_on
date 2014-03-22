import cherrypy

from game_on import database as db
from game_on import games


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
                _or(
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
        team_lookup = {}
        for team in teams:
            #Create a lookup (used when POSTing)
            team_lookup[team.uuid] = team

            #Create the lists (used when GETting)
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
            #Find the teams
            team_1_dbobj = team_lookup[team_1]
            team_2_dbobj = team_lookup[team_2]

            #Find the team classes
            team_1_class = team_1_dbobj.load_class()
            team_2_class = team_2_dbobj.load_class()

            #Run the game
            game_obj = game([team_1_class, team_2_class])
            result = game_obj.run()

            #Create the match
            match = db.Match(
                game = game_id,
                team_1 = team_1_dbobj,
                team_2 = team_2_dbobj,
                creator = cherrypy.request.user,
            )
            db.Session.add(match)
            db.Session.commit()

            #Save result to file
            match.save_result(result)

            #Go replay the match!
            raise cherrypy.HTTPRedirect('/go/games/replay/%s/' % match.uuid)

        #Render the setup template
        return {
            'game_id': game_id,
            'game_name': game.name,
            'static_url': '/go/game/static/%s' % game_id,
            'your_teams': your_teams,
            'public_teams': public_teams,
            'other_teams': other_teams,
        }


def mount_tree():
    return Tree()
