import json

from psycopg2.errorcodes import UNIQUE_VIOLATION
import cherrypy
import sqlalchemy as sa

from team_not_found.database_helper import sa_exc

class BaseCrud(object):
    """
    Extend the RestAPI by adding nice HTML pages for CRUD operations
    """
    #The sqlalchemy model this API is for
    model = None

    #TODO: Try to get this from model?
    db = None

    #Any properties which should not be shown
    exclude_properties = []

    #Any properties which should not be editable
    readonly_properties = ['uuid']

    def __init__(self):
        if self.db is None:
            raise Exception('You must define a db attribute on %s' % self.__class__.__name__)
        if self.model is None:
            raise Exception('You must define a model attribute on %s' % self.__class__.__name__)

    #TODO: @memoize
    def get_columns(self, exclude_readonly=False):
        """
        Get the list of properties which should be exposed when CRUDing
        """
        columns = []
        for column in self.model.__table__.columns:
            if column.name in self.exclude_properties:
                continue
            if exclude_readonly and column.name in self.readonly_properties:
                continue

            if column.foreign_keys:
                columns.append({
                    'name': column.name,
                    'type': 'Related',
                    'related_name': column.related_name,
                    'related_model': column.related_model,
                })
            else:
                columns.append({
                    'name': column.name,
                    'name_set': column.name,
                    'type': column.type.__class__.__name__,
                })
        return columns

    #TODO: @memoize
    def get_properties(self, *args, **kwargs):
        """
        Get the list of properties which should be exposed when CRUDing
        """
        props = []
        for column in self.get_columns(*args, **kwargs):
            props.append(column['name'])
        return props

    def get_form_data(self, obj):
        columns = self.get_columns()
        form_data = []
        for column in columns:
            prop_dict = {
                'label': column['name'],
                'name': column['name'],
                'type': column['type'],
                'value': getattr(obj, column['name']),
                'readonly': column['name'] in self.readonly_properties,
            }
            if column['type'] == 'String':
                prop_dict['value'] = prop_dict['value'] or ''
            elif column['type'] == 'Boolean':
                pass
            elif column['type'] == 'Related':
                #Make the name nicer
                prop_dict['label'] = column['related_name']

                #Find possible values for relationship
                objects = column['related_model']._get_objects_for_user(cherrypy.request.user)

                options = []
                for option_obj in objects:
                    options.append({
                        'label': option_obj.name,
                        'value': option_obj.uuid,
                    })
                prop_dict['options'] = options
            else:
                raise Exception('Unhandled column type: %s' % column['type'])
            form_data.append(prop_dict)

        return form_data

    def set_form_data(self, obj, data):
        """
        Update the given object with the given data
        """
        validation_errors = []
        valid_properties = self.get_properties(exclude_readonly=True)
        for prop in data:
            #Check we are allowed to set this
            if prop not in valid_properties:
                validation_errors.append('You do not have permission to edit "%s"' % prop)
                continue

            #Update the property
            setattr(obj, prop, data[prop])

        return validation_errors

    def can_write(self, user, obj):
        """
        Does the user have write access to this resource?
        """
        return True

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('retrieve/')

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='crud_retrieve.html')
    def retrieve(self):
        """
        Retrieve the list of objects in a nice HTML page
        """
        #Get the list of objects we can see
        objects = self.model._get_objects_for_user(cherrypy.request.user)

        props = self.get_properties()
        data = []
        for obj in objects:
            obj_dict = {}
            for prop in props:
                obj_dict[prop] = getattr(obj, prop)
            obj_dict['can_write'] = self.can_write(cherrypy.request.user, obj)
            data.append(obj_dict)

        return {
            'object_name': self.model.verbose_name,
            'props': props,
            'objects': data,
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='crud_create.html')
    def create(self, **kwargs):
        """
        Create a new object in a nice HTML page
        """
        #Create a new object & check permissions
        obj = self.model()
        if not self.can_write(cherrypy.request.user, obj):
            raise cherrypy.HTTPError(403, 'You do not have permission to create this resource.')

        #Check if we are doing an update now
        validation_errors = []
        if cherrypy.request.method == 'POST':
            #Update the object with the given data
            validation_errors = self.set_form_data(obj, kwargs)

            if not validation_errors:
                #Save the changes
                self.db.Session.add(obj)
                self.db.Session.commit()

                #Redirect to the edit page for the new object
                #This should need another ../ but that goes too far...
                raise cherrypy.HTTPRedirect('update/%s/' % obj.uuid)

        return {
            'object_name': self.model.verbose_name,
            'obj': obj,
            'obj_props': self.get_form_data(obj),
            'validation_errors': validation_errors,
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='crud_update.html')
    def update(self, uuid, **kwargs):
        """
        Update this object in a nice HTML page
        """
        #Get the list of objects we can see
        objects = self.model._get_objects_for_user(cherrypy.request.user)

        #Check the given uuid is editable
        obj = objects.filter(
            self.model.uuid == uuid
        ).one()
        if not self.can_write(cherrypy.request.user, obj):
            raise cherrypy.HTTPError(403, 'You do not have permission to edit this resource.')

        #Check if we are doing an update now
        validation_errors = []
        if cherrypy.request.method == 'POST':
            #Update the object with the given data
            validation_errors = self.set_form_data(obj, kwargs)

            if not validation_errors:
                #Save the changes
                self.db.Session.add(obj)
                self.db.Session.commit()

        return {
            'object_name': self.model.verbose_name,
            'obj': obj,
            'obj_props': self.get_form_data(obj),
            'validation_errors': validation_errors
        }

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='crud_delete.html')
    def delete(self, uuid):
        """
        Delete this object in a nice HTML page
        """
        #Get the list of objects we can see
        objects = self.model._get_objects_for_user(cherrypy.request.user)

        #Check the given uuid is editable
        obj = objects.filter(
            self.model.uuid == uuid
        ).one()
        if not self.can_write(cherrypy.request.user, obj):
            raise cherrypy.HTTPError(403, 'You do not have permission to delete this resource.')

        #Check if we are doing an update now
        if cherrypy.request.method == 'POST':
            #Delete this object
            self.db.Session.delete(obj)
            self.db.Session.commit()

            #Redirect back to the list
            #This should need another ../ but that goes too far...
            raise cherrypy.HTTPRedirect('../retrieve/')

        return {
            'object_name': self.model.verbose_name,
            'obj': obj,
        }
