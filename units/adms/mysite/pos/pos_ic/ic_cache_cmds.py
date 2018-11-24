# -*- coding: utf-8 -*-
from django.db.models import Q,Max
from django.core.cache import cache
from django.conf import settings
import os
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import connection as conn
import types 

#基于Memcached 进程缓存
CMDS_KEY_PREFIX = "zk_cmds_list_%s" #缓存中设备命令id列表的键值 cmds_id_list
CMD_KEY = "zk_cmd_%s" #缓存中，每个命令的键值
PROCESSING_MAX_PK = "zk_cmds_%s_pmp" #命令队列中最大命令PK processing_max_pk
LAST_SAVE_CMD_PK = "zk_cmds_%s_lsp" #数据库中命令最大pk last_save_pk
START_PROCESSED_INDEX = "zk_cmds_%s_spi" #上一次下发命令在命令队列中的起始序号 start_processed_index
END_PROCESSED_INDEX = "zk_cmds_%s_epi" #上一次下发命令在命令队列中的结束序号 end_processed_index

DEV_KEY_PREFIX =  "zk_dev_%s" #缓存中设备的键值

MAX_SIZE_PER_DEVICE_CMDS = settings.MAX_SIZE_PER_DEVICE_CMDS #缓存中，每个设备最大命令容量
MAX_SIZE_PER_CMD = settings.MAX_SIZE_PER_CMD #每条命令最大容量

TIMEOUT = 7*24*3600 #7天

LAST_ACTIVITY_PREV_SAVE_TIME = "zk_get_time_%s"

HALF_HOUR = 1800

IS_MYSQL_DB = 1
IS_SQLSERVER_DB = 2
IS_ORACLE_DB = 3
IS_POSTGRESQL_DB = 4


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

def get_prev_save_time(device_obj):
    u"获取前一次last_activity保存时间"
    import datetime
    key = LAST_ACTIVITY_PREV_SAVE_TIME%device_obj.sn
    dt = cache.get(key)
    if not dt:
        dt = datetime.datetime.now()
        cache.set(key,dt,HALF_HOUR)
    return dt

def save_last_activity(device_obj):
    u"保存last_activity到数据库"
    import datetime
    key = LAST_ACTIVITY_PREV_SAVE_TIME%device_obj.sn
    cache.set(key,datetime.datetime.now(),HALF_HOUR)

def set_last_save_cmd_pk(device_pk,max_cmd_pk):
    u"设置最后一次保存的命令PK"
    key = LAST_SAVE_CMD_PK%device_pk
    cache.set(key,max_cmd_pk,TIMEOUT)


def check_and_init_cmds_cache(device_obj):
    u"检查缓存命令结构是否存在，如果不存在初始化缓存命令结构"
    device_pk = device_obj.pk
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    key_pmk = PROCESSING_MAX_PK%device_pk #队列中最大命令PK键
    key_lscp = LAST_SAVE_CMD_PK%device_pk #数据库中最大PK键
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    
    #check_是否存在需要细化
    cache_value = cache.get(key_cmds)
    key_pmk_value = cache.get(key_pmk)
    key_lscp_value = cache.get(key_lscp)
    key_spi_value = cache.get(key_spi)
    key_epi_value = cache.get(key_epi)
    
    
    if None in (cache_value,key_pmk_value,key_lscp_value ,key_spi_value,key_epi_value):#只要有一个过期了
        #print 'init struct for device %s\n'%device_obj
        from mysite.iclock.models.model_devcmd import DevCmd
        count = int(MAX_SIZE_PER_DEVICE_CMDS/MAX_SIZE_PER_CMD)
        
        ATT_DEVICE=1 #
        POS_DEVICE = 5
        if device_obj.device_type not in [ATT_DEVICE,POS_DEVICE]:
            return None
        
        timeout=TIMEOUT
        
        cmds=DevCmd.objects.filter(
                SN__id=device_pk
            ).filter(
                Q(CmdTransTime__isnull=True)
            ).order_by('id')
        cmds=list(cmds[:count])
        processing_max_pk=0
        if cmds:
            processing_max_pk=cmds[-1].pk
        
        last_save_cmd_pk=DevCmd.objects.filter(SN__id=device_pk).aggregate(max_id=Max("id"))["max_id"]
        if not last_save_cmd_pk:
            last_save_cmd_pk=0
           
        cmds_id_list = []
        
        for e in cmds:
            cmd_key = CMD_KEY%e.pk
            cache.set(cmd_key, e, TIMEOUT)
            cmds_id_list.append(cmd_key)
        
        cache.set(key_cmds,cmds_id_list,TIMEOUT)    
        cache.set(key_pmk,processing_max_pk,TIMEOUT)
        if not  cache.get(key_lscp):
            cache.set(key_lscp,last_save_cmd_pk,TIMEOUT)
        cache.set(key_spi,0,TIMEOUT)
        cache.set(key_epi,0,TIMEOUT)
    
    
INSERT_SQL=u'''INSERT INTO devcmds_bak(
                    SN_id,CmdOperate_id,CmdContent,CmdCommitTime,CmdTransTime,
                    CmdOverTime,CmdReturn,CmdReturnContent,CmdImmediately,status
                ) VALUES(
                    %(sn_id)s,%(cmdoperate_id)s,%(cmdcontent)s,
                    %(cmdcommittime)s,%(cmdtranstime)s,%(cmdovertime)s,
                    %(cmdreturn)s,%(cmdreturncontent)s,%(cmdimmediately)s,
                    '0'
                ) 
            '''
MYSQL_INSERT_SQL=u'''INSERT INTO devcmds_bak(
                    SN_id,CmdOperate_id,CmdContent,CmdCommitTime,CmdTransTime,
                    CmdOverTime,CmdReturn,CmdReturnContent,CmdImmediately,status
                ) VALUES %(batch_rows)s;
'''
DELETE_SQL=u'''
    DELETE FROM devcmds WHERE id in 
    (%s)
'''
UPDATE_SQL = u'''
    UPDATE  devcmds SET SN_id =%(sn_id)s ,CmdOperate_id =%(cmdoperate_id)s ,CmdContent = %(cmdcontent)s ,
        CmdCommitTime =%(cmdcommittime)s ,CmdTransTime =%(cmdtranstime)s ,CmdOverTime = %(cmdovertime)s,
        CmdReturn = %(cmdreturn)s,CmdReturnContent = %(cmdreturncontent)s,CmdImmediately = %(cmdimmediately)s,
        status ='0' 
    WHERE id = %(id)s
'''    

def update_and_load_cmds(device_obj):
    u'''
        检查命令是否全部执行完了，如果执行完了，
        更新数据库，加载新的命令
    '''
    device_pk = device_obj.pk
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    key_pmk = PROCESSING_MAX_PK%device_pk #队列中最大命令PK键
    key_lscp = LAST_SAVE_CMD_PK%device_pk #数据库中最大PK键
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    
    cmds_value = cache.get(key_cmds)
    if types.ListType == type(cmds_value):
        start_index =cache.get(key_spi)
        end_index = cache.get(key_epi)
        #print 'ss start_index:%s,%s\n'%(start_index,end_index)
        if (start_index == end_index and  len(cmds_value) == end_index and end_index != 0) or len(cmds_value) < end_index:#全部执行完了，更新命令到数据库
            #print 'upload data,start_index:%s,end_index:%s\n'%(start_index,end_index)
            failed_cmds_sql = []
            cmds_pk_list = []
            update_sql = []
            for cmd_key in cmds_value:
                cmd_obj = cache.get(cmd_key)
                cmds_pk_list.append("%s"%cmd_obj.id)
                if cmd_obj.CmdReturn != "0":
                    record_dict ={
                        "sn_id":cmd_obj.SN_id,
                        "cmdoperate_id":cmd_obj.CmdOperate_id or "NULL",
                        "cmdcontent":u"'%s'"%cmd_obj.CmdContent,
                        "cmdcommittime":cmd_obj.CmdCommitTime and  u"'%s'"%cmd_obj.CmdCommitTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "cmdtranstime":cmd_obj.CmdTransTime and u"'%s'"%cmd_obj.CmdTransTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "cmdovertime":cmd_obj.CmdOverTime and u"'%s'"%cmd_obj.CmdOverTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "cmdreturn":cmd_obj.CmdReturn or  "NULL",
                        "cmdreturncontent":u"'%s'"%cmd_obj.CmdReturnContent,
                        "cmdimmediately":u"'%s'"%cmd_obj.CmdImmediately,
                    }
                        
                    if db_select == IS_SQLSERVER_DB:#SQLSERVER数据库
                        failed_cmds_sql.append(INSERT_SQL%record_dict)
                    elif db_select == IS_MYSQL_DB:#MYSQL数据库
                        failed_cmds_sql.append(
                                '''(
                                    %(sn_id)s,%(cmdoperate_id)s,%(cmdcontent)s,
                                    %(cmdcommittime)s,%(cmdtranstime)s,%(cmdovertime)s,
                                    %(cmdreturn)s,%(cmdreturncontent)s,%(cmdimmediately)s,
                                    '0'
                                )''' %record_dict
                        )
                            
                if not settings.DELETE_PROCESSED_CMD:
                    update_sql.append(
                        UPDATE_SQL%{
                            "id":cmd_obj.pk,
                            "sn_id":cmd_obj.SN_id,
                            "cmdoperate_id":cmd_obj.CmdOperate_id or "NULL",
                            "cmdcontent":u"'%s'"%cmd_obj.CmdContent,
                            "cmdcommittime":cmd_obj.CmdCommitTime and  u"'%s'"%cmd_obj.CmdCommitTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                            "cmdtranstime":cmd_obj.CmdTransTime and u"'%s'"%cmd_obj.CmdTransTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                            "cmdovertime":cmd_obj.CmdOverTime and u"'%s'"%cmd_obj.CmdOverTime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                            "cmdreturn":cmd_obj.CmdReturn or  "NULL",
                            "cmdreturncontent":u"'%s'"%cmd_obj.CmdReturnContent,
                            "cmdimmediately":u"'%s'"%cmd_obj.CmdImmediately,
                        }
                    )
            delete_sql = DELETE_SQL%(u",".join(cmds_pk_list))
            cursor = conn.cursor()
            #备份失败的命令
            if failed_cmds_sql:
                if db_select == IS_SQLSERVER_DB:
                    cursor.execute(u";".join(failed_cmds_sql))
                    #conn._commit()
                elif db_select == IS_MYSQL_DB:
                    sql=MYSQL_INSERT_SQL%({
                        "batch_rows":u",".join(failed_cmds_sql)
                    })
                    cursor.execute(sql)
                    #conn._commit()
                    
            #删除原始表中的记录
            if settings.DELETE_PROCESSED_CMD:
                cursor.execute(delete_sql)
                #conn._commit()  
            else:
                cursor.execute(u";".join(update_sql))
            
            try:
                conn._commit()
            except:
                import traceback;traceback.print_exc();
                pass
            
            #重置缓存变量，清空缓存数据
#            print u"重置缓存变量，清空缓存数据"
            cache.set(key_cmds,[],TIMEOUT)
            cache.set(key_spi,0,TIMEOUT)
            cache.set(key_epi,0,TIMEOUT)
            for k  in cmds_value:
                cache.delete(k)
        
        
        #检查是否需要加入命令    
        last_save_cmd_pk = cache.get(key_lscp)
        processing_max_pk = cache.get(key_pmk)
        
        #判断是否有命令需要加入缓存
        if processing_max_pk<last_save_cmd_pk and end_index == 0:
            from mysite.iclock.models.model_devcmd import DevCmd
            #print 'add commands \n'
            count = int(MAX_SIZE_PER_DEVICE_CMDS/MAX_SIZE_PER_CMD)
            
            ATT_DEVICE=1 #
            POS_DEVICE = 5
            if device_obj.device_type not in [ATT_DEVICE,POS_DEVICE]:
                return None
            
            timeout=TIMEOUT
            
            cmds=DevCmd.objects.filter(
                    SN__id=device_pk
                ).filter(
                    Q(CmdTransTime__isnull=True)
                ).order_by('id')
            cmds=list(cmds[:count])
            processing_max_pk=0
            if cmds:
                processing_max_pk=cmds[-1].pk
               
            cmds_id_list = []
            
            for e in cmds:
                cmd_key = CMD_KEY%e.pk
                cache.set(cmd_key, e, TIMEOUT)
                cmds_id_list.append(cmd_key)
            
            cache.set(key_cmds,cmds_id_list,TIMEOUT)   
            if processing_max_pk: 
                cache.set(key_pmk,processing_max_pk,TIMEOUT)
            cache.set(key_spi,0,TIMEOUT)
            cache.set(key_epi,0,TIMEOUT)
                
            
def check_pre_request(device_obj):
    u'''
    检测上次下发命令,机器是否接收到,
    只要有一条命令确认了，就代表执行成功
    '''
    device_pk = device_obj.pk
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    #SUCCESS = "0" #命令执行成功标示
    
    start_index = cache.get(key_spi)
    end_index = cache.get(key_epi)
    
    if start_index == end_index:
        #print 'pre request success\n'
        return True
    
    if settings.GETREQ_THREE_TIMES:
        cmd_ids = cache.get(key_cmds)
        for index in range(start_index,end_index):
            cmd_key = cmd_ids[index]
            cmd_obj = cache.get(cmd_key)
            if cmd_obj.CmdReturn < -99998:
                cache.set(key_spi,end_index,TIMEOUT)
                #print '-99998 pre check cmds\n'
                #print 'pre request success\n'
                return True
            #print 'cmd_obj return:%s\n'%cmd_obj.CmdReturn
    #print 'pre request fail\n'
    return False
 
def get_pre_request_cmds(device_obj):
    u"返回上一次下发的命令"
    device_pk = device_obj.pk
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    start_index = cache.get(key_spi)
    end_index = cache.get(key_epi)
    cmd_ids = cache.get(key_cmds)
    #print 'get pre request cmds,start_index:%s,end_index:%s\n'%(start_index,end_index)
    return cmd_ids[start_index:end_index]

def get_request_cmds(device_obj):
    u"取得当前命令"
    device_pk = device_obj.pk
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    end_index = cache.get(key_epi)
    cmd_ids = cache.get(key_cmds)
    try:
    #print 'get current request cmds %s \n'%cmd_ids[end_index:]
        return cmd_ids[end_index:]
    except:
        return None

def post_check_update(device_obj,rets):
    '''
    移动命令批次处理的开始指针
    '''
    device_pk = device_obj.pk
    length = len(rets)
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    key_cmds = CMDS_KEY_PREFIX%device_pk #命令键
    
    start_index =cache.get(key_spi)
    end_index =cache.get(key_epi)
    
    if settings.GETREQ_THREE_TIMES:
        getreq_length = end_index-start_index
        if length!= getreq_length:
            cmd_ids = cache.get(key_cmds)   #此批名林ID列表
            for index in range(start_index,end_index):
                cmd_key = cmd_ids[index]
                cmd_obj = cache.get(cmd_key)    #根据ID获取命令对象
                if cmd_obj.CmdReturn < -99998:
                    cache.set(key_spi,end_index,TIMEOUT)    #移动开始指针
                    #print '-99998 check cmds\n'
                    break
            
        else:
            #print 'check cmds getreq tree times\n'
            cache.set(key_spi,end_index,TIMEOUT)
    else:#不管长度是否相等，都更新
        #print 'check cmds \n'
        cache.set(key_spi,end_index,TIMEOUT)    #移动开始指针
        
    
            
def update_start_end_index(device_obj,count):
    u"更新起始和结束位置"
    device_pk = device_obj.pk
    key_spi = START_PROCESSED_INDEX%device_pk #上一次处理的起始序号
    key_epi = END_PROCESSED_INDEX%device_pk #上一次处理的结束序号
    end_index = cache.get(key_epi)
    
    #print 'count:%s,update startindex:%s,endindex:%s\n'%(count,end_index,end_index+count)
    cache.set(key_spi,end_index,TIMEOUT)
    cache.set(key_epi,end_index+count,TIMEOUT)
    

def update_cached_cmd(cmd_obj):
    u"设备确认命令时，更新命令到缓存"
    cmd_key= CMD_KEY%cmd_obj.id
    cache.set(cmd_key,cmd_obj,TIMEOUT)

def get_cached_cmd(cmd_id):
    u"通过cmd_id从缓存中得到命令"
    cmd_key = CMD_KEY%cmd_id
    return cache.get(cmd_key)
    
def get_device_last_activity(device):
    u"得到设备的最后通信时间"
    dev_obj=get_device(device.sn)
    return dev_obj.last_activity

def cache_delete_cmds(device):
    u'''删除设备命令结构'''
    device_pk = device.pk
    cache_key=CMDS_KEY_PREFIX%device_pk
    cache.delete(cache_key)
    cache_key = START_PROCESSED_INDEX%device_pk
    cache.delete(cache_key)
    cache_key = END_PROCESSED_INDEX%device_pk
    cache.delete(cache_key)

def cache_delete_device(device):
    u'''删除设备缓存'''
    cache_key=DEV_KEY_PREFIX%device.sn
    cache.delete(cache_key)


def check_db_device():
    u"如果是第一次，先读取数据库中已有的设备SN,写入到文件"
    from mysite.iclock.models import Device
    devlist_file=settings.DEVICE_SN_LIST
    if not os.path.exists(devlist_file):
        try:
            f=file(devlist_file,"w+")
            add_sns = []
            dev_all = Device.objects.all()
            for dev in dev_all:
                add_sns.append(dev.sn)
            
            f.write("\n".join(add_sns)+"\n")
        finally:
            f.close()
        return True #存储SN的文件不存在，创建文件
    return False #存储SN的文件已经存在
    
def cache_delete_sn(device):
    u'''删除文件中缓存的SN序列号'''
    devlist_file=settings.DEVICE_SN_LIST
    sn_list=[]
            
    check_db_device()
    #读取文件中的序列号
    try:
        f=file(devlist_file,"r+")
        sn_list=list(set(f.read().strip().split("\n")))
    finally:
        f.close()
        
    #删除该设备的SN
    try:
        f=file(devlist_file,"w+")
        sn_list=[e for e in sn_list if e!=device.sn]
        f.write("\n".join(sn_list)+"\n")
    finally:
        f.close()
        
def cache_device_sn(device):
    u'''文件缓存更新设备SN'''
    #文件缓存设备SN
    create_file = check_db_device()
    if create_file:
        return False
        
    devs_file=settings.DEVICE_SN_LIST
    try:
        f=file(devs_file,"a+")
        f.write("%s\n"%device.sn)
    finally:
        f.close()
    
def cache_device(device):
    u'''
    缓存设备对象,
    键值：DEV_KEY_PREFIX_+DEVICE.SN
    '''
    cache_key=DEV_KEY_PREFIX%device.sn
    cache.set(cache_key,device,settings.COMMAND_TIMEOUT*3600)

def get_device(sn):
    u'''从缓存中读取设备,如果没有得到则读数据库取'''
    from mysite.iclock.models  import Device
    cache_key=DEV_KEY_PREFIX%sn
    cache_obj=cache.get(cache_key)
    if not cache_obj:
        try:
            cache_obj=Device.objects.get(sn=sn)
            cache.set(cache_key,cache_obj,settings.COMMAND_TIMEOUT*3600)
        except:
            cache_obj=None
    
    return cache_obj


def get_device_raise(sn):
    u'''通过sn取设备，如果没有取到抛出异常!'''
    from mysite.iclock.models  import Device
    cache_key=DEV_KEY_PREFIX%sn
    cache_obj=cache.get(cache_key)
    if not cache_obj:
        try:
            cache_obj=Device.objects.get(sn=sn)
            cache.set(cache_key,cache_obj,settings.COMMAND_TIMEOUT*3600)
        except:
            raise ObjectDoesNotExist
            cache_obj=None
    
    return cache_obj
    
def get_snlist():
    u'''
    如果发现该文件还没有，则创建，
    写入所有已有设备SN,
    从文件中读取缓存的设备SN的值
    '''
    from mysite.iclock.models import Device
    devlist_file=settings.DEVICE_SN_LIST
    sn_list=[]
    ATT_DEVICE=1
    if not os.path.exists(devlist_file):
        dev_objs=Device.objects.filter(device_type__in=[ATT_DEVICE,])
        sn_list=[e.sn for e in dev_objs]
        try:
            f=file(devlist_file,"w+")
            f.write("\n".join(sn_list)+"\n")
            f.close()
        except:
            f.close()
    else:
        try:
            f=file(devlist_file,"r+")
            sn_list=f.read()
            f.close()
            sn_list=sn_list.strip().split("\n")
        except:
            f.close()
    return sn_list
    
    
def get_all_device():
    u'''取得缓存中的所有设备'''
    dev_list=[]
    sn_list = get_snlist()
    for sn in sn_list:
        dev_obj=get_device(sn)
        if dev_obj:
            dev_list.append(dev_obj)
    return dev_list

    







