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
from db_conn import session_cpu_cc
from db_conn import session_evaluting
from evaluting.NewsSourcename import News_Sourcename
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()


class News_sourcename(object):
    """
    News source name
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
        get news number by source name
        """
        sql = "select content_num, source_name from (select count(*) as \
                content_num, source_name from news_info_201710\
                where create_time > \'%s\' and status =3 group by source_name) as b order \
                by content_num desc limit 100"\
                %(now)
        print sql
        try:
            with session_cpu_cc() as session: 
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))
    
    def is_exist(self, now, sourcename):
        """
        is_exist
        """
        sql = "select * from News_Sourcename where \
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
            count = result.content_num
            sourcename = result.source_name.encode("utf-8")
            update_dict = {
                           "num": count,
                           "time": now
            }
            new_record = News_Sourcename(
                    time = now,
                    sourcename = sourcename.encode("utf-8"),
                    num = count
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, sourcename):
                        query = session.query(News_Sourcename)
                        query.filter(News_Sourcename.time == now, News_Sourcename.sourcename == sourcename.encode("utf-8")).\
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
    news_sourcename = News_sourcename()
    news_sourcename.run()
