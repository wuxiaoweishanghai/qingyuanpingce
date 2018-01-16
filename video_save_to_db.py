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
from operatedb import OperateDB
reload(sys)
sys.setdefaultencoding( "utf-8" )

global file_record
file_record = {}
global work_flow
work_flow = {}
global save_to_db
save_to_db = {}

def get_file_list(rootdir):
    """
    获取文件夹目录
    返回更新的文件列表

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

def handle_file(filename):
    """
    处理文件并记录索引
    """
    global save_to_db
    try:
        cpu_publish_log = open(filename,'r')
    except BaseException, e:
        logging.warning("open cpu_pulish_log failed %s"%(e))
        return work_flow, save_to_db, dequeue
    index = get_record(filename)
    count = 0
    with open(filename, 'r') as fp:
        if index ==0:
            line = fp.readline()
            while len(line) != 0:
                save_to_db = save_to_dbsuccess(line)
                count = count + 1
                line = fp.readline()
        else:
            while index != 0:
                line = fp.readline()
                index = index - 1
                count = count + 1
            while len(line) != 0:
                save_to_db = save_to_dbsuccess(line)
                count = count + 1
                line = fp.readline()
    fp.close()
    file_record[filename]=count
    return save_to_db

def handle_time(result):
    """
    处理日志中的时间
    五分钟为维度划分时间区间
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

def save_to_dbsuccess(line):
    """
    保存入库成功的数据和对应的类目id
    """
    global save_to_db
    pattern = re.compile('.*Successfully put the video to db.*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        if date not in save_to_db.keys():
            save_to_db[date] = 1
        else:
            save_to_db[date] += 1
    return save_to_db

def main():
    """
    实时采集数据

    """
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='videosavetodb.log',
                filemode='w')
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    pool = redis.ConnectionPool(host='localhost', port=6389, db=0)
    redis_data = redis.Redis(connection_pool=pool)
    keys = redis_data.keys()
    for key in keys:
        file_record[key] = redis_data.get(key)
    while True:
        rootdir = "../cpu_publish_news_mq/"
        filelist = get_file_list(rootdir)
        filelist = sorted(filelist)
        if len(filelist) == 0:
            continue
        else:
            for filename in filelist:
                save_to_db = handle_file(filename)
            """
            策略过滤掉的图片数量以及对应的原因
            """
            """
            入库的图片数量以及对应的类目信息
            """
            now = datetime.datetime.now()
            begin_time = now.replace(hour = 00, minute = 15)
            end_time = now.replace(hour = 00, minute = 45)
            if now >= begin_time and now <= end_time:
                cmd = "sh -x ./clear_savevideodb.sh"
                os.system(cmd)
                sys.exit()
            else:
                now.strftime('%Y-%m-%d 00:00:00')
                now = str(now).split(' ')[0] + "%"
                sql = "select time from Video_Flow_Funnel where Stage = 400 and time like \'%s\' order by time desc"%(now)
                cursor = operatedb.selectsql(sql)
                timelist = []
                for row in cursor:
                    row = ''.join(row)
                    timelist.append(row)
                if len(save_to_db.keys()) != 0:
                    datelist = sorted(save_to_db.keys())
                    for i in range(0, len(datelist)):
                        if datelist[i] in timelist:
                            sql = "update Video_Flow_Funnel\
                                    set ImageNum = ImageNum + %s where\
                                    time = \'%s\' and Stage = 400"%(save_to_db[datelist[i]], datelist[i])
                            logging.info("save to db success image number as %s%s"%(save_to_db[datelist[i]], sql))
                        else:
                            sql = "insert into Video_Flow_Funnel\
                                    (time, Stage, ImageNum) values (\'%s\', \'400\', %s)"\
                                    %(datelist[i], save_to_db[datelist[i]])
                            logging.info("save to db success image number as %s%s"%(save_to_db[datelist[i]], sql))
                        operatedb.executesql(sql)
                        save_to_db.pop(datelist[i])
                else:
                    continue
                for filename in file_record.keys():
                    redis_data.set(filename, file_record[filename])
    operatedb.disconnect()

if __name__ == '__main__':
    main()
