import hashlib
import os
import uuid

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref

from game_on import database_helper


Base = declarative_base()

#To allow easier access in importing modules
Session = None
connection = None

def connect_to_db(db_config):
    global connection, Session
    connection = database_helper.Connection(
        name=db_config['name'],
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        base = Base)

    Session = connection.Session


class ModelBase(
        database_helper.TableNameMixin,
        database_helper.UuidMixin,
        database_helper.DictMixin):

    @classmethod
    def _get_objects_for_user(self, user):
        """
        Get a DB query with all the objects which are visible to this user
        """
        return Session.query(self)


class User(ModelBase, Base):
    username = sa.Column(sa.String(100), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    password_hash = sa.Column(sa.String(200), nullable=False)
    is_admin = sa.Column(sa.Boolean(), default=False)

    @classmethod
    def _get_objects_for_user(cls, user):
        """
        Implement this to filter out what the user shouldn't see
        """
        objects = Session.query(cls)

        if not user.is_admin:
            #This user is not an admin; filter out all users but their own
            objects = objects.filter(
                uuid == user.uuid
            )

        return objects

    @classmethod
    def hash_password(cls, password, salt=None):
        if not salt:
            salt = uuid.uuid4().hex
        hash = hashlib.sha512(password + salt).hexdigest()
        return salt + ':' + hash

    def check_password(self, password):
        #Find the salt we used
        salt = self.password_hash.split(':')[0]
        #Get the hash again using that salt
        check_password_hash = User.hash_password(password, salt)
        #Check if this matches the existing hash
        return self.password_hash == check_password_hash


class Player(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(1000))
    is_public = sa.Column(sa.Boolean(), default=False)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('players', passive_deletes=True, cascade="all"))
    #Add extra info because I cant work out how to get it through f**king SqlAlchemy!
    setattr(creator_uuid, 'related_name', 'creator')
    setattr(creator_uuid, 'related_model', User)
