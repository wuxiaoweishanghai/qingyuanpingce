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
Video_cluster = sqlalchemy.Table("Video_Clusternum", metadata,
        sqlalchemy.Column('numrange', mysql.VARCHAR(6), primary_key = True),
        sqlalchemy.Column('cluster_num', mysql.BIGINT(10)),
        sqlalchemy.Column('time', mysql.TIMESTAMP, primary_key = True)
        )

class Video_Clusternum(object):
    """
    video_info
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

sqlalchemy.orm.mapper(Video_Clusternum, Video_cluster)
