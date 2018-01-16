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
news_flowfunnel = sqlalchemy.Table("News_Flow_Funnel", metadata,
        sqlalchemy.Column('time', mysql.VARCHAR(100), primary_key=True),
        sqlalchemy.Column('Stage', mysql.BIGINT(4), primary_key=True),
        sqlalchemy.Column('ImageNum', mysql.BIGINT(10))
        )

class News_Flow_Funnel(object):
    """
    news_flow_funnel
    """
    def __init__(self, 
            time,
            Stage,
            ImageNum):
        self.time = time
        self.Stage = Stage
        self.ImageNum = ImageNum
    
    def __str__(self):
        out = [self.time, self.Stage, self.ImageNum]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(News_Flow_Funnel, news_flowfunnel)
