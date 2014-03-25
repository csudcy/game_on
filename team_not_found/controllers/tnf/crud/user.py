import cherrypy

from team_not_found import database as db
from team_not_found.controllers.tnf.crud import base_crud

class UserCrud(base_crud.BaseCrud):
    db = db
    model = db.User

    exclude_properties = ['password_hash']

    def can_write(self, user, obj):
        """
        Does the user have write access to this resource?
        """
        return user.is_admin

    def get_form_data(self, obj):
        #Get default form properties
        form_data = super(UserCrud, self).get_form_data(obj)

        #Add extra form properties
        form_data.append({
            'label': 'Password',
            'name': 'password1',
            'type': 'Password',
            'value': '',
            'readonly': False,
        })

        form_data.append({
            'label': 'Confirm Password',
            'name': 'password2',
            'type': 'Password',
            'value': '',
            'readonly': False,
        })

        return form_data

    def set_form_data(self, obj, data):
        #Remove the extra form properties
        password1 = data.pop('password1')
        password2 = data.pop('password2')

        #Deal with default form properties
        validation_errors = super(UserCrud, self).set_form_data(obj, data)

        #Deal with extra form properties
        if password1 or password2:
            #Check the passwords are valid
            if len(password1) < 8:
                validation_errors.append('Passwords must be at least 8 characters long!')
            elif password1 != password2:
                validation_errors.append('Passwords must match!')
            else:
                #Password is valid, set the new password
                obj.password_hash = obj.hash_password(password1)
        else:
            if not obj.uuid:
                #This is a new user, password is required!
                validation_errors.append('New users require a password!')

        return validation_errors


def mount_tree():
    return UserCrud()
