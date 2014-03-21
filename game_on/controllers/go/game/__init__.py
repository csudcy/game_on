import os

import cherrypy
from sqlalchemy import or_

from game_on import database as db
from game_on import games
from game_on.cfg import config


class GameTree(object):
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
    def setup(self, game_id, team_1=None, team_2=None):
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
            raise cherrypy.HTTPRedirect('../replay/%s/' % match.uuid)

        #Render the setup template
        return {
            'game_id': game_id,
            'game_name': game.name,
            'static_url': '/go/game/static/%s' % game_id,
            'your_teams': your_teams,
            'public_teams': public_teams,
            'other_teams': other_teams,
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2('game_matches.html')
    def matches(self, game_id):
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
    def replay(self, match_uuid):
        """
        Replay the selected <match_uuid>
        """
        #Get the match
        match = db.Session.query(
            db.Match
        ).filter(
            db.Match.uuid == match_uuid
        ).one()

        #Get the game
        game = games.GAME_DICT[match.game]

        #Render the replay template
        template = game.jinja2_env.get_template('replay.html')
        return template.render({
            'current_user': cherrypy.request.user,
            'game_name': game.name,
            'match_uuid': match_uuid,
            'static_url': '/go/game/static/%s' % match.game,
            'data_url': '/go/game/replay_json/%s/' % match_uuid,
            'match_list_url': '/go/game/matches/%s/' % match.game,
        })


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

    @cherrypy.expose
    def replay_json(self, match_uuid):
        """
        Retrieve the JSON for the selected <match_uuid>
        """
        #Get the match
        match = db.Session.query(
            db.Match
        ).filter(
            db.Match.uuid == match_uuid
        ).one()

        #Return the result
        return cherrypy.lib.static.serve_file(match.get_path())


def mount_tree():
    return GameTree()
