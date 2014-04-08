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
            'team': team,
            'versions_url': '/tnf/team/versions/%s/' % team.uuid,
            'code_url': '/tnf/team/code/%s/' % team.uuid,
            'game_info_url': '/tnf/game/%s/' % team.game,
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def versions(self, team_uuid):
        """
        Return a list of all the available versions of the given team
        """
        return []

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def code(self, team_uuid, version=None, code=None):
        """
        Get the contents of an existing version of code or create a new version.
        """
        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        #Save a new file?
        if cherrypy.request.method == 'POST':
            if version:
                raise Exception('You cannot POST to a specific version!')
            team_file = team.add_file(code)
            return {
                'uuid': team_file.uuid,
                'version': team_file.version,
            }

        #Read an existing file
        return {
            'code': team.read_file(version)
        }


def mount_tree():
    return Tree()
