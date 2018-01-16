#!/usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import MySQLdb
import logging

class OperateDB(object):
    def __init__(self, mysqlconf = "./mysql.conf"):
        """
        初始化数据库参数
        """
        self.mysqlconf = ConfigParser.ConfigParser()
        self.mysqlconf.read(mysqlconf)
        options = self.mysqlconf.items("database")
        self.database_host = str(options[0][1])
        self.database_port = int(str(options[1][1]))
        self.database_user = str(options[2][1])
        self.database_passwd = str(options[3][1])
        self.database_name = str(options[4][1])
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            logging.info("Begin to connect to database")
            self.conn = MySQLdb.connect(host = '10.119.25.50',\
                    port = 3306,\
                    user = 'cpuqa',\
                    passwd = 'MhxzKhl',\
                    db = 'evaluating')
            self.cursor = self.conn.cursor()
            logging.info("Successfully connected to database")
        except BaseException, e:
            logging.warning("Connect to database failed %s"%(e))

                                                                                                                                                            
    def disconnect(self):
        try:
            logging.info("Begin to disconnect to database")
            self.cursor.close()
            self.conn.close()
            logging.info(" Successfully connected to database")
        except BaseException, e:
            logging.warning("disconnect from database failed %s"%(e))

    def executesql(self, sql_cmd):
        try:
            logging.info("Begin to insert into image tables")
            self.checkconnect()
            self.cursor.execute(sql_cmd)
            self.conn.commit()
        except BaseException, e:
            self.conn.rollback()
            logging.warning("execuet sql failed %s"%(e))

    def selectsql(self, sql_cmd):
        try:
            logging.info("Begin to select from image tables")
            self.checkconnect()
            self.cursor.execute(sql_cmd)
            return self.cursor
        except BaseException, e:
            logging.warning("Failed to select sql from image tables %s"%(e))

    def checkconnect(self):
        try:
            logging.info("Begin to check connect exists")
            if self.conn == None:
                self.conn = MySQLdb.connect(host = '10.119.25.50',\
                        port = 3306,\
                        user = 'cpuqa',\
                        passwd = 'MhxzKhl',\
                        db = 'evaluating')
                self.cursor = self.conn.cursor()
            else:
                self.conn.ping(True)
        except BaseException, e:
            logging.warning("connect to mysql db error %s"%(e))
