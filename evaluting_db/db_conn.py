#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
db_conn
"""
import sys
import logging
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy import select
from contextlib import contextmanager
from common.db import DbOperation
from common.config import YamlConfigReader

reload(sys)
sys.setdefaultencoding("utf-8")
from common.logger import setup_logging

class Evaluting(object):
    """
    evaluting db
    """
    def __init__(self):
        self.db_user = None
        self.db_passwd = None
        self.db_host = None
        self.db_port = None
        self.db_dbname = None
        self.init_db_params()
        db_opt = DbOperation(self.db_host, self.db_port,
                self.db_user, self.db_passwd, self.db_dbname)
        self.session = db_opt.get_session()

    def init_db_params(self):
        """
        init_db_params
        """
        yamp_config = YamlConfigReader("./conf/db_conf.yaml")
        db_conf_dict = yamp_config.get_config_dict()
        self.db_user = db_conf_dict["evaluating"]["user"]
        self.db_passwd = db_conf_dict["evaluating"]["passwd"]
        self.db_host = db_conf_dict["evaluating"]["host"]
        self.db_port = db_conf_dict["evaluating"]["port"]
        self.db_dbname = db_conf_dict["evaluating"]["dbname"]

    def get_session(self):
        """
        get session
        """
        return self.session

class CpuIc(object):
    """
    cpu_ic db
    """
    def __init__(self):
        self.db_user = None
        self.db_passwd = None
        self.db_host = None
        self.db_port = None
        self.db_dbname = None
        self.init_db_params()
        db_opt = DbOperation(self.db_host, self.db_port,
                self.db_user, self.db_passwd, self.db_dbname)
        self.session = db_opt.get_session()

    def init_db_params(self):
        """
        init_db_params
        """
        yamp_config = YamlConfigReader("./conf/db_conf.yaml")
        db_conf_dict = yamp_config.get_config_dict()
        self.db_user = db_conf_dict["cpu_ic"]["user"]
        self.db_passwd = db_conf_dict["cpu_ic"]["passwd"]
        self.db_host = db_conf_dict["cpu_ic"]["host"]
        self.db_port = db_conf_dict["cpu_ic"]["port"]
        self.db_dbname = db_conf_dict["cpu_ic"]["dbname"]
    
    def get_session(self):
        """
        get session
        """
        return self.session

class CpuCc(object):
    """
    cpu_ic db
    """
    def __init__(self):
        self.db_user = None
        self.db_passwd = None
        self.db_host = None
        self.db_port = None
        self.db_dbname = None
        self.init_db_params()
        db_opt = DbOperation(self.db_host, self.db_port,
                self.db_user, self.db_passwd, self.db_dbname)
        self.session = db_opt.get_session()

    def init_db_params(self):
        """
        init_db_params
        """
        yamp_config = YamlConfigReader("./conf/db_conf.yaml")
        db_conf_dict = yamp_config.get_config_dict()
        self.db_user = db_conf_dict["cpu_cc"]["user"]
        self.db_passwd = db_conf_dict["cpu_cc"]["passwd"]
        self.db_host = db_conf_dict["cpu_cc"]["host"]
        self.db_port = db_conf_dict["cpu_ic"]["port"]
        self.db_dbname = db_conf_dict["cpu_cc"]["dbname"]

    def get_session(self):
        """
        get session
        """
        return self.session
    
class CpuVc(object):
    """
    cpu_vc db
    """
    def __init__(self):
        self.db_user = None
        self.db_passwd = None
        self.db_host = None
        self.db_port = None
        self.db_dbname = None
        self.init_db_params()
        db_opt = DbOperation(self.db_host, self.db_port,
                self.db_user, self.db_passwd, self.db_dbname)
        self.session = db_opt.get_session()

    def init_db_params(self):
        """
        init_db_params
        """
        yamp_config = YamlConfigReader("./conf/db_conf.yaml")
        db_conf_dict = yamp_config.get_config_dict()
        self.db_user = db_conf_dict["cpu_vc"]["user"]
        self.db_passwd = db_conf_dict["cpu_vc"]["passwd"]
        self.db_host = db_conf_dict["cpu_vc"]["host"]
        self.db_port = db_conf_dict["cpu_vc"]["port"]
        self.db_dbname = db_conf_dict["cpu_vc"]["dbname"]

    def get_session(self):
        """
        get session
        """
        return self.session

cpu_ic = CpuIc()
evaluting = Evaluting()
cpu_cc = CpuCc()
cpu_vc = CpuVc()

@contextmanager
def session_cpu_ic():
    """
    connect to cpu_ic
    """
    session = cpu_ic.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception("db error, roll back:%s" % str(e))
    finally:
        session.close()
        
@contextmanager
def session_evaluting():
    """
    connect to evaluating
    """
    session = evaluting.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception("db error, roll back:%s" % str(e))
    finally:
        session.close()

@contextmanager
def session_cpu_cc():
    """
    connect to cpu cc
    """
    session = cpu_cc.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception("db error, roll back:%s" % str(e))
    finally:
        session.close()

@contextmanager
def session_cpu_vc():
    """
    connect to cpu vc
    """
    session = cpu_vc.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception("db error, roll back:%s" % str(e))
    finally:
        session.close()
