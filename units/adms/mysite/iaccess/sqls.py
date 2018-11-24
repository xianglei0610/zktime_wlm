#coding:utf-8

u"""

    保存事件记录的sql语句
    函数名+数据库操作名name_select
    
"""

import dict4ini
#获取当前数据库
from mysite.settings import cfg
database_engine=cfg['DATABASE']['ENGINE']
from mysite import sql_utils

def checkdevice_and_savecache_update(*args):
    u"""
        修改最后连接时间
        params:
            last_activity
            devobj.id
    """
    sql=''
    params={}
    id_part={}
    
    params={'last_activity':args[0],'DevID':args[1]}
    sql=sql_utils.get_sql('sql','checkdevice_and_savecache_update','iaccess',params,id_part)
    return sql


def parse_event_to_sql_insert():
    u"""
        插入数据库的sql语句
    """
    sql=''
    sql=sql_utils.get_sql('sql','parse_event_to_sql_insert','iaccess',only_content=True)
    return sql
    
def sync_to_att_insert(*args):
    u"""
        门禁控制器事件记录写入考勤原始记录表
    """
    sql =" "
    params={}
    id_part={}

    params={'pin':args[2],'sn_name':args[0],'checktime':args[1]}
    sql=sql_utils.get_sql('sql','sync_to_att_insert','iaccess',params,id_part)
    
    return sql


def process_event_log_select1(*args):
    u"""
        获取记录，第一条为最旧的数据，查询时间比它大的记录
    """
    sql=''
    params={}
    id_part={}

    time1=args[1] and args[1][0]
    params={'DevID':args[0],'time1':time1}
    sql=sql_utils.get_sql('sql','process_event_log_select1','iaccess',params,id_part)
    
    return sql
    
def process_event_log_select2(*args):
    u"""
        查询大于这个时间的考勤原始记录信息
    """
    sql=''
    params={}
    id_part={}
    
    dateStr=strtodatetime(args[0])
    params={'dateStr':dateStr}
    sql=sql_utils.get_sql('sql','process_event_log_select2','iaccess',params,id_part)
    return sql

def process_event_log_select3():
    u"""
        查询全部人员的编号，id 
    """
    sql=''
    params={}
    id_part={}
    
    sql=sql_utils.get_sql('sql','process_event_log_select3','iaccess',params,id_part)
    return sql

def process_event_log_insert(*args):
    u"""
        插入原始记录表
    """
    sql=''
    params={}
    id_part={}
    
    params={'sn_name':args[0], 'pin':args[1],'checktime':args[2]}
    sql=sql_utils.get_sql('sql','process_event_log_insert','iaccess',params,id_part)
    return sql


#####################---end---############保存事件记录的sql语句############################

def get_card_number_select(*args):
    u"""
        实时获取控制器中未注册的卡
        params:
            args[0]:log_id
            args[1]:time_now
            args[2]:door_list
    """
    sql=''
    params={}
    id_part={}
    
    if args[0] == 'undefined':
        if args[1] == 'undefined':
            args[1] = datetime.datetime.now()
            args[1] = time_now.strftime("%Y-%m-%d %X")
        params={'time_now':args[1],'door_list':args[2]}
        id_part['where']='undefined_true'
    else:
        params={'log_id':args[0],'door_list':args[2]}
        id_part['where']='undefined_false'

    sql=sql_utils.get_sql('sql','get_card_number_select','iaccess',params,id_part) 
    
    return sql



def OpAddEmpToLevel_insert1(*args):
    u"""
        添加人员权限
        params:
            args[0]:对应权限组id
            args[1]:部门list
            
    """
    sql=''
    params={}
    id_part={}
    
    params={'levelsetID':args[0],'EmpID':args[1]}
    
    sql=sql_utils.get_sql('sql','OpAddEmpToLevel_insert1','iaccess',params,id_part) 
    
    return sql
        
    
def OpAddEmpToLevel_insert2(*args):
    u"""
        已经存在的不需要再次添加
        params:
            args[0]:对应权限组id
            args[1]:新的人员id
    """
    sql=''
    params={}
    id_part={}

    params={'levelsetID':args[0],'EmpID':args[1]}
    
    sql=sql_utils.get_sql('sql','OpAddEmpToLevel_insert2','iaccess',params,id_part) 
    
    return sql
    
    
    
#设备中人员权限的model_device
def delete_emp_bylevel_select(*args):
    u"""
        params:
            args[0]:删除人员权限的人员is元组
            args[1]:设备id
    """
    sql=''
    params={}
    id_part={}
    
    params={'EmpID':args[0],'DevID':args[1]}
    
    sql=sql_utils.get_sql('sql','delete_emp_bylevel_select','iaccess',params,id_part) 
        
    return sql

def search_accuser_bydevice_select(*args):
    u"""
        params:
            args[0]:设备id
    """
    sql=''
    params={}
    id_part={}
    
    params={'devID':args[0]}
    sql=sql_utils.get_sql('sql','search_accuser_bydevice_select','iaccess',params,id_part) 
    return sql


def set_user_privilege_select(*args):
    u"""
        设备同步数据
        params:
            args[0]:设备id
            args[1]:人员id的元组
    """
    
    sql=''
    id_part={}
    params={}
    
    params={'devID':args[0],'EmpID':args[1]}
    sql=sql_utils.get_sql('sql','set_user_privilege_select','iaccess',params,id_part)    
    #sql=sql and sql%(args[0],args[1]) or ''
    
    return sql
    

def set_multicard_select(*args):
    u"""
        同步设备的多卡开卡
        params:
            args[0]:门id
    """
    sql=''
    id_part={}
    params={}
    
    params={'door_id':args[0]}
    
    sql=sql_utils.get_sql('sql','set_multicard_select','iaccess',params,id_part)    
    return sql


def UploadUserInfoz_update(*args):
    u"""
        获取人员信息
        params:
            args[0]:user_count从设备中获取人数
            args[1]:dev_id设备ID
            args[2]:fp_count从设备中获取指纹数
    """
    sql=''
    fp_count=args[2] and args[2] or 0
    id_part={}
    params={}
    
    if fp_count:
        id_part['where']='fp_count_true'
    else:
        id_part['where']='fp_count_false'
    params={'user_count':args[0],'dev_id':args[1],'fp_count':fp_count}
    sql=sql_utils.get_sql('sql','UploadUserInfoz_update','iaccess',params,id_part)
    return sql
    
        


