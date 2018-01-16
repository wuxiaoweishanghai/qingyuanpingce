#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
db
"""
import sqlalchemy
import sqlalchemy.orm
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from logger import setup_logging
setup_logging()

class DbOperation(object):
    """
    DbOperation
    """
    def __init__(self, db_host, db_port, db_user, db_passwd, db_dbname):

        self.logger = logging.getLogger("DbOperation")
        self.engine_str = None
        self.engine = None
        self.session = None
        self.connect = None

        self.db_user = db_user
        self.db_passwd = db_passwd
        self.db_host = db_host
        self.db_port = db_port
        self.db_dbname = db_dbname

        self.db_init()

    def db_init(self):
        """
        db_init
        """
        self.engine_str = self._build_engine_str()
        self.engine = sqlalchemy.create_engine(self.engine_str,
                                               echo=False,
                                               pool_recycle=600,
                                               connect_args =
                                               {'connect_timeout':86400})
        self.connect = self.engine.connect()
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

    def get_session(self):
        """
        get_session
        """
        return self.session

    def get_connection(self):
        """
        get_session
        """
        return self.connect

    def get_engine(self):
        """
        get_engine
        """
        return self.engine

    def _build_engine_str(self, dbtype="mysql"):
        """
        _build_engine_str
        """
        engine_str = None
        try:
            if dbtype == "mysql":
                engine_str = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % \
                             (self.db_user, self.db_passwd,
                              self.db_host, self.db_port, self.db_dbname)
            return engine_str
        except Exception as e:
            self.logger.exception(e)
            raise Exception

if "__main__" == __name__:

    pass
