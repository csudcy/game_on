import cherrypy


def forced_trailing_slash():
    """Redirect if path_info has a missing trailing slash."""
    if cherrypy.request.method == 'GET':
        if not cherrypy.request.path_info.endswith('/'):
            new_url = cherrypy.url(cherrypy.request.path_info + '/', cherrypy.request.query_string)
            raise cherrypy.HTTPRedirect(new_url, status=301)

cherrypy.tools.forced_trailing_slash_tool = cherrypy.Tool('before_handler', forced_trailing_slash, priority=90)
