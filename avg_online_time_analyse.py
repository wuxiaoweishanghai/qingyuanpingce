#!/usr/bin/env python
#-*- coding: utf-8 -*-
from operatedb import OperateDB
from datetime import datetime,timedelta
import logging
import time
import MySQLdb

logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='avg_online_time.log',
        filemode='w')

def get_news_avgonline_time(now):
    """
    get news avg online time from database
    """
    try:
        conn = MySQLdb.connect(host = '10.26.188.23', \
                port = 5100, user = 'wuxiaowei01', passwd \
                = '03hQkG62xq', db = 'cpu_cc')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database %s"%(e)) 
    year = now.split('-')[0]
    month = int(now.split('-')[1])
    if int(month/7) == 0:
        count = '07'
    if int(month/10) == 1:
        count = '10'
    sql_cmd = "select issue_time,create_time from news_info_%s%s where create_time > \'%s\'"%(year, count, now)
    print sql_cmd
    cursor = conn.cursor()
    cursor.execute(sql_cmd)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_image_avgonline_time(now):
    """
    get image avg online time from database
    """
    try:
        conn = MySQLdb.connect(host = '10.26.188.23', \
                port = 5100, user = 'wuxiaowei01', passwd \
                = '03hQkG62xq', db = 'cpu_ic')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database %s"%(e))
    year = now.split('-')[0]
    month = int(now.split('-')[1])
    if int(month/7) == 0:
        count = '01'
    if int(month/7) == 1:
        count = '07'
    sql_cmd = "select issue_time,create_time from image_info_%s%s where create_time > \'%s\'"%(year, count, now)
    print sql_cmd
    cursor = conn.cursor()
    cursor.execute(sql_cmd)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_video_avgonline_time(now):
    """
    get video avg online time from database
    """
    try:
        conn = MySQLdb.connect(host = '10.26.188.23', \
                port = 5100, user = 'wuxiaowei01', passwd \
                = '03hQkG62xq', db = 'cpu_vc')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database %s"%(e))
    now_time = time.mktime(time.strptime(now, '%Y-%m-%d %H:00:00'))
    sql_cmd = "select source_create_time,check_in_time from video_info where check_in_time > \'%s\'"%(now_time)
    print sql_cmd
    cursor = conn.cursor()
    cursor.execute(sql_cmd)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
    
def update_content(now, timecost, operatedb, content_type):
    """
    update some contents
    """
    for key in timecost:
        sql_cmd = "replace into avg_contentcreate_time (time, content_type, timezone, content_num) \
                values (\'%s\', \'%s\', \'%s\', \'%s\')"%(now, content_type, key, timecost[key])
        print sql_cmd
        operatedb.executesql(sql_cmd)
   
def calucate(results):
    list = []
    timecost = {'<10min':0,'10min-30min':0,'30min-60min':0,'1Hour-24Hour':0,'>24Hour':0}
    for result in results:
        avg_time = result[1] - result[0]
        list.append(avg_time)
    timesday = timedelta(days=1)
    timetenminu = timedelta(minutes = 10)
    timethirtyminu = timedelta(minutes = 30)
    timesixtyminu = timedelta(minutes = 60)
    for i in range(0, len(list)):
        if list[i] <= timetenminu:
            timecost['<10min'] += 1
        elif list[i] <= timethirtyminu:
            timecost['10min-30min'] += 1
        elif list[i] <= timesixtyminu:
            timecost['30min-60min'] += 1
        elif list[i] < timesday:
            timecost['1Hour-24Hour'] += 1
        elif list[i] > timesday:
            timecost['>24Hour'] += 1
    return timecost

def calucate_int(results):
    list = []
    timecost = {'<10min':0,'10min-30min':0,'30min-60min':0,'1Hour-24Hour':0,'>24Hour':0}
    for result in results:
        avg_time = result[1] - result[0]
        list.append(avg_time)
    timesday = timedelta(days=1).seconds
    timetenminu = timedelta(minutes = 10).seconds
    timethirtyminu = timedelta(minutes = 30).seconds
    timesixtyminu = timedelta(minutes = 60).seconds
    for i in range(0, len(list)):
        if list[i] <= timetenminu:
            timecost['<10min'] += 1
        elif list[i] <= timethirtyminu:
            timecost['10min-30min'] += 1
        elif list[i] <= timesixtyminu:
            timecost['30min-60min'] += 1
        elif list[i] < timesday:
            timecost['1Hour-24Hour'] += 1
        elif list[i] > timesday:
            timecost['>24Hour'] += 1
    return timecost

def main():
    """
    main
    """
    now = datetime.now()
    now = str(now.strftime('%Y-%m-%d %H:00:00'))
    operatedb = OperateDB("./mysql.conf")
    operatedb.connect()
    content_type = 'news'
    results = get_news_avgonline_time(now)
    timecost = calucate(results)
    update_content(now, timecost, operatedb, content_type)
    content_type = 'image'
    results = get_image_avgonline_time(now)
    timecost = calucate(results)
    update_content(now, timecost, operatedb, content_type)
    content_type = 'video'
    results = get_video_avgonline_time(now)
    timecost = calucate_int(results)
    update_content(now, timecost, operatedb, content_type)

if __name__ == '__main__':
    main() 
