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
from multiprocessing import Process
reload(sys)
sys.setdefaultencoding( "utf-8" )

class newsworkflow(Process):
    
    def __init__(self, reason, table):
        """
        init
        """
        super(newsworkflow, self).__init__()
        self.work_flow = {}
        self.file_record = {}
        self.reason = reason
        self.table = table
        
    def get_file_list(self, rootdir):
        """
        get file list
        """
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
            if self.reason in self.file_record.keys():
                if filename in self.file_record[self.reason].keys():
                    if count != self.file_record[self.reason][filename]:
                        updatefilelist.append(filename)
                    else:
                        continue
                else:
                    updatefilelist.append(filename)
            else:
                updatefilelist.append(filename)
        return updatefilelist
    
    def handle_file(self, filename):
        """
        handle the file
        """
        try:
            cpu_publish_log = open(filename,'r')
        except BaseException, e:
            logging.warning("open cpu_pulish_log failed %s"%(e))
            return self.work_flow
        index = int(self.get_index(filename))
        count = 0
        with open(filename, 'r') as fp:
            if index ==0:
                line = fp.readline()
                while len(line) != 0:
                    self.work_flow = self.get_work_flow(line)
                    count = count + 1
                    line = fp.readline()
            else:
                while index != 0:
                    line = fp.readline()
                    index = index - 1
                    count = count + 1
                while len(line) != 0:
                    self.work_flow = self.get_work_flow(line)
                    count = count + 1
                    line = fp.readline()
            fp.close()
            self.file_record[reason][filename] = count
        return self.work_flow
    
    def get_index(self, filename):
        """
        get file index
        """
        index = 0
        if filename in self.file_record[reason].keys():
            index = self.file_record[reason][filename]
        return index
    
    def handle_time(self, result):
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
    
    def get_work_flow(self, line):
        """
        get work flow
        """
        pattern = re.compile(".*CPUNIWorkerRunnable.*%s.*"%(self.reason))
        result = pattern.match(line)
        if ( result != None):
            result = result.group()
            date = self.handle_time(result)
            if date not in self.work_flow.keys():
                self.work_flow[date] = 1
            else:
                self.work_flow[date] += 1
        return self.work_flow
    
    def run(self):
        """
        run the mian process
        """
        logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='newsworkflow_%s.log'%(self.table),
                filemode='w')
        operatedb = OperateDB("./mysql.conf")
        pool = redis.ConnectionPool(host='localhost', port=6386, db=0)
        redis_data = redis.Redis(connection_pool=pool)
        self.file_record[reason] = redis_data.hgetall(reason)
        while True:
            rootdir = "../cpu_publish_news_mq/"
            filelist = self.get_file_list(rootdir)
            filelist = sorted(filelist)
            if len(filelist) == 0:
                continue
            else:
                for filename in filelist:
                    self.work_flow = self.handle_file(filename)
                    now = datetime.datetime.now()
                    now.strftime('%Y-%m-%d 00:00:00')
                    now = str(now).split(' ')[0] + "%"
                    if len(self.work_flow.keys()) != 0:
                        sql = "select reason, time from work_flow_news_%s where time like \'%s\' order by time desc"%(self.table, now)
                        logging.info("sql is %s"%(sql))
                        try:
                            operatedb.connect()
                            cursor = operatedb.selectsql(sql)
                            results = cursor.fetchall()
                        except BaseException, e:
                            logging.warning("get reason, time result failed %s"%(e))
                        timelist = []
                        if len(results) == 0:
                            datelist = sorted(self.work_flow.keys())
                            for i in range(0, len(datelist)):
                                sql = "insert into work_flow_news_%s\
                                        (time, count, reason) values (\'%s\', \'%s\', \'%s\')"\
                                        %(self.table, datelist[i], self.work_flow[datelist[i]], self.reason)
                                logging.info("sql is %s"%(sql))
                                operatedb.executesql(sql)
                                self.work_flow.pop(datelist[i])
                        else:
                            for result in results:
                                timelist.append(result[1])
                            datelist = sorted(self.work_flow.keys())
                            for i in range(0, len(datelist)):
                                if ( datelist[i] in timelist and result[0] == reason):
                                    sql = "update work_flow_news_%s\
                                            set count = count + %s where\
                                            time = \'%s\' and reason = \'%s\'"%(self.table, self.work_flow[datelist[i]], datelist[i], reason)
                                    logging.info("sql is %s"%(sql))
                                else:
                                    sql = "insert into work_flow_news_%s\
                                            (time, count, reason) values (\'%s\', \'%s\', \'%s\')"\
                                            %(self.table, datelist[i], self.work_flow[datelist[i]], reason)
                                    logging.info("sql is %s"%(sql))
                                operatedb.executesql(sql)
                                logging.info("save to db success image number as %s"%(self.work_flow[datelist[i]]))
                                self.work_flow.pop(datelist[i])
                    else:
                        continue
                    redis_data.hset(reason, filename, self.file_record[reason][filename])
                    operatedb.disconnect()
        
if __name__ == '__main__':
    configure = ConfigParser.ConfigParser()
    configure.read('reason.conf')
    figures = configure.options('reason')
    processes = []
    for figure in figures:
        reason = configure.get('reason', figure)
        process = newsworkflow(reason, figure)
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
