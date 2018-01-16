#coding:utf-8
import os
import sys
import logging
import random
import json
import MySQLdb
import re
import time
reload(sys)
sys.setdefaultencoding('utf8')

def get_news_id(cursor):
    """
    get news id from mysql
    """
    sql_cmd = "select id from news_info_201710 where id >= (select floor( rand() \
            * ((select max(id) from news_info_201710)-(select min(id) \
            from news_info_201710)) + (select min(id) from news_info_201710))) \
            order by id limit 2000;"
    print sql_cmd
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    return results

def generate_id(file, results):
    """
    generate news id
    """
    news = {"id":[]}
    info_list = []
    for result in results:
        info_list.append(int(result[0]))
    news['id']=info_list
    file.write((json.dumps(news)).replace(" ",""))
    file.write(";")

def main():
    """
    main
    """
    try:
        conn = MySQLdb.connect(host = '10.58.115.18', \
                port = 6535, user = '_root', passwd \
                = 'cnN4HBH98lublJXMf5hPEp48', db = 'cpu_cc', charset='utf8')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database")
    cursor = conn.cursor()
    file = "./getnewsinfos.json"
    try:
        file = open(file, 'w')
    except BaseException, e:
        print "failed to open file %s"%(e)
    for j in range(0,10000):
        results = get_news_id(cursor)
        generate_id(file, results)
    file.close()

if __name__ == '__main__':
    main()
        
    
    

    
