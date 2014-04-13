import os

import cherrypy

from team_not_found import database as db
from team_not_found.utils import mount as mount_utils


#Handle noauth URLs
class Tree(object):
    @cherrypy.expose
    @cherrypy.tools.jinja2(template='splash.html')
    def index(self, redirect=None, email=None, password=None, confirm_code=None):
        user = None
        if email:
            try:
                #Find the user
                user = db.Session.query(
                    db.User
                ).filter(
                    db.User.email == email
                ).one()
            except:
                # Hope this was a db error...
                pass

        # keep a list of messages to show on the frontend
        messages = []

        if cherrypy.request.method == 'POST':
            # Trying to login...
            if user and user.check_password(password):
                # Password is good, check they are confirmed
                if user.is_confirmed:
                    #All is good!
                    cherrypy.session['user_uuid'] = user.uuid
                    cherrypy.session.save()
                    raise cherrypy.HTTPRedirect(redirect or '/tnf/')

                #If we're here, user & pass is good but they're not confirmed
                messages.append({
                    'class': 'error',
                    'text': 'You have not confirmed your email address',
                })

                #Resend confirmation email just in case...
                user.send_confirmation_email()
                messages.append({
                    'class': 'info',
                    'text': 'The confirmation email has been resent',
                })
            else:
                messages.append({
                    'class': 'error',
                    'text': 'Email or password incorrect',
                })
        elif user and confirm_code:
            # Trying to confirm a user account
            if user.get_confirm_code() == confirm_code:
                # Mark the user as confirmed
                user.is_confirmed = True
                db.Session.commit()

                # Tell the user they are confirmed
                messages.append({
                    'class': 'info',
                    'text': 'Thank you for confirming your email',
                })
                messages.append({
                    'class': 'info',
                    'text': 'You may now login',
                })
            else:
                # Tell the user they failed!
                messages.append({
                    'class': 'error',
                    'text': 'Email or confirm_code incorrect',
                })

        return {
            'messages': messages,
            'redirect': redirect,
            'email': email,
        }

    @cherrypy.expose
    def logout(self):
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    @cherrypy.tools.jinja2(template='create_user.html')
    def create_user(self, email=None, name=None, password=None):
        messages = []
        show_form = True
        if cherrypy.request.method == 'POST':
            #Trying to create a new user...
            if not (email and name and password):
                messages.append({
                    'class': 'error',
                    'text': 'All fields must be filled in',
                })
            else:
                #Check a user doesnt exist with that email already
                existing_user_count = db.Session.query(
                    db.User
                ).filter(
                    db.User.email == email
                ).count()

                if existing_user_count != 0:
                    messages.append({
                        'class': 'error',
                        'text': 'That email address is already taken',
                    })
                else:
                    #Create the user now!
                    user = db.User(
                        email=email,
                        name=name,
                        is_confirmed=False,
                        password_hash=db.User.hash_password(password),
                        is_admin=False,
                    )
                    db.Session.add(user)
                    db.Session.commit()

                    #Tell the user
                    messages.append({
                        'class': 'info',
                        'text': 'Thanks for registering',
                    })

                    #Send confirmation email
                    user.send_confirmation_email()
                    messages.append({
                        'class': 'info',
                        'text': 'Please confirm your email before logging in',
                    })

                    #Don't show the form again
                    show_form = False

        return {
            'messages': messages,
            'show_form': show_form,
            'email': email,
            'name': name,
        }


def mount_tree():
    mount_utils.add_all_trees(
        os.path.dirname(os.path.abspath(__file__)),
        globals(),
        Tree)
    return Tree()
