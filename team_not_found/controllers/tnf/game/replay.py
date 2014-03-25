import cherrypy

from team_not_found import database as db
from team_not_found import games


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
            'static_url': '/tnf/game/static/%s' % match.game,
            'data_url': '/tnf/game/replay/json/%s/' % match_uuid,
            'match_list_url': '/tnf/game/%s/' % match.game,
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
        return cherrypy.lib.static.serve_fileobj(match.get_flo())


def mount_tree():
    return Tree()