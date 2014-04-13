import os

import cherrypy

from team_not_found import database as db
from team_not_found.utils import mount as mount_utils


#Handle noauth URLs
class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template='splash.html')
    def index(self, error=None, redirect=None):
        return {
            'error': error,
            'redirect': redirect,
        }

    @cherrypy.expose
    def login(self, email, password, redirect=None):
        #Find the user
        users = db.Session.query(
            db.User
        ).filter(
            db.User.email == email
        )
        error = 'Email or password incorrect'
        if users.count() == 1:
            # User found!
            user = users[0]
            # Check the password
            if user.check_password(password):
                # Password is good, check they are confirmed
                if user.is_confirmed:
                    #All is good!
                    cherrypy.session['user_uuid'] = user.uuid
                    cherrypy.session.save()
                    raise cherrypy.HTTPRedirect(redirect or '/tnf/')
                #If we're here, user & pass is good but they're not confirmed
                error = 'You have not confirmed your email address!'

        #If we get here, something's wrong :(
        url = '/?error=%s' % error
        if redirect:
            url += '&redirect=%s' % redirect
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def logout(self):
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='create_user.html')
    def create_user(self, email=None, password=None):
        return {}


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
