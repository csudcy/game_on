#!/usr/bin/python
from optparse import OptionParser
import logging
import os
import sys
import traceback

# These paths are useful for development & <i>shouldn't</i> break
# anything when released
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PARENT_DIRECTORY = os.path.split(CURRENT_DIRECTORY)[0]
LIB_PATH = os.path.join(PARENT_DIRECTORY, 'libs')
sys.path.insert(0, PARENT_DIRECTORY)
sys.path.insert(0, LIB_PATH)
sys.path.insert(0, os.path.join(LIB_PATH, 'cherrypy'))

import cherrypy

#Have to import tools before controllers
from game_on import tools
from game_on import controllers
from game_on import database as db
from game_on import games
from game_on.cfg import config
from game_on.utils import log as log_utils
from game_on.utils.json_tools import json_in_processor, json_out_handler


def initialise_db():
    db.connect_to_db(config['db'])
    db.connection.sync()
    #Ensure an admin user exists
    admin_users = db.Session.query(
        db.User
    ).filter(
        db.User.is_admin == True
    )
    if admin_users.count() == 0:
        db.Session.add(db.User(
            username = 'admin',
            name = 'Admin',
            password_hash = db.User.hash_password('admin'),
            is_admin = True,
        ))
        db.Session.commit()


def initialise_games():
    #Get the admin user for creating example teams
    admin_user = db.Session.query(
        db.User
    ).filter(
        db.User.is_admin == True
    ).one()

    #Go!
    games.initialise_games(admin_user)


def initialise_cherrypy():
    #Make AutoReloader exit not restart
    cherrypy.engine._restart = cherrypy.engine.restart
    cherrypy.engine.restart = cherrypy.engine.exit

    #Make sure we close sessions after requests
    def _close_session():
        db.Session.remove()
    cherrypy.request.hooks.attach('on_end_request', _close_session)

    #Mount the root & static files
    cwd = os.path.dirname(os.path.abspath(__file__))
    cherrypy.tree.mount(
        controllers.mount_tree(),
        '/',
        {
            '/': {
                'tools.sessions.on': True,
                'tools.sessions.name': 'game_on_session_id',
                'tools.sessions.locking': 'explicit',
                'tools.sessions.timeout': 60 * 24 * 7, # 1 week
                'tools.json_in.processor': json_in_processor,
                'tools.json_out.handler': json_out_handler,
            },
            '/go': {
                'tools.auth_tool.on': True,
            },
            '/go/crud': {
                #Make sure everything has a trailing slash so relative links work
                'tools.forced_trailing_slash_tool.on': True,
            },
            '/static': {
                'tools.sessions.on': False,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(cwd, 'static'),
                'tools.staticdir.content_types':
                        {
                          'woff': 'application/x-font-woff',
                          'svg' : 'image/svg+xml'
                        },
                'tools.expires.on': True,
                'tools.expires.secs': 60*60*config['cherrypy']['static_timeout_hours'],
            },
            '/favicon.ico' : {
                'tools.staticfile.on' : True,
                'tools.staticfile.filename' : os.path.join(cwd, 'static/img/icons/favicon.ico')
            }
        })

    cherrypy.server.socket_host = config['cherrypy']['host']
    cherrypy.server.socket_port = config['cherrypy']['port']


def start_cherrypy():
    try:
        cherrypy.engine.start()
    except IOError:
        logging.error(
            'Unable to bind to address ({0}, {1}'.format(
                cherrypy.server.socket_host,
                cherrypy.server.socket_port
            ))
        sys.exit(1)
    # Wait until the app is started before proceeding
    cherrypy.engine.wait(cherrypy.process.wspbus.states.STARTED)
    logging.info('CherryPy started')
    cherrypy.engine.block()


def main():
    if sys.version_info < (2, 6):
        print 'Requires Python 2.6 or greater'
        sys.exit(1)
    if not cherrypy.__version__.startswith('3.2'):
        print 'Requires CherryPy version 3.2 (use the included version)'
        sys.exit(1)

    log_utils.configure_logging(config['logging'])
    initialise_db()
    initialise_games()
    initialise_cherrypy()
    try:
        start_cherrypy()
    except Exception, ex:
        print str(ex)


if __name__ == '__main__':
    main()
