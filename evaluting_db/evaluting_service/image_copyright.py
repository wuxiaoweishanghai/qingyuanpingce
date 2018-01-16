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
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class Image_copyright(object):
    """
    image database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("Image_copyright")
    
    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now
        
    def get_result(self, now):
        """
        get image numbers by copyright
        """
        year = now.split('-')[0]
        month = int(now.split('-')[1])
        month = '0' + str(int(month/6) + 1)
        sql = "select count(*) AS image_num, has_copyright from image_info_%s%s\
                group by has_copyright where create_time like \'%s\'"\
                %(year, month, now.split(' ')[0] + '%')
        try:
            with session_cpu_ic() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))
            
    def is_exist(self, now):
        """
        is_exist
        """
        sql = "select * from image_copyright where \
              time like \'%s\'"%(now)
        try:
            with session_evaluting() as session:
                result = session.execute(sql).fetchall()
                if result is not None:
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.exception("is exist %s"% str(e))
    
    def update_db(self, now):
        """
        update db
        """
        if results is None:
            self.logging.warning("result is none No update")
            return
        for result in results:
            count = result.image_num
            has_copyright = result.has_copyright
            update_dict = {
                           "count": count,
                           "has_copyright": has_copyright,
                           "time": now
            }
            new_record = Image_CopyRight(
                    time = now,
                    copyright = has_copyright,
                    count = count
                    )
            try:
                with session_evaluting() as session:
                    if self.if_exist(now):
                        query = session.query(Image_CopyRight)
                        query.filter(Image_CopyRight).update(update_dict)
                    else:
                        query.add(new_record)
            except Exception as e:
                self.logger.exception("update_db error: %s" % str(e))

    def run(self):
        """
        run
        """
        self.logger.info(">>>>>> running Image database")
        self.logger.info(">>>>>> get current date")
        now = get_current_time()
        self.logger.info(">>>>>> get imagenumber by copyright")
        result = get_result(now)
        self.logger.info(">>>>>> update imagenum by copyright")
        update_db(now)
        self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    image_copyright = Image_copyright()
    image_copyright.run()
