#-*- coding: utf-8 -*-

#import pymssql
#args = (0,0,0,100,0,0,None )
#conn_kwargs = {
#               'host':'127.0.0.1\SQLEXPRESS',
#                'user':'sa', 
#                'charset':'utf8',
#                'password':'123123', 
#                'database': 'ltcj_x'}


import dict4ini
cfg = dict4ini.DictIni("../attsite.ini")

db_cfg = cfg["DATABASE"]

HOST = ""
PORT = ""
if db_cfg["ENGINE"]=="sqlserver_ado":
    import pymssql as pyDB
    HOST = db_cfg.has_key("HOST") and db_cfg["HOST"].replace("\\\\","\\") or "127.0.0.1"
    PORT = db_cfg.has_key("PORT") and db_cfg["PORT"] or 1433
elif  db_cfg["ENGINE"]=="mysql":
    import MySQLdb as pyDB
    HOST = db_cfg.has_key("HOST") and db_cfg["HOST"] or "127.0.0.1"
    PORT = db_cfg.has_key("PORT") and db_cfg["PORT"] or 3306
elif db_cfg["ENGINE"]=="oracle":
    # 如果需要支持 oracle 请自行配置
    pass
CHARSET = 'utf8'
USER = db_cfg.has_key("USER") and db_cfg["USER"] or ""
PASSWORD = db_cfg.has_key("PASSWORD") and db_cfg["PASSWORD"] or ""
NAME = db_cfg.has_key("NAME") and db_cfg["NAME"] or ""

conn_args = {
        'host':"%s"%HOST,
        'user':"%s"%USER, 
        'charset':"%s"%CHARSET,
        'password':"%s"%PASSWORD, 
        'database':"%s"%NAME,
        'port':PORT
        }
"""
    mincached : 启动时开启的闲置连接数量(缺省值 0 意味着开始时不创建连接)
    maxcached: 连接池中允许闲置的最多连接数量(缺省值 0 代表不限制连接池大小)
    maxshared: 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量，被请求为共享的连接将会被共享使用。
    maxconnections: 创建连接池的最大数量(缺省值 0 代表不限制)
    blocking: 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>；其他代表阻塞直到连接数减少,连接被分配)
    maxusage: 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用)。当达到最大数值时，连接会自动重新连接(关闭和重新打开)
    setsession: 一个可选的SQL命令列表用于准备每个会话，如 ["set datestyle to german", ...]  
"""
args = (10,10,10,50,True,0,None )