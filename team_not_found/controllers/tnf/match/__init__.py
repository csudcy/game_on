import json

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
            'game': game,
            'match_uuid': match_uuid,
            'static_url': '/tnf/game/static/%s' % match.game,
            'data_url': '/tnf/match/json/%s/' % match_uuid,
            'game_info_url': '/tnf/game/%s/' % match.game,
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

        #Check the match has been played
        if match.state != 'PLAYED':
            return json.dumps({
                'state': match.state
            })

        #Return the result
        ret = cherrypy.lib.static.serve_fileobj(match.get_flo_reader_compressed())

        #Make the client unGZip
        cherrypy.response.headers['Content-Encoding'] = 'gzip'

        #Then just return it
        return ret


def mount_tree():
    return Tree()
