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
News_offlinereason = sqlalchemy.Table("News_Offline_Info", metadata,
        sqlalchemy.Column('OfflineReason', mysql.VARCHAR(10), primary_key = True),
        sqlalchemy.Column('ImageNum', mysql.BIGINT(10)),
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key = True)
        )

class News_Offline_Reason(object):
    """
    image_info
    """
    def __init__(self, 
            OfflineReason,
            ImageNum,
            time):
        self.OfflineReason = OfflineReason
        self.ImageNum = ImageNum
        self.time = time
    
    def __str__(self):
        out = [self.OfflineReason, self.ImageNum, self.time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(News_Offline_Reason, News_offlinereason)
