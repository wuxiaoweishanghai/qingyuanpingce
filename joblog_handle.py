#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import json
import sys
import logging
import time
import commands
from mq_handle import *
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
                filename='joblog_handle.log',
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
                flow_funnel = get_job_offline(line)
                count = count + 1
                line = fp.readline()
        else:
            while index != 0:
                line = fp.readline()
                index = index - 1
                count = count + 1
            while len(line) != 0:
                flow_funnel = get_job_offline(line)
                count = count + 1
                line = fp.readline()
    fp.close()
    file_record[filename] = count
    return flow_funnel
#def get_file_list(rootdir):
#    """
#    获取文件夹目录
#    返回更新的文件列表
#
#    """
#    filelist = []
#    updatefilelist = []
#    for root, dir, filenames in os.walk(rootdir):
#       for filename in filenames:
#            filelist.append(os.path.join(rootdir, filename))
#    filelist = sorted(filelist)
#    for i in range(len(filelist)):
#        cmd = "wc -l %s"%(filelist[i])
#        output = commands.getoutput(cmd)
#        count = int(output.split(' ')[0])
#        filename = output.split(' ')[1]
#        if filename in file_record.keys():
#            if count != file_record[filename]:
#                updatefilelist.append(filename)
#            else:
#                continue
#        else:
#            updatefilelist.append(filename)
#    return updatefilelist

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

def get_job_offline(line):
    """
    筛选上下架成功的数据
    """
    global flow_funnel
    pattern = re.compile('.*imageSetId=.*result=.*')
    result = pattern.match(line)
    if (result != None):
        result = result.group()
        date = handle_time(result)
        result = result.split(' - ')
        result = result[1].split(', ')
        final_result = result[1].split('=')[1]
        if date not in flow_funnel.keys():
            flow_funnel[date] = {}
            if final_result not in flow_funnel[date].keys():
                flow_funnel[date][final_result] = 1
            else:
                flow_funnel[date][final_result] += 1
        else:
            if final_result not in flow_funnel[date].keys():
                flow_funnel[date][final_result] = 1
            else:
                flow_funnel[date][final_result] += 1
    return flow_funnel

def main():
    """
    任务调度
    5分钟采集一次数据

    """
    global flow_funnel
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    while True:
        time.sleep(10)
        filename = '../cpu-publish-image-job.log'
        flow_funnel = handle_file(filename)
        if len(flow_funnel.keys()) >= 2:
            datelist = sorted(flow_funnel.keys())
            for i in range(0, len(datelist) - 1):
                for result in flow_funnel[datelist[i]].keys():
                    if result == 'pass':
                        sql_cmd = "replace into Image_Flow_Funnel (time, Stage, ImageNum) values ('%s', '%s', %s)" \
                                %(datelist[i], '500', flow_funnel[datelist[i]][result])
                        logging.info('插入上架成功的图集信息%s'%(sql_cmd))
                        operatedb.executesql(sql_cmd)
                    else:
                        sql_cmd = "replace into Image_Offline_Info (time, OfflineReason, ImageNum) values (\'%s\', \'%s\', %s)"\
                        %(datelist[i], result, flow_funnel[datelist[i]][result])
                        logging.info('插入下架的图集信息%s'%(sql_cmd))
                        operatedb.executesql(sql_cmd)
                del flow_funnel[datelist[i]]
        else:
            continue
    operatedb.disconnect()

if __name__ == '__main__':
    main()
