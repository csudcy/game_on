import os
import logging

import cherrypy

logger = logging.getLogger(__name__)

def add_all_trees(cwd, globals, cls):
    """
    This scans all files/directories in cwd, imports them all then mounts them.
    Very useful for mounting routing trees!
    """
    url_map = {}

    #First import everything
    for filename in os.listdir(cwd):
        if filename == '__init__.py':
            #Don't try to remount ourselves!
            continue
        if os.path.isfile(os.path.join(cwd, filename)):
            if not filename.endswith('.py'):
                continue
            #Remove .py
            filename = filename[:-3]
        logger.debug('Loading  %s...' % filename)
        module = __import__(filename, globals=globals)
        if hasattr(module, 'mount_tree'):
            logger.debug('Adding   %s' % filename)
            api_instance = module.mount_tree()
            setattr(cls, filename, api_instance)

            #store a reference of the instance in the map
            url_map[filename] = api_instance
        else:
            logger.debug('Skipping %s (no tree)' % filename)

    return url_map

class SelfDoc(object):
    @cherrypy.expose
    def index(self):
        #Default to returning a list all my URLs
        output = [
            '<h2>%s</h2>' % __name__,
            '<h4>',
            '<a href="..">..</a>'
        ]
        for key in dir(self):
            if key.startswith('_') or key in ['index', 'default']:
                continue
            output.append('<br/><a href="{key}">{key}</a>'.format(key=key))
        output.append('</h4>')
        return '\n'.join(output)

    #Copy so index can be overridden
    _doc = index
