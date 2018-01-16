#!/usr/bin/env python
# -*- coding: utf8 -*-
# coding: utf-8
"""
table image_profile
"""
import sys
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import sqlalchemy.dialects.mysql as mysql

reload(sys)
sys.setdefaultencoding("utf-8")

metadata = sqlalchemy.MetaData()
image_cluster_profile = sqlalchemy.Table("image_cluster_profile", metadata,
        sqlalchemy.Column('id', mysql.BIGINT, primary_key=True),
        sqlalchemy.Column('cluster_id', mysql.BIGINT),
        sqlalchemy.Column('category_id', mysql.BIGINT),
        sqlalchemy.Column('tags', mysql.VARCHAR),
        sqlalchemy.Column('quality_feature', mysql.VARCHAR),
        sqlalchemy.Column('quality_level', mysql.TINYINT),
        sqlalchemy.Column('quality_score', mysql.DECIMAL),
        sqlalchemy.Column('image_info_ids', mysql.VARCHAR),
        sqlalchemy.Column('valid_count', mysql.INT),
        sqlalchemy.Column('delete_flag', mysql.TINYINT),
        sqlalchemy.Column('create_time', mysql.TIMESTAMP),
        sqlalchemy.Column('update_time', mysql.TIMESTAMP))

class Image_Cluster_Profile(object):
    """
    image profile table
    """
    def __init__(self,
            id=None,
            cluster_id=None,
            category_id =None,
            tags = None,
            quality_feature=None,
            quality_level=None,
            quality_score=None,
            image_info_ids =None,
            valid_count=None,
            delete_flag=None,
            create_time=None,
            update_time=None):
        self.id = id
        self.cluster_id = cluster_id
        self.category_id = category_id
        self.tags = tags
        self.quality_feature = quality_feature
        self.quality_level = quality_level
        self.quality_score = quality_score
        self.image_info_ids = image_info_ids
        self.valid_count = valid_count
        self.delete_flag = delete_flag
        self.create_time = create_time
        self.update_time = update_time

    def __str__(self):
        out = [self.id, self.cluster_id, self.category_id, self.tags,\
                self.quality_feature, self.quality_level, self.quality_score,\
                self.image_info_ids, self.valid_count, self.delete_flag,\
                self.create_time, self.update_time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Image_Cluster_Profile, image_cluster_profile)
