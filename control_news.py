#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import logging
import time
import ConfigParser
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

def run():
    configure = ConfigParser.ConfigParser()
    configure.read('reason.conf')
    figures = configure.options('reason')
    for figure in figures:
        print figure
        reason = configure.get('reason', figure)
        print reason
        cmd = 'nohup python news_work_flow.py \"%s\" %s 2>&1 &' % (str(reason), figure)
        os.system(cmd)
        
if __name__ == '__main__':
    now = datetime.datetime.now()
    begin_time = now.replace(hour = 00, minute = 15)
    end_time = now.replace(hour = 00, minute = 45)
    if now >= begin_time and now <= end_time:
        sys.exit()
    run()




