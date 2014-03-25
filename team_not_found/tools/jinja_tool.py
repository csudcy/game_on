import os

import cherrypy
from jinja2 import Environment, FileSystemLoader

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_PATH, '..', 'ui')
TEMPLATE_PATH = os.path.abspath(TEMPLATE_PATH)

def get_env(extra_paths=None):
    paths = [TEMPLATE_PATH]
    if extra_paths:
        if isinstance(extra_paths, list):
            paths.extend(extra_paths)
        else:
            paths.append(extra_paths)
    env = Environment(
        loader=FileSystemLoader(paths),
        extensions=['jinja2.ext.i18n']
    )
    return env

def jinja2(template=None, extra_paths=None):
    #Create the environment every time so we can add different paths
    env = get_env(extra_paths=extra_paths)
    if not env.get_template(template):
        raise Exception('Template not found: %s' % template)
    def inner_jinja2(func):
        def wrapped(*args, **kwargs):
            data = func(*args, **kwargs)
            if cherrypy.response.status < 400:
                if hasattr(cherrypy.request, 'user'):
                    #Always pass through the user when logged in
                    if 'current_user' in data:
                        raise Exception('Data already has current_user!')
                    data['current_user'] = cherrypy.request.user
                data = env.get_template(template).render(**data)
            return data
        return wrapped
    return inner_jinja2
#Even though this isnt a tool, we'll store it in tools to allow easy access
cherrypy.tools.jinja2 = jinja2
