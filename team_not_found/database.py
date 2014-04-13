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
    email = sa.Column(sa.String(100), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    is_confirmed = sa.Column(sa.Boolean(), default=False)
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

    def get_confirm_code(self):
        return hashlib.md5('%s:%s:%s' % (config['secret'], self.uuid, self.email)).hexdigest()

    def send_confirmation_email(self):
        pass


class Team(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    is_public = sa.Column(sa.Boolean(), default=False)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('teams', lazy='dynamic', passive_deletes=True, cascade="all"))

    #Add extra info because I cant work out how to get it through f**king SqlAlchemy!
    setattr(creator_uuid, 'related_name', 'creator')
    setattr(creator_uuid, 'related_model', User)

    def get_team_file(self, team_file_uuid=None):
        """
        Get the team_file <team_file_uuid or latest>
        """
        if team_file_uuid is None or team_file_uuid == '':
            return self.team_files.order_by(
                TeamFile.version.desc()
            ).first()
        return self.team_files.filter(
            TeamFile.uuid == team_file_uuid
        ).one()

    def add_file(self, new_contents):
        """
        Create a new team_file & save contents to it.
        If new_contents is the same as the latest contents, don't create a new team_file.
        """
        #Get the current_team_file
        current_team_file = self.get_team_file()

        if current_team_file:
            #Check the current_contents & new_contents are different
            current_contents = current_team_file.read_file()
            if current_contents == new_contents:
                #The file hasn't changed, return the current_team_file
                return current_team_file

        #Create the new_team_file
        version = 0
        if current_team_file:
            version = current_team_file.version + 1
        path = os.path.join(
            config['team']['folder'],
            '%s-%s.py' % (self.uuid, version),
        )
        new_team_file = TeamFile(
            team=self,
            version=version,
            path=path,
        )

        #Write new_contents to the new_team_file
        new_team_file.write_file(new_contents)

        #Save the new new_team_file
        Session.add(new_team_file)
        Session.commit()

        #Let the caller know which new_team_file we added
        return new_team_file


class TeamFile(ModelBase, Base):
    team_uuid = sa.Column(sa.String(36), sa.ForeignKey('team.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team = sa_orm.relationship('Team', backref=backref('team_files', lazy='dynamic', passive_deletes=True, cascade="all"))
    path = sa.Column(sa.String(200), nullable=False)
    version = sa.Column(sa.Integer, nullable=False)

    def load_class(self):
        """
        Load this team_file
        """
        import imp
        module_name = 'team_not_found.games.%s.external.%s' % (self.team.game, self.uuid)
        module = imp.load_source(module_name, self.path)
        return module.Team

    def read_file(self):
        """
        Return the contents of this team_file.
        """
        with self.get_flo_reader() as f:
            return f.read()

    def get_flo_reader(self):
        """
        Return a FLO for reading this team_file.
        """
        return open(self.path, 'rb')

    def write_file(self, contents):
        """
        Write contents to this team_file.
        """
        with self.get_flo_writer() as f:
            f.write(contents)

    def get_flo_writer(self):
        """
        Return a FLO for writing this team_file.
        """
        return open(self.path, 'wb')


class Match(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    state = sa.Column(sa.String(10), nullable=False) #WAITING, PLAYING, PLAYED
    team_file_1_uuid = sa.Column(sa.String(36), sa.ForeignKey('teamfile.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team_file_1 = sa_orm.relationship('TeamFile', foreign_keys=[team_file_1_uuid], backref=backref('matches_1', lazy='dynamic', passive_deletes=True, cascade="all"))
    team_1_won = sa.Column(sa.Boolean(), nullable=True)
    team_file_2_uuid = sa.Column(sa.String(36), sa.ForeignKey('teamfile.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team_file_2 = sa_orm.relationship('TeamFile', foreign_keys=[team_file_2_uuid], backref=backref('matches_2', lazy='dynamic', passive_deletes=True, cascade="all"))
    team_2_won = sa.Column(sa.Boolean(), nullable=True)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('matches', lazy='dynamic', passive_deletes=True, cascade="all"))

    tournament_uuid = sa.Column(sa.String(36), sa.ForeignKey('tournament.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    tournament = sa_orm.relationship('Tournament', backref=backref('matches', lazy='dynamic', passive_deletes=True, cascade="all"))

    def _get_path(self):
        filename = '%s-%s.json.gz' % (self.game, self.uuid)
        path = os.path.join(config['match']['folder'], filename)
        return path

    def get_flo_reader_compressed(self):
        """
        Return a FLO for reading this (still GZipped) matches results file.
        """
        return open(self._get_path(), 'rb')

    def get_flo_reader(self):
        """
        Return a FLO for reading this matches results file.
        """
        return GzipFile(self._get_path(), 'rb')

    def get_flo_writer(self):
        """
        Return a FLO for writing this matches results file.
        """
        return GzipFile(self._get_path(), 'wb')


class Tournament(ModelBase, Base):
    game = sa.Column(sa.String(100), nullable=False)
    tournament_type = sa.Column(sa.String(100), nullable=False)
    best_of = sa.Column(sa.Integer, nullable=False)
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('tournaments', lazy='dynamic', passive_deletes=True, cascade="all"))

    team_files = sa_orm.relationship('TeamFile', secondary='tournamentteamfile', backref='tournaments')


class TournamentTeamFile(ModelBase, Base):
    tournament_uuid = sa.Column(sa.String(36), sa.ForeignKey('tournament.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    tournament = sa_orm.relationship('Tournament', backref=backref('tournament_team_files', lazy='dynamic', passive_deletes=True, cascade="all"))
    team_file_uuid = sa.Column(sa.String(36), sa.ForeignKey('teamfile.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team_file = sa_orm.relationship('TeamFile', backref=backref('tournament_team_files', lazy='dynamic', passive_deletes=True, cascade="all"))
