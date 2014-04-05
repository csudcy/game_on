import logging
import uuid
import re
import os

#Do not remove these imports (some of them are just to allow easier importing in other modules)
from sqlalchemy import exc as sa_exc
from sqlalchemy import func as sa_func
from sqlalchemy import orm as sa_orm
from sqlalchemy import types as sa_types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import expression as sa_exp
import sqlalchemy as sa


class Connection(object):
    def __init__(
            self,
            base,
            user,
            password,
            host,
            port,
            name,
        ):
        self.name = name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn_str = 'postgresql://%s:%s@%s:%s/%s' % (
            user,
            password,
            host,
            port,
            name)
        self.engine = self.get_engine()
        self.ensure_database_exists()
        self.Session = sa_orm.scoped_session(sa_orm.sessionmaker(bind = self.engine))
        self.Base = base

        #Deal with versioning
        class Version(
                UuidMixin,
                TableNameMixin,
                self.Base
            ):
            version = sa.Column(sa.Integer, nullable=False)
        self.Version = Version


    def get_engine(self):
        return sa.create_engine(
            self.conn_str,
            echo=False,
            #pool_size=cfg.db_pool_size(),
            #max_overflow=cfg.db_pool_overflow(),
            #pool_recycle=cfg.db_pool_recycle(),
            client_encoding='utf8')

    def ensure_database_exists(self):
        try:
            #Attempt to open a connection (without doing anything else)
            conn = self.engine.connect()
        except sa_exc.OperationalError:
            #Woops! Better create that database
            default_conn_str = 'postgresql://%s:%s@%s:%s/' % (
                self.user,
                self.password,
                self.host,
                self.port
            )
            #Make a temporary connection to the default database
            default_engine = sa.create_engine(
                default_conn_str,
                echo = False,
                isolation_level = 'AUTOCOMMIT',
                client_encoding = 'utf8'
            )
            #Create the database
            create_expression = sa_exp.text("CREATE DATABASE %s WITH OWNER = %s ENCODING 'UTF8'" % (
                self.name,
                self.user
            ))
            result = default_engine.execute(create_expression)
            result.close()
            #Make sure we don't leave the connection hanging
            default_engine.dispose()
        else:
            #If a connection is successfully created then return it to the pool
            conn.close()

    def sync(self, drop = False):
        if drop:
            try:
                tear_down_engine = self.get_engine()
                TearDownBase = declarative_base()
                TearDownBase.metadata.reflect(tear_down_engine)
                TearDownBase.metadata.drop_all(tear_down_engine)
                tear_down_engine.dispose()
            except:
                logging.warning('Error dropping database %s' % self.conn_str, exc_info=True)
                raise

        #Get the current version
        version_obj = None
        try:
            version_obj = self.Session.query(
                self.Version
            ).one()
        except sa.exc.ProgrammingError:
            #Table doesn't exist, create it
            self.Version.__table__.create(bind = self.engine)
            self.Session.commit()
        except sa.orm.exc.NoResultFound:
            #Table exists but there are no rows; we will add it shortly
            pass

        if version_obj is None:
            #Assume the DB is at version 0
            version_obj = self.Version(
                version = 0
            )
            self.Session.add(version_obj)
            self.Session.commit()

        #Get list of version from the file system
        current_directory = os.path.dirname(os.path.abspath(__file__))
        db_folder = os.path.join(current_directory, 'db')
        upgrade_scripts = {}
        for filename in os.listdir(db_folder):
            filepath = os.path.join(db_folder, filename)
            if not os.path.isfile(filepath):
                #Not a file
                continue
            print os.path.splitext(filepath)
            if os.path.splitext(filepath)[1].lower() != '.sql':
                #Not a sql file
                continue
            index = int(filename.split('.')[0])
            if index in upgrade_scripts:
                raise Exception('Duplicate upgrade scripts: "%s" and "%s"' % (upgrade_scripts[index], filename))
            upgrade_scripts[index] = filename

        #Check versions are contiguous and start at 0
        if 0 not in upgrade_scripts:
            raise Exception('Upgrade scripts dont start at 0!')
        max_version = max(upgrade_scripts.keys()) + 1
        if len(upgrade_scripts) != max_version:
            raise Exception('Upgrade scripts are not contiguous!')

        #Upgrade the database to the latest version
        while version_obj.version < max_version:
            #Run the script
            filename = upgrade_scripts[version_obj.version]
            path = os.path.join(db_folder, filename)
            with open(path, 'r') as f:
                sql = f.read()
            with self.engine.begin() as connection:
                connection.execute(sql)

            #Update the version
            version_obj.version += 1
            self.Session.commit()



class TableNameMixin(object):
    @declared_attr
    def __tablename__(cls):
        cls.verbose_name = cls.__name__
        return cls.__name__.lower()

class UuidMixin(object):
    uuid = sa.Column(sa.String(36), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class CreateDateMixin(object):
    create_date = sa.Column(sa.DateTime, default=sa_func.now(), nullable=False)
