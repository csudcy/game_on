from urlparse import urlparse

import cherrypy

from team_not_found import database as db

def auth_tool():
    #Check this session has a user
    user_uuid = cherrypy.session.get('user_uuid')
    if user_uuid:
        #Check it is a real user
        users = db.Session.query(
            db.User
        ).filter(
            db.User.uuid == user_uuid
        )
        if users.count() == 1:
            #Save the user somewhere
            cherrypy.request.user = users[0]

            #We're done here
            return

    #If we get here, something's not right!
    raise cherrypy.HTTPRedirect('/?redirect=%s' % urlparse(cherrypy.url()).path)

cherrypy.tools.auth_tool = cherrypy.Tool('before_handler', auth_tool, priority=90)
