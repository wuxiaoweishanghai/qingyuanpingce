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
from db_conn import session_cpu_cc
from db_conn import session_evaluting
from evaluting.NewsOfflinereason import News_Offline_Reason
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class News_offlinereason(object):
    """
    image database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("News_Offline_reason")
    
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
        sql = "select count(*) as content_num, off_reason_type from news_info_201710\
                where create_time > \'%s\' and status = 6 group by off_reason_type"%(now)
        print sql
        try:
            with session_cpu_cc() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_results %s" % str(e))

    def is_exist(self, now, OfflineReason):
        """
        is_exist
        """
        sql = "select * from News_Offline_Info where \
                OfflineReason = \'%s\' and time = \'%s\'"%(OfflineReason, now)
        try:
            with session_evaluting() as session:
                result = session.execute(sql).fetchall()
                if len(result) != 0:
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.exception("is exist %s"% str(e))

    #def is_existforbidden(self, now):
    #    """
    #    contains forbidden words exists
    #    """
    #    OfflineReason = "内容或标题含有违禁词"
    #    sql = "select * from News_Offline_Info where \
    #           OfflineReason = \'%s\' and time = \'%s\'"%(OfflineReason, now)
    #    try:
    #        with session_evaluting() as session:
    #            result = session.execute(sql).fetchall()
    #            if len(result) != 0:
    #                return True
    #            else:
    #                return False
    #    except Exception as e:
    #        self.logger.exception("is exist %s"% str(e))
        
    def update_db(self, now, results):
        """
        update db
        """
        if results is None:
            self.logging.warning("result is none No update")
            return
        update_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        update_containforbidden = {
           "ImageNum": 0,
           "time": update_time
        }
        #otherreason_results = []
        for result in results:
            OfflineReason = result.off_reason_type
        #    reason = '内容或标题含有违禁词'
        #    if reason in OfflineReason:
        #        update_containforbidden['ImageNum'] += result.content_num
        #    else:
        #        otherreason_results.append(result)
        #        continue
        #for result in otherreason_results:
            ImageNum = result.content_num
            #OfflineReason = result.off_reason_msg.encode("utf-8")
            update_dict = {
            "ImageNum": ImageNum,
            "time": update_time,
            }
            new_record = News_Offline_Reason(
                OfflineReason = OfflineReason,
                ImageNum = ImageNum,
                time = update_time
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, OfflineReason):
                        query = session.query(News_Offline_Reason)
                        query.filter(News_Offline_Reason.OfflineReason == OfflineReason, News_Offline_Reason.time == update_time).\
                                update(update_dict)
                    else:
                        session.add(new_record)
            except Exception as e:
                self.logger.exception("update_db error: %s" % str(e))
            #new_record = News_Offline_Reason(
            #        OfflineReason = '内容或标题含有违禁词',
            #        ImageNum = update_containforbidden['ImageNum'],
            #        time = update_time
            #        )
            #try:
            #    with session_evaluting() as session:
            #        if self.is_existforbidden(now):
            #            query = session.query(News_Offline_Reason)
            #            contains_forbidden = '内容或标题含有违禁词'
            #            query.filter(News_Offline_Reason.OfflineReason == contains_forbidden, News_Offline_Reason.time == update_time).\
            #                    update(update_containforbidden)
            #        else:
            #            session.add(new_record)
            #except Exception as e:
            #    self.logger.exception("update_db error: %s" % str(e))

    def run(self):
        """
        run
        """
        self.logger.info(">>>>>> running News database")
        self.logger.info(">>>>>> get offline_reason by content number")
        now = self.get_current_time()
        results = self.get_result(now)
        self.logger.info(">>>>>> update content number by offline_reason")
        self.update_db(now, results)
        self.logger.info(">>>>>> all Done")

if __name__ == '__main__':
    news_offline_reason = News_offlinereason()
    news_offline_reason.run()
