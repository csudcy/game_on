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
    def login(self, username, password, redirect=None):
        #Find the user
        users = db.Session.query(
            db.User
        ).filter(
            db.User.username == username
        )
        if users.count() == 1:
            #User found!
            user = users[0]
            #Check the password
            if user.check_password(password):
                #Everything is good
                cherrypy.session['user_uuid'] = user.uuid
                cherrypy.session.save()
                raise cherrypy.HTTPRedirect(redirect or '/tnf/')

        #If we get here, something's wrong :(
        url = '/?error=Username or password incorrect'
        if redirect:
            url += '&redirect=' + redirect
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def logout(self):
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect('/')


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
