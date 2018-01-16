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
image_profile = sqlalchemy.Table("image_profile", metadata,
        sqlalchemy.Column('id', mysql.BIGINT, primary_key=True),
        sqlalchemy.Column('image_id', mysql.BIGINT),
        sqlalchemy.Column('quality_feature', mysql.VARCHAR),
        sqlalchemy.Column('quality_level', mysql.VARCHAR),
        sqlalchemy.Column('quality_score', mysql.VARCHAR),
        sqlalchemy.Column('delete_flag', mysql.TINYINT),
        sqlalchemy.Column('create_time', mysql.TIMESTAMP),
        sqlalchemy.Column('update_time', mysql.TIMESTAMP))

class Image_Profile(object):
    """
    image profile table
    """
    def __init__(self,
            id=None,
            image_id=None,
            quality_feature=None,
            quality_level=None,
            quality_score=None,
            delete_flag=None,
            create_time=None,
            update_time=None):
        self.id = id
        self.image_id = image_id
        self.quality_feature = quality_feature
        self.quality_level = quality_level
        self.quality_score = quality_score
        self.delete_flag = delete_flag
        self.create_time = create_time
        self.update_time = update_time
    
    def __str__(self):
        out = [self.id, self.image_id, self.quality_feature, self.quality_level,\
                self.quality_score, self.delete_flag, \
                self.create_time, self.update_time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(Image_Profile, image_profile)        
