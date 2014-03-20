import os

import cherrypy

from game_on import games


JSON_FILE = 'C:/dev/tanks/temp.json'

class GameTree(object):
    @cherrypy.expose
    def setup(self, game_id):
        """
        Display the setup page for a match of <game_id>
        """
        #TODO: Implement!

        #HAX
        raise cherrypy.HTTPRedirect('../run/%s/' % game_id)

    @cherrypy.expose
    def run(self, game_id, **params):
        """
        Run a match of <game_id> with the posted parameters
        """
        #TODO: Implement!

        #HAX

        #Run a game
        from game_on.games.tanks import game
        from game_on.games.tanks import example_team
        tg = game.TankGame([example_team.Team, example_team.Team])
        match = tg.run()

        #JSON the output
        import json
        match_json = json.dumps(match)

        #Save it to file
        with open(JSON_FILE, 'w') as f:
            f.write(match_json)

        #Go watch it right now
        raise cherrypy.HTTPRedirect('../replay/%s/XXX/' % game_id)

    @cherrypy.expose
    def matches(self, game_id):
        """
        Display the list of matches for <game_id>
        """
        #TODO: Implement!

        #HAX
        raise cherrypy.HTTPRedirect('../replay/%s/XXX/' % game_id)

    @cherrypy.expose
    def replay(self, game_id, match_id):
        """
        Replay the selected <match_id> for <game_id>
        """
        #TODO: Implement!

        #HAX
        pass

    @cherrypy.expose
    def replay_json(self, game_id, match_id):
        """
        Retrieve the JSON for the selected <match_id> for <game_id>
        """
        #TODO: Implement!

        #HAX
        #Read the file
        with open(JSON_FILE, 'r') as f:
            contents = f.read()

        return contents



def mount_tree():
    return GameTree()
