import os

import cherrypy

from game_on import games


MATCH_DIRECTORY = 'C:/dev/tanks/matches'
MATCH_ID = '20140101T000000'

class GameTree(object):
    def get_match_path(self, game_id, match_id):
        filename = '%s-%s.json' % (game_id, match_id)
        path = os.path.join(MATCH_DIRECTORY, filename)
        return path

    @cherrypy.expose
    def setup(self, game_id):
        """
        Display the setup page for a match of <game_id>
        """
        #TODO: Implement!
        pass

        #HAX
        raise cherrypy.HTTPRedirect('../run/%s/' % game_id)

    @cherrypy.expose
    def run(self, game_id, **params):
        """
        Run a match of <game_id> with the posted parameters
        """
        #TODO: Implement!

        #Run a game
        from game_on.games.tanks import game
        from game_on.games.tanks import example_teams
        tg = game.TankGame([
            example_teams.dumb_runner_random.Team,
            example_teams.dumb_runner_ordered.Team,
        ])
        match = tg.run()

        #JSON the output
        import json
        match_json = json.dumps(match)

        #Save it to file
        with open(self.get_match_path(game_id, MATCH_ID), 'w') as f:
            f.write(match_json)

        #Go watch it right now
        raise cherrypy.HTTPRedirect('../replay/%s/%s/' % (game_id, MATCH_ID))

    @cherrypy.expose
    def matches(self, game_id):
        """
        Display the list of matches for <game_id>
        """
        #TODO: Implement!
        pass

        #HAX
        raise cherrypy.HTTPRedirect('../replay/%s/%s/' % (game_id, MATCH_ID))

    @cherrypy.expose
    def replay(self, game_id, match_id):
        """
        Replay the selected <match_id> for <game_id>
        """
        #TODO: Implement!
        game = games.GAME_DICT[game_id]
        template = game.jinja2_env.get_template('game.html')
        return template.render({
            'current_user': cherrypy.request.user,
            'game_id': game_id,
            'match_id': match_id,
            'static_url': '/go/game/static/%s' % game_id,
            'data_url': '/go/game/replay_json/%s/%s/' % (game_id, match_id),
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
    def replay_json(self, game_id, match_id):
        """
        Retrieve the JSON for the selected <match_id> for <game_id>
        """
        #TODO: Implement!

        #Find the replay file
        path = self.get_match_path(game_id, match_id)

        #Return the file
        return cherrypy.lib.static.serve_file(path)


def mount_tree():
    return GameTree()
