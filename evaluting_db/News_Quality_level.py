#!/usr/bin/env python
# -*- coding: utf8 -*-
#
"""
image_cluster
"""
import logging
import sys
from contextlib import contextmanager
from common.logger import setup_logging
import time
import datetime
from db_conn import session_cpu_cc
from db_conn import session_evaluting
from evaluting.Newsquality import News_Quality_level
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class News_quality(object):
    """
    image database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("News_quality")
    
    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now
        
    def get_nonecopyright_quality(self, now):
        """
        get content numbers by quality_level with no copyright 
        """
        sql = "select count(*) as content_num, quality_level from \
                (select news_info.id, news_profile.quality_level \
                from news_info join news_profile on \
                news_info.id = news_profile.news_id where news_info.has_copyright = 0 and \
                news_info.create_time > \'%s\') as b group by quality_level"\
                %(now)
        try:
            with session_cpu_cc() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_nonecopyright_quality %s" % str(e))
            
    def get_quality(self, now):
        """
        get content numbers by quality_level with copyright
        """
        sql = "select count(*) as content_num, quality_level from \
                (select news_info.id, news_profile.quality_level \
                from news_info join news_profile on \
                news_info.id = news_profile.news_id where news_info.has_copyright = 1 and \
                news_info.create_time > \'%s\') as b group by quality_level"\
                %(now)
        try:
            with session_cpu_cc() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_quality %s" % str(e))
            
    def is_exist(self, now, quality_level, copy_right):
        """
        is_exist
        """
        sql = "select * from News_Quality_level where \
              time like \'%s\' and quality_level = %s and copy_right = %s"%(now.split(' ')[0] + '%',\
              quality_level, copy_right)
        try:
            with session_evaluting() as session:
                result = session.execute(sql).fetchall()
                if len(result) != 0:
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.exception("is exist %s"% str(e))
    
    def update_db(self, now, results, copy_right):
        """
        update db
        """
        update_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        if results is None:
            self.logging.warning("result is none No update")
            return
        for result in results:
            count = result.content_num
            quality_level = result.quality_level
            update_dict = {
                           "ImageNum": count,
                           "time": update_time,
                           "quality_level": quality_level
            }
            new_record = News_Quality_level(
                    time = update_time,
                    quality_level = quality_level,
                    ImageNum = count,
                    copy_right = copy_right
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, quality_level, copy_right):
                        query = session.query(News_Quality_level)
                        query.filter(News_Quality_level.time == update_time, News_Quality_level.quality_level == quality_level\
                                , News_Quality_level.copy_right == copy_right).\
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
        self.logger.info(">>>>>> get imagenumber by quality_level")
        results = self.get_nonecopyright_quality(now)
        self.logger.info(">>>>>> update imagenum by quality_level")
        copy_right = 0
        self.update_db(now, results, copy_right)
        copy_right = 1
        results = self.get_quality(now)
        self.update_db(now, results, copy_right)
        self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    news_quality = News_quality()
    news_quality.run()
