#!/usr/bin/env python
# -*- coding: utf8 -*-
#
"""
image_copyright
"""
import logging
import sys
from contextlib import contextmanager
from common.logger import setup_logging
import time
import datetime
from db_conn import session_cpu_ic
from db_conn import session_evaluting
from evaluting.Imageclusternum import Image_Clusternum
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class Image_cluster(object):
    """
    image database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("Image_cluster")
    
    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now
        
    def get_result(self, now):
        """
        get image numbers by cluster number
        """
        sql = "select count(*) as cluster_num, valid_count from image_cluster_profile\
                where create_time > \'%s\' group by valid_count"%(now)
        print sql
        try:
            with session_cpu_ic() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))
            
    def is_exist(self, now, numrange):
        """
        is_exist
        """
        sql = "select * from Image_Clusternum where \
                numrange = \'%s\' and time = \'%s\'"%(numrange, now)
        try:
            with session_evaluting() as session:
                result = session.execute(sql).fetchall()
                if len(result) != 0:
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.exception("is exist %s"% str(e))
    
    def update_db(self, now, results):
        """
        update db
        """
        if results is None:
            self.logging.warning("result is none No update")
            return
        cluster_number = {'>10':0, '5-10':0}
        update_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        for result in results:
            valid_count = int(result.valid_count)
            cluster_num = result.cluster_num
            if valid_count > 10:
                cluster_number['>10'] += int(result.cluster_num)
            if  valid_count >=5 and valid_count <= 10:
                cluster_number['5-10'] += int(result.cluster_num)
            if valid_count >=0 and valid_count < 5:
                if valid_count not in cluster_number.keys():
                    cluster_number[valid_count] = int(result.cluster_num)
                else:
                    cluster_number[valid_count] += int(result.cluster_num)
        for numrange in cluster_number.keys():
            update_dict = {
            "cluster_num": cluster_number[numrange],
            "time": update_time,
            }
            print update_dict
            new_record = Image_Clusternum(
                numrange = numrange,
                cluster_num = cluster_number[numrange],
                time = update_time
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, numrange):
                        query = session.query(Image_Clusternum)
                        query.filter(Image_Clusternum.numrange == numrange, Image_Clusternum.time == update_time).\
                                update(update_dict)
                    else:
                        session.add(new_record)
            except Exception as e:
                self.logger.exception("update_db error: %s" % str(e))

    def run(self):
        """
        run
        """
        self.logger.info(">>>>>> running Image database")
        self.logger.info(">>>>>> get clusternumber by valid count")
        now = self.get_current_time()
        results = self.get_result(now)
        self.logger.info(">>>>>> update imagenum by copyright")
        self.update_db(now, results)
        self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    image_cluster = Image_cluster()
    image_cluster.run()
