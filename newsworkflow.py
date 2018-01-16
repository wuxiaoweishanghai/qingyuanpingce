#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import json
import sys
import logging
import datetime
from operatedb import OperateDB
import ConfigParser
def run():
    """
    get work flow
    """
    now = datetime.datetime.now()
    now.strftime('%Y-%m-%d 00:00:00')
    now_time = str(now).split(' ')[0] + "%"
    now = str(now).split(' ')[0] + " 00:00:00"
    operatedb = OperateDB("./mysql.conf") 
    operatedb.connect()
    configure = ConfigParser.ConfigParser()
    configure.read('reason.conf')
    figures = configure.options('reason')
    for figure in figures:
        sql_cmd = "select sum(count) as count from work_flow_news_%s where time like \'%s\'"%(figure, now_time)
        cursor = operatedb.selectsql(sql_cmd)
        result = cursor.fetchall()
        print result
        if result[0][0] != None:
            reason = configure.get('reason', figure)
            sql_cmd = "replace into work_flow_news (time, reason, count) values (\'%s\', \'%s\', %s)"%(now, reason, int(result[0][0]))
            print sql_cmd
            operatedb.executesql(sql_cmd)
   
if __name__ == '__main__':
    run()
    
