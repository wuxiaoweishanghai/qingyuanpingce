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
Image_cluster = sqlalchemy.Table("Image_Clusternum", metadata,
        sqlalchemy.Column('numrange', mysql.VARCHAR(6), primary_key = True),
        sqlalchemy.Column('cluster_num', mysql.BIGINT(10)),
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key = True)
        )

class Image_Clusternum(object):
    """
    image_info
    """
    def __init__(self, 
            numrange,
            cluster_num,
            time):
        self.numrange = numrange
        self.cluster_num = cluster_num
        self.time = time
    
    def __str__(self):
        out = [self.numrange, self.cluster_num, self.time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Image_Clusternum, Image_cluster)
