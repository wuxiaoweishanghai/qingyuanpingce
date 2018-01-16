#!/usr/bin/env python
# -*- coding: utf8 -*-
# coding: utf-8
"""
table video_info
"""
import sys
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.dialects.mysql as mysql

reload(sys)
sys.setdefaultencoding("utf-8")

metadata = sqlalchemy.MetaData()
video_sourcename = sqlalchemy.Table("Video_Sourcename", metadata,
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key=True),
        sqlalchemy.Column('sourcename', mysql.VARCHAR(10), primary_key=True),
        sqlalchemy.Column('num', mysql.BIGINT(10))
        )

class Video_Sourcename(object):
    """
    image_info
    """
    def __init__(self, 
            time,
            sourcename,
            num):
        self.time = time
        self.sourcename = sourcename
        self.num = num
    
    def __str__(self):
        out = [self.time, self.sourcename, self.num]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Video_Sourcename, video_sourcename)
