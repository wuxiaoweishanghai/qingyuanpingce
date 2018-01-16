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
Image_Copyright = sqlalchemy.Table("Image_Copyright", metadata,
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key=True),
        sqlalchemy.Column('copyright', mysql.BIGINT(4), primary_key=True),
        sqlalchemy.Column('imagenum', mysql.BIGINT(10))
        )

class Image_CopyRight(object):
    """
    image_info
    """
    def __init__(self, 
            time,
            copyright,
            imagenum):
        self.time = time
        self.copyright = copyright
        self.imagenum = imagenum
    
    def __str__(self):
        out = [self.time, self.copyright, self.imagenum]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Image_CopyRight, Image_Copyright)
