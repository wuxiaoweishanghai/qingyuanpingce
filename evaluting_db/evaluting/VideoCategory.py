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
Video_Category = sqlalchemy.Table("Video_Category_Info", metadata,
        sqlalchemy.Column('categoryId', mysql.BIGINT(10), primary_key = True),
        sqlalchemy.Column('ImageNum', mysql.BIGINT(10)),
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key = True)
        )

class Video_Category_Info(object):
    """
    image_info
    """
    def __init__(self, 
            categoryId,
            ImageNum,
            time):
        self.categoryId = categoryId
        self.ImageNum = ImageNum
        self.time = time
    
    def __str__(self):
        out = [self.categoryId, self.ImageNum, self.time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Video_Category_Info, Video_Category)
