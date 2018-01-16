import MySQLdb
import datetime
import time
import logging
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='category_handle.log',
                filemode='w')

def get_categery_number(now, cursor):
    category_number = {}
    year = now.split('-')[0]
    month = int(now.split('-')[1])
    if int(month/7) == 0:
        count = '01'
    if int(month/7) == 1:
        count = '07'
    print count
    sql_cmd="select category_id,count(*) \
                from image_info_%s%s where status = 3 \
                and create_time like \'%s\' group by category_id"\
                %(year, count, now.split(' ')[0] + '%')
    print sql_cmd
    logging.info("select image number by categoryid %s"%(sql_cmd))
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    for result in results:
        category_number[result[0]] = result[1]
    return category_number

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
    #now = str(now.strftime('2017-04-14 00:00:00'))
    category_number = get_categery_number(now, cursor)
    cursor.close()
    try:
        conn = MySQLdb.connect(host = '10.119.25.50', \
                port = 3306, user = 'cpuqa', passwd \
                = 'MhxzKhl', db = 'evaluating')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database")
    cursor = conn.cursor()
    for category in category_number.keys():
        sql_cmd = "replace into Image_Category_Info (time, categoryId, ImageNum) \
                values (\'%s\', \'%s\', \'%s\')"\
                %(now, category, category_number[category])
        print sql_cmd
        cursor.execute(sql_cmd)
    cursor.close()

if __name__ == '__main__':
    main()
