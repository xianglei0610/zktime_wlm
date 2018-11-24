# -*- coding: utf-8 -*-

##################### 系统环境设置 #######################
def set_lib_path():
    import sys
    import os
    sys.path.append('E:/custom_work/Mole')
    #os.environ["PYTHONPATH"]='../'
set_lib_path()

from mole import route, static_file

#安装的子应用
apps_list = (
        ('personnel',u'公共维护'),
        ('att',u'考勤管理'),
        ('pos',u'消费管理')
        )

# 配置静态目录
@route('/static/:file#.*#')
def media(file):
    return static_file(file, root='./apps/media')

@route('/media/:file#.*#')
def media(file):
    return static_file(file, root='./apps/media')

import routes

#数据库接口配置
from DBUtils.PooledDB import PooledDB
############ Mysql ########
#import MySQLdb
#dbpool = PooledDB(
#            creator=MySQLdb, 
#            maxusage=1000,
#            host='localhost',
#            user='root', 
#            passwd='root',
#            db='zkeco_last')
############ Mssql #########
from zkeco_conf import pyDB, args, conn_args
dbpool = PooledDB(pyDB, *args, **conn_args)


workspace = '.'
