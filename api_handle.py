#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import json
import sys
import logging
import time
import commands
import redis
import datetime
from dequeue import handle_time
from operatedb import OperateDB
reload(sys)
sys.setdefaultencoding( "utf-8" )

global file_record
file_record = {}
global flow_funnel
flow_funnel = {}
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='api_handle.log',
                filemode='w')

def handle_file(filename):
    """ 
    处理文件并记录索引
    """
    global flow_funnel
    index = get_record(filename)
    count = 0 
    with open(filename, 'r') as fp:
        if index ==0:
            line = fp.readline()
            while len(line) != 0:
                flow_funnel = get_enqueue_dequeue(line)
                count = count + 1
                line = fp.readline()
        else:
            while index != 0:
                line = fp.readline()
                index = index - 1
                count = count + 1
            while len(line) != 0:
                flow_funnel = get_enqueue_dequeue(line)
                count = count + 1
                line = fp.readline()
    fp.close()
    file_record[filename] = count
    return flow_funnel

def get_file_list(rootdir):
    """
    获取文件夹目录
    返回更新的文件列表

    """
    filelist = []
    updatefilelist = []
    for root, dir, filenames in os.walk(rootdir):
        pattern = re.compile(".*common_log.*")
        for filename in filenames:
            result = pattern.match(filename)
            if result != None:
                filelist.append(os.path.join(root, filename))
    filelist = sorted(filelist)
    for i in range(len(filelist)):
        cmd = "wc -l %s"%(filelist[i])
        output = commands.getoutput(cmd)
        count = int(output.split(' ')[0])
        filename = output.split(' ')[1]
        if filename in file_record.keys():
            if count != file_record[filename]:
                updatefilelist.append(filename)
            else:
                continue
        else:
            updatefilelist.append(filename)
    return updatefilelist

def get_record(filename):
    """
    获取文件记录索引
    """
    global file_record
    index = 0
    if filename in file_record.keys():
        return int(file_record[filename])
    else:
        return index

def get_enqueue_dequeue(line):
    """
    筛选出入队列的数据
    """
    global flow_funnel
    pattern = re.compile('.*enqueue success.*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        if date == None:
            return flow_funnel
        else:
            if date not in flow_funnel.keys():
                flow_funnel[date] = 1
            else:
                flow_funnel[date] += 1
    return flow_funnel

def main():
    """
    任务调度
    5分钟采集一次数据

    """
    global flow_funnel
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    pool = redis.ConnectionPool(host='localhost', port=6380, db=0)
    redis_data = redis.Redis(connection_pool=pool)
    keys = redis_data.keys()
    for key in keys:
        file_record[key] = redis_data.get(key)
    while True:
        rootdir = "../cpu_publish_image_api/"
        #now = datetime.datetime.now()
        #begin_time = now.replace(hour = 00, minute = 15)
        #end_time = now.replace(hour = 00, minute = 45)
        #if now >= begin_time and now <= end_time:
        #    cmd = 'sh -x ./clear_api.sh'
        #    os.system(cmd)
        #    sys.exit()
        #else:
        filelist = get_file_list(rootdir)
        filelist = sorted(filelist)
        if len(filelist) == 0:
            continue
        else:
            for filename in filelist:
                flow_funnel = handle_file(filename)
            if len(flow_funnel.keys()) != 0:
                now = datetime.datetime.now()
                now = now.strftime('%Y-%M-%D %H:%M:%S')
                now = now.split(' ')[0] + "%"
                sql = "select time from Image_Flow_Funnel where Stage = 200 and time like \'%s\' order by time desc"%(now)
                cursor = operatedb.selectsql(sql)
                timelist = []
                for row in cursor:
                    row = ''.join(row)
                    timelist.append(row)
                datelist = sorted(flow_funnel.keys())
                for i in range(0, len(datelist) - 1):
                    if datelist[i] in timelist:
                        sql = "update Image_Flow_Funnel\
                                set ImageNum = ImageNum + %s where Stage = 200 and time = \'%s\'"%(flow_funnel[datelist[i]], datelist[i])
                        logging.info("save to db success image number as %s%s"%(flow_funnel[datelist[i]], sql))
                    else:
                        sql = "insert into Image_Flow_Funnel\
                                (time, Stage, ImageNum) values (\'%s\', \'%s\', %s)"\
                                %(datelist[i], '200', flow_funnel[datelist[i]])
                        logging.info("save to db success image number as %s%s"%(flow_funnel[datelist[i]], sql)) 
                    operatedb.executesql(sql)
                    flow_funnel.pop(datelist[i])
            else:
                continue
            for filename in file_record.keys():
                redis_data.set(filename, file_record[filename])
    operatedb.disconnect()

if __name__ == '__main__':
    main()
