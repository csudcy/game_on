import json

import cherrypy

from team_not_found import database as db
from team_not_found import games


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template='team/index.html')
    def default(self):
        """
        Create a new team
        """
        return {}


    @cherrypy.expose
    @cherrypy.tools.jinja2(template='team/edit.html')
    def edit(self, team_uuid):
        """
        Edit the given team
        """
        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        #Get the game
        game = games.GAME_DICT[team.game]

        #Render the tournament template
        return {
            'game': game,
            'team_uuid': team_uuid,
            'team': team,
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='team/edit.html')
    def code(self, team_uuid, code=None):
        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        if cherrypy.request.method == 'POST':
            team.write_file(code)
            return

        return team.read_file()


def mount_tree():
    return Tree()
