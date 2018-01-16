#!/usr/bin/env python
# -*- coding: utf8 -*-
#
"""
news_work_flow
"""
import logging
import sys
from contextlib import contextmanager
from common.logger import setup_logging
import time
import datetime
from db_conn import session_cpu_cc
from db_conn import session_evaluting
from evaluting.Newsworkflow import News_Flow_Funnel
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()


class News_flow_funnel(object):
    """
    News flow funnel
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("News_flow_funnel")

    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now

    def get_result(self, now):
        """
        get news number by online
        """
        sql = "select count(*) as \
                newsnum from news_info\
                where create_time > \'%s\' and status =3"\
                %(now)
        print sql
        try:
            with session_cpu_cc() as session: 
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))
    
    def is_exist(self, now):
        """
        is_exist
        """
        print now
        sql = "select * from News_Flow_Funnel where \
                time = \'%s\' and Stage = 500"%(now)
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
            count = result.newsnum
            update_dict = {
                           "ImageNum": count,
                           "time": now,
                           "Stage": "500"
            }
            new_record = News_Flow_Funnel(
                    time = now,
                    ImageNum = count,
                    Stage = '500'
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now):
                        query = session.query(News_Flow_Funnel)
                        query.filter(News_Flow_Funnel.time == now, News_Flow_Funnel.Stage == '500').\
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
    news_flow_funnel = News_flow_funnel()
    news_flow_funnel.run()
