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
from mq_handle import *
from operatedb import OperateDB
reload(sys)
sys.setdefaultencoding( "utf-8" )

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='apimonitor_handle.log',
                filemode='w')

def handle_file(filename):
    """ 
    处理文件并记录索引
    """
    global total_flow
    index = get_record(filename)
    count = 0
    with open(filename, 'r') as fp:
        if index ==0:
            line = fp.readline()
            while len(line) != 0:
                total_flow = get_total_flow(line)
                count = count + 1
                line = fp.readline()
        else:
            while index != 0:
                line = fp.readline()
                index = index - 1
                count = count + 1
            while len(line) != 0:
                total_flow = get_total_flow(line)
                count = count + 1
                line = fp.readline()
    fp.close()
    file_record[filename] = count
    return total_flow

def get_file_list(rootdir):
    """
    获取文件夹目录
    返回更新的文件列表

    """
    filelist = []
    updatefilelist = []
    for root, dir, filenames in os.walk(rootdir):
        pattern = re.compile(".*monitor_log.*")
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
                logging.info("更新的文件列表%s"%(filename))
                updatefilelist.append(filename)
            else:
                continue
        else:
            logging.info("更新的文件列表%s"%(filename))
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

def get_total_flow(line):
    """
    获取api接受到的总的请求
    """
    global total_flow
    pattern = re.compile('.*interface=PublishImageServiceImpl method=publish .*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        if date not in total_flow.keys():
            total_flow[date] = 1
        else:
            total_flow[date] += 1
    return total_flow

def main():
    """
    任务调度
    5分钟采集一次数据

    """
    time.sleep(100)
    global total_flow
    total_flow = {}
    global file_record
    file_record = {}
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    pool = redis.ConnectionPool(host='localhost', port=6381, db=0)
    redis_data = redis.Redis(connection_pool=pool)
    keys = redis_data.keys()
    if keys != None:
        for key in keys:
            file_record[key] = redis_data.get(key)
    while True:
        time.sleep(10)
        now = datetime.datetime.now()
    #    now_hour = str(now.strftime('%Y%m%d%H'))
    #    now_day = str(now.strftime('%Y%m%d'))
        rootdir = "../cpu_publish_image_api/"
        print rootdir
        filelist = get_file_list(rootdir)
        filelist = sorted(filelist)
        print filelist
        if len(filelist) == 0:
            continue
        else:
            for filename in filelist:
                total_flow = handle_file(filename)
            if len(total_flow.keys()) >= 2:
                datelist = sorted(total_flow.keys())
                for i in range(0, len(datelist) - 1):
                    sql_cmd = "replace into Image_Flow_Funnel (time, Stage, ImageNum) values ('%s', '%s', %s)" \
                        %(datelist[0], '100', total_flow[datelist[i]])
                    logging.info("api接受到的流量%s"%(sql_cmd))
                    operatedb.executesql(sql_cmd)
                    del total_flow[datelist[i]]
            else:
                continue
            for filename in file_record.keys():
              redis_data.set(filename, file_record[filename])
            continue
    operatedb.disconnect()

if __name__ == '__main__':
    main()
