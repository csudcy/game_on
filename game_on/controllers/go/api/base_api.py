import json

from psycopg2.errorcodes import UNIQUE_VIOLATION
import cherrypy
import sqlalchemy as sa

from game_on.database_helper import sa_exc

class BaseAPI(object):
    def get_allowed_methods(self):
        methods = []
        for method in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'):
            if hasattr(self, 'handle_{method}'.format(method=method)):
                methods.append(method)
        return methods

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    #This MUST be default and not index or this will not be used to handle calls with an ID!
    def default(self, *vpath, **params):
        method = getattr(self, "handle_" + cherrypy.request.method, None)
        if not method:
            methods = self.get_allowed_methods()
            cherrypy.response.headers["Allow"] = ",".join(methods)
            raise cherrypy.HTTPError(405, "Method not implemented.")
        return method(*vpath, **params);

    def handle_OPTIONS(self):
        methods = self.get_allowed_methods()
        cherrypy.response.headers["Allow"] = ",".join(methods)
        return None

    def extend_documents(self, documents):
        pass


class RestAPI(BaseAPI):
    #The sqlalchemy model this API is for
    model = None
    #TODO: Try to get this from model?
    db = None

    def __init__(self):
        if self.db is None:
            raise Exception('You must define a db attribute on %s' % self.__class__.__name__)
        if self.model is None:
            raise Exception('You must define a model attribute on %s' % self.__class__.__name__)

    def catch_unique_violation(self, ex):
        if ex.orig.pgcode == UNIQUE_VIOLATION:
            constraint_name = ex.orig.diag.constraint_name
            for t_arg in self.model.__table_args__:
                if getattr(t_arg, 'name', None) == constraint_name and hasattr(t_arg, 'columns'):
                    column_names = t_arg.columns.keys()
                    messages = {}
                    for name in column_names:
                        messages[name] = 'Must be unique'
                    cherrypy.response.status = 400
                    return {'messages': messages}
        # else
        raise

    def handle_GET(self, uuid=None):
        #Get the list of objects we can see
        objects = self.model._get_objects_for_user(cherrypy.request.user)

        # Handle single object case
        if uuid is not None:
            objects = objects.filter(self.model.uuid == uuid)
            if objects.count() != 1:
                raise cherrypy.HTTPError(404, "Object not found.")

        # Convert the results into a list of dictionaries
        data = []
        for row in objects:
            data.append(row.to_dict())

        #Add on any extra data
        self.extend_documents(data)

        #Return the data
        if uuid is not None:
            return data[0]
        return data

    def update_obj_with_data(self, obj, new_data):
        # Update the object with the data from the dictionary.
        obj.from_dict(new_data)
        return obj

    def handle_POST(self):
        data = cherrypy.request.json
        if not data:
            raise cherrypy.HTTPError(404, 'Missing data')
        #Create a new instance
        obj = self.model()
        #Update with the given data
        obj = self.update_obj_with_data(obj, data)
        #Save the instance
        self.db.Session.add(obj)
        try:
            self.db.Session.commit()
        except sa_exc.IntegrityError as ex:
            return self.catch_unique_violation(ex)
        cherrypy.response.status = 201
        return obj.to_dict()

    def handle_PUT(self, uuid=None):
        data = cherrypy.request.json
        data_uuid = data.get('uuid', None)
        if uuid and data_uuid and uuid != data_uuid:
            raise cherrypy.HTTPError(400, 'You provided multiple different UUIDs!')
        uuid = uuid or data_uuid
        if not uuid:
            raise cherrypy.HTTPError(400, 'You cannot put without providing a uuid!')
        #Get the instance
        obj = self.db.Session.query(self.model).get(uuid)
        if not obj:
            raise cherrypy.HTTPError(404, 'Object not found.')
        #Update with the given data
        obj = self.update_obj_with_data(obj, data)
        #Save the instance
        try:
            self.db.Session.commit()
        except sa_exc.IntegrityError as ex:
            return self.catch_unique_violation(ex)
        return obj.to_dict()

    def handle_DELETE(self, uuid):
        #Delete the instance
        delete_count = self.db.Session.query(self.model).filter(self.model.uuid == uuid).delete()
        if not delete_count:
            raise cherrypy.HTTPError(404, 'Object not found.')
        self.db.Session.commit()
        cherrypy.response.status = 204

    @cherrypy.expose
    def info(self):
        return '\n'.join(
            [
                #TODO: CHECK!
                '<h2>%s</h2>' % self.model.__name__,
                '<h4>',
                '<a href="..">..</a><br/>',
                'Count: %s' % self.db.Session.query(self.model).count(),
                '</h4>'
            ]
        )
