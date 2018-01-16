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
image_info = sqlalchemy.Table("image_info_201707", metadata,
        sqlalchemy.Column('id', mysql.BIGINT, primary_key=True),
        sqlalchemy.Column('cluster_id', mysql.BIGINT),
        sqlalchemy.Column('title', mysql.VARCHAR),
        sqlalchemy.Column('description', mysql.VARCHAR),
        sqlalchemy.Column('source_url', mysql.VARCHAR),
        sqlalchemy.Column('edit_images', mysql.VARCHAR),
        sqlalchemy.Column('source_name', mysql.VARCHAR),
        sqlalchemy.Column('crumb', mysql.VARCHAR),
        sqlalchemy.Column('origin_cate', mysql.VARCHAR),
        sqlalchemy.column('category_id', mysql.BIGINT),
        sqlalchemy.column('has_copyright', mysql.TINYINT),
        sqlalchemy.column('images_count', mysql.TINYINT),
        sqlalchemy.column('status', mysql.TINYINT),
        sqlalchemy.column('off_reason_type', mysql.TINYINT),
        sqlalchemy.column('off_reason_msg', mysql.VARCHAR),
        sqlalchemy.column('bonus_owner_id', mysql.VARCHAR),
        sqlalchemy.column('bonus_owner_type', mysql.TINYINT),
        sqlalchemy.column('delete_flag', mysql.TINYINT),
        sqlalchemy.column('issue_time', mysql.TIMESTAMP),
        sqlalchemy.column('create_time', mysql.TIMESTAMP),
        sqlalchemy.column('update_time', mysql.TIMESTAMP),
        sqlalchemy.column('publish_time', mysql.TIMESTAMP)
        )

class image_info(object):
    """
    image_info
    """
    def __init__(self, 
            id,
            cluster_id,
            title,
            description,
            source_url,
            edit_images,
            source_name,
            crumb,
            origin_cate,
            category_id,
            has_copyright,
            images_count,
            status,
            off_reason_type,
            off_reason_msg,
            bonus_owner_id,
            bonus_owner_type,
            delete_flag,
            issue_time,
            create_time,
            update_time,
            publish_time
            ):
        self.id = id
        self.cluster_id = cluster_id
        self.title = title
        self.description = description
        self.source_url = source_url
        self.edit_images = edit_images
        self.source_name = source_name
        self.crumb = crumb
        self.origin_cate = origin_cate
        self.category_id = category_id
        self.has_copyright = has_copyright
        self.images_count = images_count
        self.status = status
        self.off_reason_type = off_reason_type
        self.off_reason_msg = off_reason_msg
        self.bonus_owner_id = bonus_owner_id
        self.bonus_owner_type = bonus_owner_type
        self.delete_flag = delete_flag
        self.issue_time = issue_time
        self.create_time = create_time
        self.update_time = update_time
        self.publish_time = publish_time
        
    def __str__(self):
        out = [self.id, self.cluster_id, self.title, self.description, self.source_url,\
                self.edit_images, self.source_name, self.crumb, self.origin_cate, self.category_id,\
                self.has_copyright, self.images_count, self.status, self.off_reason_type, self.off_reason_msg,\
                self.bonus_owner_id, self.bonus_owner_type, self.delete_flag, self.issue_time, self.create_time,\
                self.update_time, self.publish_time]
        out = list(map(lambda x: str(x), out))
        out = '\t'.join(out)
        return out

sqlalchemy.orm.mapper(image_info_201707, image_info)
