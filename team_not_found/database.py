from gzip import GzipFile
import hashlib
import json
import os
import uuid

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref

from team_not_found import database_helper
from team_not_found.cfg import config

Base = declarative_base()

#To allow easier access in importing modules
Session = None
connection = None

def connect_to_db(db_config):
    global connection, Session
    connection = database_helper.Connection(
        base = Base,
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port'],
        name=db_config['name'],
    )

    Session = connection.Session


class ModelBase(
        database_helper.TableNameMixin,
        database_helper.UuidMixin,
        database_helper.CreateDateMixin):

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


class Team(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    is_public = sa.Column(sa.Boolean(), default=False)
    path = sa.Column(sa.String(200), nullable=False)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('teams', passive_deletes=True, cascade="all"))

    #Add extra info because I cant work out how to get it through f**king SqlAlchemy!
    setattr(creator_uuid, 'related_name', 'creator')
    setattr(creator_uuid, 'related_model', User)

    def load_class(self):
        """
        Load the class referenced by self.path
        """
        import imp
        module_name = 'team_not_found.games.%s.external.%s' % (self.game, self.uuid)
        module = imp.load_source(module_name, self.path)
        return module.Team


class Match(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    state = sa.Column(sa.String(10), nullable=False) #WAITING, PLAYING, PLAYED
    team_1_uuid = sa.Column(sa.String(36), sa.ForeignKey('team.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team_1 = sa_orm.relationship('Team', foreign_keys=[team_1_uuid], backref=backref('matches_1', passive_deletes=True, cascade="all"))
    team_1_won = sa.Column(sa.Boolean(), nullable=True)
    team_2_uuid = sa.Column(sa.String(36), sa.ForeignKey('team.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team_2 = sa_orm.relationship('Team', foreign_keys=[team_2_uuid], backref=backref('matches_2', passive_deletes=True, cascade="all"))
    team_2_won = sa.Column(sa.Boolean(), nullable=True)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('matches', passive_deletes=True, cascade="all"))

    tournament_uuid = sa.Column(sa.String(36), sa.ForeignKey('tournament.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    tournament = sa_orm.relationship('Tournament', backref=backref('matches', passive_deletes=True, cascade="all"))

    def _get_path(self):
        filename = '%s-%s.json.gz' % (self.game, self.uuid)
        path = os.path.join(config['match']['folder'], filename)
        return path

    def get_flo_reader_compressed(self):
        """
        Return a FLO for this (still GZipped) matches results file.
        """
        return open(self._get_path(), 'rb')

    def get_flo_reader(self):
        """
        Return a FLO for this matches results file.
        """
        return GzipFile(self._get_path(), 'rb')

    def get_flo_writer(self):
        """
        Return a FLO for this matches results file.
        """
        return GzipFile(self._get_path(), 'wb')


class Tournament(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    tournament_type = sa.Column(sa.String(100), nullable=False)
    best_of = sa.Column(sa.Integer, nullable=False)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('tournaments', passive_deletes=True, cascade="all"))

    teams = sa_orm.relationship('Team', secondary='tournamentteam', backref='tournaments')


class TournamentTeam(ModelBase, Base):
    tournament_uuid = sa.Column(sa.String(36), sa.ForeignKey('tournament.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    tournament = sa_orm.relationship('Tournament', backref=backref('tournament_teams', passive_deletes=True, cascade="all"))
    team_uuid = sa.Column(sa.String(36), sa.ForeignKey('team.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team = sa_orm.relationship('Team', backref=backref('tournament_teams', passive_deletes=True, cascade="all"))
