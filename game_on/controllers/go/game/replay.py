import cherrypy

from game_on import database as db
from game_on import games


class Tree(object):
    @cherrypy.expose
    def default(self, match_uuid):
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
            'game_id': match.game,
            'game_name': game.name,
            'match_uuid': match_uuid,
            'static_url': '/go/game/static/%s' % match.game,
            'data_url': '/go/game/replay/json/%s/' % match_uuid,
            'match_list_url': '/go/game/%s/' % match.game,
        })


    @cherrypy.expose
    def json(self, match_uuid):
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
    return Tree()
