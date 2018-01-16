#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import json
import sys
import logging
import time
import redis
import commands
import datetime
import ConfigParser
import multiprocessing
from operatedb import OperateDB
reload(sys)
sys.setdefaultencoding( "utf-8" )

global file_record
file_record = {}
global reason
global work_flow
work_flow = {}

def get_file_list(rootdir):
    """
    get file list
    """
    global reason
    filelist = []
    updatefilelist = []
    for root, dir, filenames in os.walk(rootdir):
        pattern = re.compile(".*cpu-publish-mq_log.*")
        for filename in filenames:
            result = pattern.match(filename)
            if result != None:
                filelist.append(os.path.join(root, filename))
    filelist = sorted(filelist)
    for filename in filelist:
        cmd = "wc -l %s"%(filename)
        output = commands.getoutput(cmd)
        count = int(output.split(' ')[0])
        if reason in file_record.keys():
            if filename in file_record[reason].keys():
                if count != file_record[reason][filename]:
                    updatefilelist.append(filename)
                else:
                    continue
            else:
                updatefilelist.append(filename)
        else:
            updatefilelist.append(filename)
    return updatefilelist
        
def handle_file(filename):
    """
    handle the file
    """
    global reason
    global work_flow
    try:
        cpu_publish_log = open(filename,'r')
    except BaseException, e:
        logging.warning("open cpu_pulish_log failed %s"%(e))
        return work_flow
    index = int(get_index(filename))
    count = 0
    with open(filename, 'r') as fp:
        if index ==0:
            line = fp.readline()
            while len(line) != 0:
                work_flow = get_work_flow(line)
                count = count + 1
                line = fp.readline()
        else:
            while index != 0:
                line = fp.readline()
                index = index - 1
                count = count + 1
            while len(line) != 0:
                work_flow = get_work_flow(line)
                count = count + 1
                line = fp.readline()
    fp.close()
    file_record[reason][filename] = count
    return work_flow

def get_index(filename):
    """
    get file index
    """
    global file_record
    global reason
    index = 0
    if filename in file_record[reason].keys():
        index = file_record[reason][filename]
    return index
    
def handle_time(result):
    """
    handle the time
    """
    results = result.split(" ")
    date = results[0] + " " + results[1]
    date = date.replace("[","")
    dates = date.split(" ")
    year = dates[0].split("-")[0]
    month = dates[0].split("-")[1]
    day = dates[0].split("-")[2]
    hour = dates[1]
    hours = hour.split(":")
    minu = int(hours[1])
    minu = str((minu / 5) * 5)
    if len(minu) < 2:
        minu = "0" + minu
    updatetime = year + "-" + month + "-" + day + " " + str(hours[0]) + ":" + minu + ":" + "00"
    return updatetime
    
def get_work_flow(line):
    """
    get work flow
    """
    global reason
    pattern = re.compile(".*CPUNIWorkerRunnable.*%s.*"%(reason))
    result = pattern.match(line)
    if ( result != None):
        result = result.group()
        date = handle_time(result)
        if date not in work_flow.keys():
            work_flow[date] = 1
        else:
            work_flow[date] += 1
    return work_flow
    
def run():
    """
    run the mian process
    """
    global file_record
    global reason
    global work_flow
    reason = sys.argv[1]
    table = sys.argv[2]
    logging.basicConfig(level=logging.INFO,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename='newsworkflow_%s.log'%(table),
            filemode='w')
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    pool = redis.ConnectionPool(host='localhost', port=6386, db=0)
    redis_data = redis.Redis(connection_pool=pool)
    file_record[reason] = redis_data.hgetall(reason)
    while True:
        rootdir = "../cpu_publish_news_mq/"
        filelist = get_file_list(rootdir)
        filelist = sorted(filelist)
        if len(filelist) == 0:
            continue
        else:
            for filename in filelist:
                work_flow = handle_file(filename)
                now = datetime.datetime.now()
                now.strftime('%Y-%m-%d 00:00:00')
                now = str(now).split(' ')[0] + "%"
                if len(work_flow.keys()) != 0:
                    sql = "select reason, time from work_flow_news_%s where time like \'%s\' order by time desc"%(table, now)
                    logging.info("sql is %s"%(sql))
                    try:
                        cursor = operatedb.selectsql(sql)
                        results = cursor.fetchall()
                    except BaseException, e:
                        logging.warning("get reason, time result failed %s"%(e))
                    timelist = []
                    if len(results) == 0:
                        datelist = sorted(work_flow.keys())
                        for i in range(0, len(datelist)):
                            sql = "insert into work_flow_news_%s\
                                    (time, count, reason) values (\'%s\', \'%s\', \'%s\')"\
                                    %(table, datelist[i], work_flow[datelist[i]], reason)
                            logging.info("sql is %s"%(sql))
                            operatedb.executesql(sql)
                            work_flow.pop(datelist[i])
                    else:
                        for result in results:
                            timelist.append(result[1])
                        datelist = sorted(work_flow.keys())
                        for i in range(0, len(datelist)):
                            if ( datelist[i] in timelist and result[0] == reason):
                                sql = "update work_flow_news_%s\
                                        set count = count + %s where\
                                        time = \'%s\' and reason = \'%s\'"%(table, work_flow[datelist[i]], datelist[i], reason)
                                logging.info("sql is %s"%(sql))
                            else:
                                sql = "insert into work_flow_news_%s\
                                        (time, count, reason) values (\'%s\', \'%s\', \'%s\')"\
                                        %(table, datelist[i], work_flow[datelist[i]], reason)
                                logging.info("sql is %s"%(sql))
                            operatedb.executesql(sql)
                            logging.info("save to db success image number as %s"%(work_flow[datelist[i]]))
                            work_flow.pop(datelist[i])
                else:
                    continue
                redis_data.hset(reason, filename, file_record[reason][filename])
            operatedb.disconnect()
        
if __name__ == '__main__':
    run()
