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
            'editable': cherrypy.request.user == team.creator,
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
        #Get the team_files
        team_files = db.Session.query(
            db.TeamFile.version
        ).filter(
            db.TeamFile.team_uuid == team_uuid
        ).order_by(
            db.TeamFile.version
        )

        #Return the list
        return [tf[0] for tf in team_files]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def code(self, team_uuid, version=None, code=None):
        """
        Get the contents of an existing version of code or create a new version.
        """
        #Cast version to be usable
        if version != None:
            version = int(version)

        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        #Save a new file?
        if cherrypy.request.method == 'POST':
            #Check the creator is the editor
            if cherrypy.request.user != team.creator:
                raise Exception('Only a teams creator may edit the team!')

            #Check the user is editing the latest version of the code
            if version is None:
                raise Exception('You must include version when POSTing to avoid conflicts!')
            team_file = team.get_team_file()
            if team_file.version != version:
                raise Exception('You are not editing the latest version of the code (%s < %s)!' % (version, team_file.version))

            #Save the code to a (probably) new file
            team_file = team.add_file(code)
            return {
                'uuid': team_file.uuid,
                'version': team_file.version,
            }

        #Read an existing file
        team_file = team.get_team_file(version)
        return {
            'code': team_file.read_file(),
            'version': team_file.version,
        }


def mount_tree():
    return Tree()
