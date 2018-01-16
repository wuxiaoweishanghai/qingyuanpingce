import MySQLdb
import datetime
import time
import logging
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='offline_analyse.log',
                filemode='w')

def get_offlinereason_number(now, cursor):
    offline_reason = {}
    year = now.split('-')[0]
    month = int(now.split('-')[1])
    if int(month/7) == 0:
        count = '01'
    if int(month/7) == 1:
        count = '07'
    print count
    sql_cmd="select off_reason_type,count(*) \
                from image_info_%s%s where create_time like \'%s\' \
                and status = 6 group by off_reason_type"\
                %(year, count, now.split(' ')[0] + '%')
    print sql_cmd
    logging.info("select image number by off_reason_type %s"%(sql_cmd))
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    for result in results:
        offline_reason[result[0]] = result[1]
    return offline_reason

def main():
    try:
        conn = MySQLdb.connect(host = '10.26.188.23', \
                port = 5100, user = 'wuxiaowei01', passwd \
                = '03hQkG62xq', db = 'cpu_ic')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database")
    cursor = conn.cursor()
    now = datetime.datetime.now()
    now = str(now.strftime('%Y-%m-%d 00:00:00'))
    offline_reason = get_offlinereason_number(now, cursor)
    print offline_reason
    cursor.close()
    try:
        conn = MySQLdb.connect(host = '10.119.25.50', \
                port = 3306, user = 'cpuqa', passwd \
                = 'MhxzKhl', db = 'evaluating')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database")
    cursor = conn.cursor()
    for reason in offline_reason.keys():
        print reason
        sql_cmd = "replace into Image_Offline_Info (time, OfflineReason, ImageNum) \
                values (\'%s\', \'%s\', \'%s\')"%(now, reason, offline_reason[reason])
        print sql_cmd
        cursor.execute(sql_cmd)
    cursor.close()

if __name__ == '__main__':
    main()
