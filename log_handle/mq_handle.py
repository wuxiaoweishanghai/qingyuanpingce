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
global dequeue
dequeue = {}
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='mq_handle.log',
                filemode='w')

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
    global work_flow
    global save_to_db
    global dequeue
    try:
        cpu_publish_log = open(filename,'r')
    except BaseException, e:
        logging.warning("open cpu_pulish_log failed %s"%(e))
    index = get_record(filename)
    count = 0
    line = cpu_publish_log.readline()
    if index == 0:
        while len(line) !=0:
            count = count + 1
            line = cpu_publish_log.readline()
            work_flow = get_work_flow_interupt(line)
            save_to_db = save_to_dbsuccess(line)
            dequeue = get_dequeue_flow(line) 
        cpu_publish_log.close()
    else:
        while True:
            count = count + 1
            index = index - 1
            line = cpu_publish_log.readline()
            if index == 0:
                break
            else:
                continue
        while len(line) != 0:
            line = cpu_publish_log.readline()
            count = count + 1
            work_flow = get_work_flow_interupt(line)
            save_to_db = save_to_dbsuccess(line)
            dequeue = get_dequeue_flow(line)
        cpu_publish_log.close()
    file_record[filename]=count
    return work_flow, save_to_db, dequeue

def get_work_flow_interupt(line):
    """
    筛选出workflow阶段被过滤的数据
    """
    global work_flow
    pattern = re.compile('.*work flow unit execute interrupt.*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        result = result.split(" - ")
        log_format = result[1].split(",")
        reason = log_format[1]
        name = reason.split(':')[1]
        if date not in work_flow.keys():
            work_flow[date] = {}
            work_flow[date][name] = 1
        else:
            if name not in work_flow[date].keys():
                work_flow[date][name] = 1
            else:
                work_flow[date][name] += 1
    return work_flow

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

def get_dequeue_flow(line):
    """
    筛选出队列的图片数据
    """
    global dequeue
    pattern = re.compile('.*content dequeue*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        if date not in dequeue.keys():
            dequeue[date] = 1
        else:
            dequeue[date] += 1
    return dequeue

def save_to_dbsuccess(line):
    """
    保存入库成功的数据和对应的类目id
    """
    global save_to_db
    pattern = re.compile('.*save to db success.*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        imageinfo = result.split('imageSet:')[1]
        try:
            imageinfo = json.loads(imageinfo, encoding='utf-8')
        except BaseException, e:
            logging.warning("load json failed %s"%(e))
            return save_to_db
        categoryId =  imageinfo['categoryId']
        date = handle_time(result)
        if date not in save_to_db.keys():
            save_to_db[date] = {}
            if categoryId not in save_to_db[date].keys():
                save_to_db[date][categoryId] = 1
            else:
                save_to_db[date][categoryId] += 1
        else:
            if categoryId not in save_to_db[date].keys():
                save_to_db[date][categoryId] = 1
            else:
                save_to_db[date][categoryId] += 1
    return save_to_db

def main():
    """
    实时采集数据

    """
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    redis_data = redis.Redis(connection_pool=pool)
    keys = redis_data.keys()
    for key in keys:
        file_record[key] = redis_data.get(key)
    while True:
        time.sleep(10)
        now = datetime.datetime.now()
      #  now_hour = str(now.strftime('%Y%m%d%H'))
      #  now_day = str(now.strftime('%Y%m%d'))
        rootdir = "../cpu_publish_image_mq/"
        filelist = get_file_list(rootdir)
        filelist = sorted(filelist)
        if len(filelist) == 0:
            continue
        else:
            for filename in filelist:
                work_flow = handle_file(filename)[0]
                save_to_db = handle_file(filename)[1]
                dequeue = handle_file(filename)[2]
            """
            策略过滤掉的图片数量以及对应的原因
            """
            if len(work_flow.keys()) >= 2:
                datelist = sorted(work_flow.keys())
                for i in range(0, len(datelist) - 1):
                    for name in work_flow[datelist[i]].keys():
                        sql_cmd = "replace into work_flow_image\
                              (time, reason, count) values (\'%s\', \'%s\', %s)"\
                              %(datelist[i], name, work_flow[datelist[i]][name])
                        logging.info("插入过滤掉的图集数量及其对应的原因 %s"%(sql_cmd))
            
                        operatedb.executesql(sql_cmd)
                    work_flow.pop(datelist[i])
            """
            入库的图片数量以及对应的类目信息
            """
            if len(save_to_db.keys()) >= 2:
                datelist = sorted(save_to_db.keys())
                total_num = 0
                for i in range(0, len(datelist) - 1):
                    for categoryId in save_to_db[datelist[i]].keys():
                        sql_cmd = "replace into Image_Category_Info\
                                (time, CategoryId, ImageNum) values (\'%s\', \'%s\', %s)"\
                                %(datelist[i], categoryId, save_to_db[datelist[i]][categoryId])
                        total_num += save_to_db[datelist[i]][categoryId]
                        logging.info("插入入库的图集数量及其类目:%s %s"%(categoryId, sql_cmd))
                        operatedb.executesql(sql_cmd)
                        sql =  "replace into Image_Flow_Funnel\
                                (time, Stage, ImageNum) values (\'%s\', \'%s\', %s)"\
                                %(datelist[0], '400', total_num)
                        logging.info("插入入库的图集数量:%s %s"%(total_num, sql))
                        operatedb.executesql(sql)
                    save_to_db.pop(datelist[i])
            """
            出队列的图片数量
            """
            if len(dequeue.keys()) >= 2:
                datelist = sorted(dequeue.keys())
                for i in range(0, len(datelist) - 1):
                    sql_cmd = "replace into Image_Flow_Funnel\
                            (time, Stage, ImageNum) values (\'%s\', \'%s\', %s)"\
                            %(datelist[i], '300', dequeue[datelist[i]])
                    logging.info("插入出队列的图集数量%s %s"%(dequeue[datelist[i]], sql_cmd))
                    operatedb.executesql(sql_cmd)
                    dequeue.pop(datelist[i])
            else:
                continue
            for filename in file_record.keys():
                redis_data.set(filename, file_record[filename])
            continue
    operatedb.disconnect()

if __name__ == '__main__':
    main()
