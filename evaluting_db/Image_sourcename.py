#!/usr/bin/env python
# -*- coding: utf8 -*-
#
"""
image_sourcename
"""
import logging
import sys
from contextlib import contextmanager
from common.logger import setup_logging
import time
import datetime
from db_conn import session_cpu_ic
from db_conn import session_evaluting
from evaluting.ImageSourcename import Image_Sourcename
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()


class Image_sourcename(object):
    """
    Image source name
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("Image_sourcename")

    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now

    def get_result(self, now):
        """
        get image number by source name
        """
        year = now.split('-')[0]
        month = int(now.split('-')[1])
        if int(month/7) == 0:
            count = '01'
        if int(month/7) == 1:
            count = '07'
        sql = "select imagenum, source_name from (select count(*) as \
                imagenum, source_name from image_info_%s%s\
                where create_time > \'%s\' and status =3 group by source_name) as image_num order \
                by imagenum desc limit 100"\
                %(year, count ,now)
        print sql
        #sql = "select imagenum, source_name from (select count(*) as \
        #        imagenum, source_name from image_info_%s%s\
        #        where create_time between \'2017-05-13 00:00:00\' and \'2017-05-14 00:00:00\'\
        #        and status =3 group by source_name) as image_num order \
        #        by imagenum desc limit 100"\
        #        %(year, month)
        #print sql
        try:
            with session_cpu_ic() as session: 
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))
    
    def is_exist(self, now, sourcename):
        """
        is_exist
        """
        sql = "select * from Image_Sourcename where \
                time like \'%s\' and sourcename = \'%s\'"%(now.split(' ')[0] + '%',\
                sourcename.encode('utf-8'))
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
        for result in results:
            count = result.imagenum
            sourcename = result.source_name.encode("utf-8")
            update_dict = {
                           "num": count,
                           "time": now
            }
            new_record = Image_Sourcename(
                    time = now,
                    sourcename = sourcename.encode("utf-8"),
                    num = count
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, sourcename):
                        query = session.query(Image_Sourcename)
                        query.filter(Image_Sourcename.time == now, Image_Sourcename.sourcename == sourcename.encode("utf-8")).\
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
         self.logger.info(">>>>>> get current date")
         now = self.get_current_time()
         self.logger.info(">>>>>> get imagenumber by sourcename")
         results = self.get_result(now)
         self.logger.info(">>>>>> update imagenum by sourcename")
         self.update_db(now, results)
         self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    Image_sourcename = Image_sourcename()
    Image_sourcename.run()
