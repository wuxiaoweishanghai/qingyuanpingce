#!/usr/bin/env python
# -*- coding: utf8 -*-
#
"""
video_copyright
"""
import logging
import sys
from contextlib import contextmanager
from common.logger import setup_logging
import time
import datetime
from db_conn import session_cpu_vc
from db_conn import session_evaluting
from evaluting.VideoCategory import Video_Category_Info
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class Video_category(object):
    """
    video database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("Video_Category")
    
    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now
        
    def get_result(self, now):
        """
        get category by content numbers
        """
        sql = "select count(*) as content_num, category_id as categoryId from video_info\
                where check_in_time >=unix_timestamp(\'%s\') and review_status = 3 and category_id != 0 \
                group by categoryId"%(now)
        print sql
        try:
            with session_cpu_vc() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))

    def is_exist(self, now, categoryId):
        """
        is_exist
        """
        sql = "select * from Video_Category_Info where \
                categoryId = \'%s\' and time = \'%s\'"%(categoryId, now)
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
        update_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        for result in results:
            ImageNum = int(result.content_num)
            categoryId = result.categoryId
            update_dict = {
            "ImageNum": ImageNum,
            "time": update_time,
            }
            new_record = Video_Category_Info(
                categoryId = categoryId,
                ImageNum = ImageNum,
                time = update_time
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, categoryId):
                        query = session.query(Video_Category_Info)
                        query.filter(Video_Category_Info.categoryId == categoryId, Video_Category_Info.time == update_time).\
                                update(update_dict)
                    else:
                        session.add(new_record)
            except Exception as e:
                self.logger.exception("update_db error: %s" % str(e))

    def run(self):
        """
        run
        """
        self.logger.info(">>>>>> running News database")
        self.logger.info(">>>>>> get categoryId by content number")
        now = self.get_current_time()
        results = self.get_result(now)
        self.logger.info(">>>>>> update content number by categoryId")
        self.update_db(now, results)
        self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    video_category = Video_category()
    video_category.run()
