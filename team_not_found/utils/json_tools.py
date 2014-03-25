import cherrypy
import json


def json_in_processor(entity):
    """Read application/json data into handler arguments."""
    body = entity.fp.read()
    try:
        cherrypy.request.json = json.loads(body.decode('utf-8'))
    except ValueError:
        raise cherrypy.HTTPError(400, 'Invalid JSON document')


def json_out_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return json.dumps(value)
