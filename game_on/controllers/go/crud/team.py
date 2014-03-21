import cherrypy

from game_on import database as db
from game_on import games
from game_on.controllers.go.crud import base_crud

class TeamCrud(base_crud.BaseCrud):
    db = db
    model = db.Team
    readonly_properties = ['uuid', 'creator_uuid']

    def can_write(self, user, obj):
        """
        Does the user have write access to this resource?
        """
        return obj.creator is None or obj.creator == user

    def get_form_data(self, obj):
        #Get default form properties
        form_data = super(TeamCrud, self).get_form_data(obj)

        #Override form properties
        for prop in form_data:
            #Change game to be a list of options
            if prop['name'] == 'game':
                prop['type'] = 'Related'

                options = []
                for game in games.GAME_LIST:
                    options.append({
                        'label': game['name'],
                        'value': game['id'],
                    })
                prop['options'] = options

            #Show a value for creator
            if prop['name'] == 'creator_uuid':
                prop['value'] = cherrypy.request.user.name

        #Add extra form properties
        form_data.append({
            'label': 'File',
            'name': 'file',
            'type': 'File',
            'readonly': False,
        })

        return form_data

    def set_form_data(self, obj, data):
        #Deal with non-form properties
        obj.creator = cherrypy.request.user

        #Remove the extra form properties
        team_file = data.pop('file', None)

        #Deal with default form properties
        validation_errors = super(TeamCrud, self).set_form_data(obj, data)

        #Deal with extra form properties
        if team_file.length:
            #Save the file to disk
            raise Exception('TODO: Save team file')
        elif not obj.uuid:
            validation_errors.append('You must upload a file when creating a Team.')

        return validation_errors

def mount_tree():
    return TeamCrud()
