import logging
import uuid
import re
import os

#Do not remove these imports (some of them are just to allow easier importing in other modules)
from sqlalchemy import exc as sa_exc
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
            name,
            host,
            port,
            user,
            password,
            base):
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
        self.Base.metadata.create_all(self.engine)

    def clear_data(self):
        for table in reversed(self.Base.metadata.sorted_tables):
            if not getattr(table, 'static_data', False):
                self.engine.execute(table.delete())


class TableNameMixin(object):
    @declared_attr
    def __tablename__(cls):
        cls.verbose_name = cls.__name__
        return cls.__name__.lower()

class UuidMixin(object):
    uuid = sa.Column(sa.String(36), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class DictMixin(object):
    to_dict_ignored_columns = ()

    def to_dict(self, include=None):
        """
        Serialise this model instance.
        Include is a dictionary of related objects to include in the serialised JSON.
        E.g. for Advertiser we could have
        {
            'screen_advertising_company': {},
            'brands': {
                'industry_subsector': {}
            }
        }
        BE CAREFUL: There are currently no size checks!
        NOTE: This will not serialise accross databases
        Heavily influenced by Producer & http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
        """
        object_dict = {}
        for column in self.__table__.columns:
            if column.name in self.to_dict_ignored_columns:
                continue
            val = getattr(self, column.name)
            #See if we need to do any conversions
            if isinstance(val.__class__, DeclarativeMeta) or (isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
                #This is a relation, check if we're expanding it
                if column.name in include:
                    raise Exception('We cant serialise sub objects yet!')
                    #We want to serialise this object too
                    func = lambda obj: obj.to_dict(include[column.name])
                else:
                    #Just provide the id(s)
                    func = lambda obj: obj.uuid
                #Now actually serialise them
                if isinstance(val, list):
                    val = [func(v) for v in val]
                else:
                    val = func(val)
            #TODO: DateTime's
            object_dict[column.name] = val

        return object_dict

    def from_dict(self, object_dict):
        """
        Update this model instance from a serialised version.
        NOTE: Does not handle nested updates
        Heavily influenced by Producer
        """
        for column in self.__table__.columns:
            if column.name not in object_dict:
                continue
            val = object_dict[column.name]
            #See if we need to do any conversions
            #TODO: DateTime's
            setattr(self, column.name, val)

class StaticDataMixin(object):
    @classmethod
    def __declare_last__(cls):
        cls.__table__.static_data = True
