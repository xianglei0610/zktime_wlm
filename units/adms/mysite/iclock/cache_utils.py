# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import connection as conn
from django.core.cache import cache
from django.db.models import Q,Max
from mysite.iclock.sql import cache_utils_insert_sql,cache_utils_delete_sql,cache_utils_update_sql

IS_MYSQL_DB = 1
IS_SQLSERVER_DB = 2
IS_ORACLE_DB = 3
IS_POSTGRESQL_DB = 4

TIMEOUT = 7*24*3600

CMDS_KEY_PREFIX = "zk_cmds_list_%s" #缓存中设备命令id列表的键值

#根据不同的数据库 执行对应的sql语句
db_select = IS_MYSQL_DB
if 'mysql' in conn.__module__:#mysql 数据库
    db_select = IS_MYSQL_DB
elif 'sqlserver_ado' in conn.__module__:#sqlserver 2005 数据库 
    db_select = IS_SQLSERVER_DB
elif 'oracle' in conn.__module__: #oracle 数据库 
    db_select = IS_ORACLE_DB
elif 'postgresql_psycopg2' in conn.__module__: # postgresql 数据库
    db_select = IS_POSTGRESQL_DB

 
#INSERT_SQL=u'''INSERT INTO devcmds_bak(
#                    SN_id,CmdOperate_id,CmdContent,CmdCommitTime,CmdTransTime,
#                    CmdOverTime,CmdReturn,CmdReturnContent,CmdImmediately,status
#                ) VALUES(
#                    %(sn_id)s,%(cmdoperate_id)s,%(cmdcontent)s,
#                    %(cmdcommittime)s,%(cmdtranstime)s,%(cmdovertime)s,
#                    %(cmdreturn)s,%(cmdreturncontent)s,%(cmdimmediately)s,
#                    '0'
#                ) 
#            '''
#MYSQL_INSERT_SQL=u'''INSERT INTO devcmds_bak(
#                    SN_id,CmdOperate_id,CmdContent,CmdCommitTime,CmdTransTime,
#                    CmdOverTime,CmdReturn,CmdReturnContent,CmdImmediately,status
#                ) VALUES %(batch_rows)s;
#'''
#POSTGRE_INSERT_SQL='''INSERT INTO devcmds_bak(
#                    "SN_id","CmdOperate_id","CmdContent","CmdCommitTime","CmdTransTime",
#                    "CmdOverTime","CmdReturn","CmdReturnContent","CmdImmediately",status
#                ) VALUES(
#                    %(sn_id)s,%(cmdoperate_id)s,%(cmdcontent)s,
#                    %(cmdcommittime)s,%(cmdtranstime)s,%(cmdovertime)s,
#                    %(cmdreturn)s,%(cmdreturncontent)s,%(cmdimmediately)s,
#                    '0'
#                ) 
#            '''
#DELETE_SQL=u'''
#    DELETE FROM devcmds WHERE id in 
#    (%s)
#'''
#UPDATE_SQL = u'''
#    UPDATE  devcmds SET SN_id =%(sn_id)s ,CmdOperate_id =%(cmdoperate_id)s ,CmdContent = %(cmdcontent)s ,
#        CmdCommitTime =%(cmdcommittime)s ,CmdTransTime =%(cmdtranstime)s ,CmdOverTime = %(cmdovertime)s,
#        CmdReturn = %(cmdreturn)s,CmdReturnContent = %(cmdreturncontent)s,CmdImmediately = %(cmdimmediately)s,
#        status ='0' 
#    WHERE id = %(id)s
#'''
#POSTGRE_UPDATE_SQL=u'''
#    UPDATE  devcmds SET "SN_id" =%(sn_id)s ,"CmdOperate_id" =%(cmdoperate_id)s ,"CmdContent" = %(cmdcontent)s ,
#    "CmdCommitTime" =%(cmdcommittime)s ,"CmdTransTime" =%(cmdtranstime)s ,"CmdOverTime" = %(cmdovertime)s,
#    "CmdReturn" = %(cmdreturn)s,"CmdReturnContent" = %(cmdreturncontent)s,"CmdImmediately" = %(cmdimmediately)s,
#    status ='0' 
#    WHERE id = %(id)s
#'''

def run_cmds(device_pk):
    key_cmds = CMDS_KEY_PREFIX%device_pk
    cmds_value = cache.get(key_cmds)
    if cmds_value:
        update_cmds(cmds_value,device_pk)
    set_cmds(device_pk)
        
        
def update_cmds(cmds_value,device_pk):
    failed_cmds_sql = []
    cmds_pk_list = []
    update_sql = []
    for cmd_key in cmds_value:
        cmd_obj = cache.get(cmd_key)
        cmds_pk_list.append("%s"%cmd_obj.id)
        if cmd_obj.CmdReturn != "0":
            if cmd_obj.CmdCommitTime:
                cmdcommittime = u"'%s'"%cmd_obj.CmdCommitTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdcommittime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdcommittime
                
            else:
                cmdcommittime = "NULL"
                
            if cmd_obj.CmdTransTime:
                cmdtranstime = u"'%s'"%cmd_obj.CmdTransTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdtranstime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdtranstime
                
            else:
                cmdtranstime = "NULL"
                
            if cmd_obj.CmdOverTime:
                cmdovertime = u"'%s'"%cmd_obj.CmdOverTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdovertime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdovertime
            else:
                cmdovertime = "NULL"
            
            record_dict ={
                "sn_id":cmd_obj.SN_id,
                "cmdoperate_id":cmd_obj.CmdOperate_id or "NULL",
                "cmdcontent":u"'%s'"%cmd_obj.CmdContent,
                "cmdcommittime":cmdcommittime,
                "cmdtranstime":cmdtranstime,
                "cmdovertime":cmdovertime,
                "cmdreturn":cmd_obj.CmdReturn or  "NULL",
                "cmdreturncontent":u"'%s'"%cmd_obj.CmdReturnContent,
                "cmdimmediately":u"'%s'"%int(cmd_obj.CmdImmediately),
            }
            INSERT_SQL=cache_utils_insert_sql(record_dict)
            failed_cmds_sql.append(INSERT_SQL)    
#            if db_select == IS_SQLSERVER_DB or db_select == IS_ORACLE_DB or db_select == IS_POSTGRESQL_DB:
#                failed_cmds_sql.append(INSERT_SQL)
#            elif db_select == IS_MYSQL_DB:#MYSQL数据库
#                failed_cmds_sql.append(
#                        '''(
#                            %(sn_id)s,%(cmdoperate_id)s,%(cmdcontent)s,
#                            %(cmdcommittime)s,%(cmdtranstime)s,%(cmdovertime)s,
#                            %(cmdreturn)s,%(cmdreturncontent)s,%(cmdimmediately)s,
#                            '0'
#                        )''' %record_dict
#                )
                    
        if not settings.DELETE_PROCESSED_CMD:
            if cmd_obj.CmdCommitTime:
                cmdcommittime = u"'%s'"%cmd_obj.CmdCommitTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdcommittime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdcommittime
                
            else:
                cmdcommittime = "NULL"
                
            if cmd_obj.CmdTransTime:
                cmdtranstime = u"'%s'"%cmd_obj.CmdTransTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdtranstime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdtranstime
                
            else:
                cmdtranstime = "NULL"
                
            if cmd_obj.CmdOverTime:
                cmdovertime = u"'%s'"%cmd_obj.CmdOverTime.strftime("%Y-%m-%d %H:%M:%S")
                if db_select == IS_ORACLE_DB:
                    cmdovertime = "to_date(%s,'yyyy-mm-dd hh24:mi:ss')"%cmdovertime
            else:
                cmdovertime = "NULL"
            update_dict={
                    "id":cmd_obj.pk,
                    "sn_id":cmd_obj.SN_id,
                    "cmdoperate_id":cmd_obj.CmdOperate_id or "NULL",
                    "cmdcontent":u"'%s'"%cmd_obj.CmdContent,
                    "cmdcommittime":cmdcommittime,
                    "cmdtranstime": cmdtranstime,
                    "cmdovertime":cmdovertime,
                    "cmdreturn":cmd_obj.CmdReturn or  "NULL",
                    "cmdreturncontent":u"'%s'"%cmd_obj.CmdReturnContent,
                    "cmdimmediately":u"'%s'"%int(cmd_obj.CmdImmediately),
                }
            UPDATE_SQL=cache_utils_update_sql(update_dict)
            update_sql.append(UPDATE_SQL)
#            update_sql.append(
#                UPDATE_SQL%{
#                    "id":cmd_obj.pk,
#                    "sn_id":cmd_obj.SN_id,
#                    "cmdoperate_id":cmd_obj.CmdOperate_id or "NULL",
#                    "cmdcontent":u"'%s'"%cmd_obj.CmdContent,
#                    "cmdcommittime":cmdcommittime,
#                    "cmdtranstime": cmdtranstime,
#                    "cmdovertime":cmdovertime,
#                    "cmdreturn":cmd_obj.CmdReturn or  "NULL",
#                    "cmdreturncontent":u"'%s'"%cmd_obj.CmdReturnContent,
#                    "cmdimmediately":u"'%s'"%int(cmd_obj.CmdImmediately),
#                }
#            )
    delete_sql =cache_utils_delete_sql(u",".join(cmds_pk_list))
    cursor = conn.cursor()
    #备份失败的命令
    if failed_cmds_sql:
        if db_select == IS_SQLSERVER_DB or db_select == IS_POSTGRESQL_DB or db_select == IS_MYSQL_DB:
            cursor.execute(u";".join(failed_cmds_sql))
#        elif db_select == IS_MYSQL_DB:
#            sql=INSERT_SQL%({
#                "batch_rows":u",".join(failed_cmds_sql)
#            })
#            cursor.execute(sql)
        elif db_select == IS_ORACLE_DB:
            for elem_sql in failed_cmds_sql:
                cursor.execute(elem_sql)
            
    #删除原始表中的记录
    if settings.DELETE_PROCESSED_CMD:
        cursor.execute(delete_sql)
    else:
        sql = u";".join(update_sql)
        if db_select == IS_ORACLE_DB:
            for elem_sql in update_sql:
                cursor.execute(elem_sql)
        else:
            cursor.execute( sql )
    
    try:
        conn._commit()
    except:
        import traceback;traceback.print_exc();
        pass
    
    #重置缓存变量，清空缓存数据
    key_cmds = CMDS_KEY_PREFIX%device_pk    #+++++++++++++++
    cache.set(key_cmds,[],TIMEOUT)
#    cache.set(key_spi,0,TIMEOUT)
#    cache.set(key_epi,0,TIMEOUT)
    for k  in cmds_value:
        cache.delete(k)
  
from mysite.iclock.models.model_devcmd import DevCmd 
        
def set_cmds(device_pk):
    CMD_KEY = "zk_cmd_%s" #缓存中，每个命令的键值
    
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    
    cmds=DevCmd.objects.filter(
            SN__id=device_pk
        ).filter(
            Q(CmdTransTime__isnull=True)
        ).order_by('id')
    cmds=list(cmds[:1])
    
    cmds_id_list = []
    for e in cmds:
        cmd_key = CMD_KEY%e.pk
        cache.set(cmd_key, e, TIMEOUT)
        cmds_id_list.append(cmd_key)
    
    cache.set(key_cmds,cmds_id_list,TIMEOUT)   
    
def get_cmds(device_pk):
    key_cmds = CMDS_KEY_PREFIX%device_pk
    cmd_ids = cache.get(key_cmds)
    return  cmd_ids