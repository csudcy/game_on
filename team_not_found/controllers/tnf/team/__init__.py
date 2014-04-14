import json

import cherrypy

from team_not_found import database as db
from team_not_found import games
from team_not_found.utils import team as team_utils


class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template='team/index.html')
    def default(self, game_id=None, name=None, is_public=None):
        """
        Create a new team
        """
        messages = []
        if cherrypy.request.method == 'POST':
            # Create a new team
            if not game_id:
                messages.append({
                    'class': 'error',
                    'text': 'You must select a game for your team',
                })
            if not name:
                messages.append({
                    'class': 'error',
                    'text': 'You must enter a name for your team',
                })
            else:
                # Check the name is unique
                existing_team_count = db.Session.query(
                    db.Team
                ).filter(
                    db.Team.name == name
                ).count()
                if existing_team_count > 0:
                    messages.append({
                        'class': 'error',
                        'text': 'Team names must be unique',
                    })
            if not messages:
                # All fields validate correctly
                game = games.GAME_DICT[game_id]

                # create the team
                team = db.Team(
                    game=game_id,
                    name=name,
                    is_public=is_public,
                    creator=cherrypy.request.user,
                )
                db.Session.add(team)

                #Read the example team file
                example_team_file = game.get_example_team_file()

                #Create the initial file for the team & save
                team_file = team.add_file(example_team_file)

                #Done, goto the team edit page
                raise cherrypy.HTTPRedirect('/tnf/team/edit/%s/' % team.uuid)

        return {
            'messages': messages,
            'games': games.GAME_LIST,
            'game_id': game_id,
            'name': name,
            'is_public': is_public,
        }

    @cherrypy.expose
    def edit(self, team_uuid, initial_team_file_uuid=None):
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

        #Get list of opponents
        teams = team_utils.get_teams(team.game)
        opponents = teams.filter(
            db.Team.uuid != team.uuid
        )
        team_sections = team_utils.get_team_sections(opponents)

        #Render the tournament template
        template = game.jinja2_env.get_template('team/edit.html')
        return template.render({
            'current_user': cherrypy.request.user,
            'game': game,
            'team': team,
            'initial_team_file_uuid': initial_team_file_uuid,
            'editable': cherrypy.request.user == team.creator,
            'static_url': '/tnf/game/static/%s' % team.game,
            'team_sections': team_sections,
        })

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def versions(self, team_uuid):
        """
        Return a list of all the available versions of the given team
        """
        #Get the team_files
        team_files = db.Session.query(
            db.TeamFile.uuid,
            db.TeamFile.version
        ).filter(
            db.TeamFile.team_uuid == team_uuid
        ).order_by(
            db.TeamFile.version
        )

        #Return the list
        return [{
            'team_file_uuid': tf[0],
            'team_file_version': tf[1],
        } for tf in team_files]

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    def code_load(self, team_uuid, team_file_uuid=None):
        """
        Get the contents of an existing version of code
        """
        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        # Get the specific/latest team_file
        team_file = team.get_team_file(team_file_uuid)

        #Read an existing file
        return {
            'code': team_file.read_file(),
            'team_file_uuid': team_file.uuid,
            'team_file_version': team_file.version,
        }

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def code_save(self, team_uuid, team_file_uuid, code):
        """
        Create a new version of team code (ensuring you are saving over the latest version)
        """
        #Get the team
        team = db.Session.query(
            db.Team
        ).filter(
            db.Team.uuid == team_uuid
        ).one()

        # Get the specific & latest team_files
        team_file = team.get_team_file(team_file_uuid)
        latest_team_file = team.get_team_file()

        #Check the creator is the editor
        if cherrypy.request.user != team.creator:
            raise Exception('Only a teams creator may edit the team!')

        #Check the user is editing the latest version of the code
        if team_file.uuid != latest_team_file.uuid:
            raise Exception('You are not editing the latest version of the code (%s < %s)!' % (team_file.version, latest_team_file.version))

        #Save the code to a (probably) new file
        team_file = team.add_file(code)
        return {
            'team_file_uuid': team_file.uuid,
            'team_file_version': team_file.version,
        }


def mount_tree():
    return Tree()
