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
from db_conn import session_cpu_ic
from db_conn import session_evaluting
from evaluting.Imagequalitylevel import Image_Quality_level
reload(sys)
sys.setdefaultencoding("utf-8")
setup_logging()

class Image_quality(object):
    """
    image database
    """
    def __init__(self):
        """
        init
        """
        self.logger = logging.getLogger("Image_quality")
    
    def get_current_time(self):
        """
        get current time
        """
        now = datetime.datetime.now()
        now = str(now.strftime('%Y-%m-%d 00:00:00'))
        return now
        
    def get_nonecopyright_quality(self, now):
        """
        get image numbers by quality
        """
        year = now.split('-')[0]
        month = int(now.split('-')[1])
        if int(month/7) == 0:
            count = '01'
        if int(month/7) == 1:
            count = '07'
        sql = "select count(*) as image_num, quality_level from \
                (select image_info_%s%s.id, image_info_%s%s.has_copyright, \
                image_profile.quality_level from image_info_%s%s join image_profile \
                on image_info_%s%s.id = image_profile.image_id where image_info_%s%s.create_time like \'%s\') \
                as b where has_copyright = 0 group by quality_level"\
                %(year, count, year, count, year, count, year, count, year, count, now.split(' ')[0] + '%')
        print sql
        try:
            with session_cpu_ic() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_nonecopyright_quality %s" % str(e))
            
    def get_quality(self, now):
        """
        get iamge numbers by copyright 
        """
        year = now.split('-')[0]
        month = int(now.split('-')[1])
        if int(month/7) == 0:
            count = '01'
        if int(month/7) == 1:
            count = '07'
        sql = "select count(*) as image_num, quality_level from \
                (select image_info_%s%s.id, image_info_%s%s.has_copyright, \
                image_profile.quality_level from image_info_%s%s join \
                image_profile on image_info_%s%s.id = image_profile.image_id \
                where image_info_%s%s.create_time like \'%s\') \
                as b where has_copyright = 1 group by quality_level"\
                %(year, count, year, count, year, count, year, count, year, count, now.split(' ')[0] + '%')
        print sql
        try:
            with session_cpu_ic() as session:
                results = session.execute(sql).fetchall()
                if results is not None:
                    return results
        except Exception as e:
            self.logger.exception("get_quality %s" % str(e))
            
    def is_exist(self, now, quality_level, copy_right):
        """
        is_exist
        """
        sql = "select * from Image_Quality_level where \
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
            count = result.image_num
            quality_level = result.quality_level
            update_dict = {
                           "imagenum": count,
                           "time": update_time,
                           "quality_level": quality_level
            }
            print update_dict
            new_record = Image_Quality_level(
                    time = update_time,
                    quality_level = quality_level,
                    imagenum = count,
                    copy_right = copy_right
                    )
            try:
                with session_evaluting() as session:
                    if self.is_exist(now, quality_level, copy_right):
                        query = session.query(Image_Quality_level)
                        query.filter(Image_Quality_level.time == update_time, Image_Quality_level.quality_level == quality_level\
                                , Image_Quality_level.copy_right == copy_right).\
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
    image_quality = Image_quality()
    image_quality.run()
