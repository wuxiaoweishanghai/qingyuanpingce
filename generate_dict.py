#coding:utf-8
import os
import sys 
import logging
import random
import json
import MySQLdb
import re
reload(sys)
sys.setdefaultencoding('utf8')

def get_content_info(cursor):
    """
    from mysql get content info
    """
    sql_cmd = "select id,title,content,source_url,source_name,source_images,edit_images,\
            update_time,create_time,owner_id,owner_type,quality_level,cluster_no,status,\
            category_id from news_info where create_time > \"2017-07-12 12:00:00\""
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    return results
    
def get_tag_info(cursor):
    """
    from mysql get tag info
    """
    sql_cmd = "select id from tag_info where create_time > \"2017-07-12 12:00:00\""
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    return results

def get_quality_feature(cursor):
    """
    get quality feature from mysql
    """
    sql_cmd = "select news_profile.quality_feature, news_profile.quality_score, news_info.id, news_profile.seg_words from news_profile,news_info\
            where news_info.id = news_profile.news_id and news_info.create_time > \"2017-07-12 12:00:00\""
    cursor.execute(sql_cmd)
    try:
        results = cursor.fetchall()
    except BaseException, e:
        logging.warning("failed to execute sql %s"%(e))
    return results

def generate_content_info(contents, tags, quality_features):
    """
    generate content info
    """
    file = "./auto_store.json"
    try:
        filewrite = open(file,'w')
    except BaseException, e:
        print "read query file failed %s"%(e)
    for content in contents:
        content_info = {"info":{"title":"","content":"","sourceUrl":"","provider":"","issueTime":"","createTime":"","leafCategoryId":0,\
                "ownerId":0,"ownerType":0,"hasCopyright":0,"sourceImages":[],\
                "images":[],"clusterNo":0,"status":0,"tagInfo":[],"newsProfile":{"qualityFeature":"",\
                "qualityLevel":0,"qualityScore":0}}}
        content_info['info']['title'] = (str(content[1])).decode('utf-8').encode('utf-8')
        content_detail = (str(content[2])).decode('utf-8').encode('utf-8')
        content_detail = content_detail.replace('"',"'")
        content_info['info']['content'] = content_detail
        content_info['info']['provider'] =(str(content[4])).decode('utf-8').encode('utf-8')
        source_images = []
        edit_images = []
        try:
            sourceimages = eval(content[5])['url']
        except BaseException, e:
            print "dict change error %s"%(e)
            continue
        for source_image in sourceimages:
            source_images.append(source_image)
        content_info['info']['sourceImages'] = source_images
        try:
            editimages = eval(content[6])['url']
        except BaseException, e:
            print "dict change error %s"%(e)
            continue
        for edit_image in editimages:
            edit_images.append(edit_image)
        content_info['info']['images'] = edit_images
        content_info['info']['sourceUrl'] = str(content[3])
        content_info['info']['issueTime'] = str(content[7])
        content_info['info']['createTime'] = str(content[8])
        content_info['info']['ownerId'] = str(content[9])
        content_info['info']['hasCopyright'] = random.randint(0,1)
        content_info['info']['leafCategoryId'] = int(content[14])
        content_info['info']['newsProfile']['qualityLevel'] = int(content[11])
        content_info['info']['clusterNo'] = int(content[12])
        content_info['info']['status'] = int(content[13])
        for i in range(0,random.randint(5,10)):
            j = random.randint(0,len(tags)-1)
            tag = {'id':int(tags[j][0]),'score':0.405861}
            content_info['info']['tagInfo'].append(tag)
        for quality in quality_features:
            if int(content[0]) == quality[2]:
                content_info['info']['newsProfile']['qualityFeature'] = quality[0]
                content_info['info']['newsProfile']['qualityScore'] = float(quality[1])
                content_info['info']['newsProfile']['seg_words'] = str(quality[3])
        filewrite.write(json.dumps(content_info, ensure_ascii=False,encoding='utf-8'))
    filewrite.close()

def generate_content(contents):
    """
    get content
    """
    list = []
    for content in contents:
        for i in range(0, len(content)):
            list.append(content[i])

            

    
def main():
    try:
        conn = MySQLdb.connect(host = '10.26.188.23', \
                port = 5100, user = 'wuxiaowei01', passwd \
                = '03hQkG62xq', db = 'cpu_cc', charset='utf8')
        logging.info("connect to database")
    except BaseException, e:
        logging.warning("failed to connect to database")
    cursor = conn.cursor()
    contents = get_content_info(cursor)
    tags = get_tag_info(cursor)
    quality_features = get_quality_feature(cursor)
    generate_content_info(contents, tags, quality_features)

if __name__ == '__main__':
    main()
