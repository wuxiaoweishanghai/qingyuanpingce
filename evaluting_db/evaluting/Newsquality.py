#!/usr/bin/env python
# -*- coding: utf8 -*-
# coding: utf-8
"""
table image_info
"""
import sys
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.dialects.mysql as mysql

reload(sys)
sys.setdefaultencoding("utf-8")

metadata = sqlalchemy.MetaData()
News_quality = sqlalchemy.Table("News_Quality_level", metadata,
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key=True),
        sqlalchemy.Column('quality_level', mysql.VARCHAR(10), primary_key=True),
        sqlalchemy.Column('ImageNum', mysql.BIGINT(10)),
        sqlalchemy.Column('copy_right', mysql.BIGINT(4), primary_key=True),
        )

class News_Quality_level(object):
    """
    image_info
    """
    def __init__(self, 
            time,
            quality_level,
            ImageNum,
            copy_right):
        self.time = time
        self.quality_level = quality_level
        self.ImageNum = ImageNum
        self.copy_right = copy_right
    
    def __str__(self):
        out = [self.time, self.quality_level, self.ImageNum, self.copy_right]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(News_Quality_level, News_quality)
