# -*- coding: utf-8 -*-

from base.cached_model import STATUS_PAUSED, STATUS_STOP
from constant import IP4_RE
from constant import MAX_TRANS_IN_QUEQE
from constant import REALTIME_EVENT, DEVICE_POST_DATA
import datetime
import time
from dbapp.utils import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections, IntegrityError, DatabaseError, models
from django.http import HttpResponse
from dataprocaction import append_dev_cmd
from dataprocaction import dev_update_firmware
from dataprocaction import getFW
from models import *
from models.modelproc import get_normal_card
from models.model_device import device_cmd
from mysite.personnel.models.model_emp import Employee,format_pin
from dbapp.additionfile import save_model_file
import os,sys
from redis_self.server import check_and_start_queqe_server, queqe_server
from traceback import print_exc
from cmdconvert import std_cmd_convert
from models.model_devcmd import DevCmd
from mysite.iclock.models.dev_comm_operate import *
from django.core.cache import cache
import time
from mysite.utils import get_option
try:
    import cPickle as pickle
except:
    import pickle
conn = connections['default']
POSDEVICE='30'
from models.model_face import FaceTemplate
from django.utils.translation import ugettext as _
from mysite.iclock.sql import devview_log_sql

import logging
from mysite.utils import pos_write_log
logger = logging.getLogger()
hdlr = logging.FileHandler(settings.APP_HOME+"/tmp/dev_post.log")
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)

#根据不同的数据库 执行对应的sql语句
from django.db import connection
db_select=1
if 'mysql' in connection.__module__:#mysql 数据库
    db_select=1
elif 'sqlserver_ado' in connection.__module__:#sqlserver 2005 数据库 
    db_select=2
elif 'oracle' in connection.__module__: #oracle 数据库 
    db_select=3
elif 'postgresql_psycopg2' in connection.__module__: # postgresql 数据库
    db_select=4


#根据给定员工PIN查找员工
def get_employee(pin, Device=None):
    #print "get_employe   device:%s"%Device
    s_pin = format_pin(pin)
    try:
        e=Employee.all_objects.get(PIN=s_pin)
        if e:
            e.IsNewEmp=False
            return e
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        if not settings.DEVICE_CREATEUSER_FLAG:
            return None
        
        e = Employee(PIN=s_pin, EName=pin)
        e.save()
        e.IsNewEmp=True
        return e

def normal_state(state):
    if state == '0': return 'I'
    if state == '1': return 'O'
    try:
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state

def normal_verify(state):
    try:
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state

server_time_delta = datetime.datetime.now()-datetime.datetime.utcnow()

def del_len(l):
    if l > MAX_TRANS_IN_QUEQE:
        aa = int(MAX_TRANS_IN_QUEQE / 2)
    dellen = aa
    while l-dellen > MAX_TRANS_IN_QUEQE:
        dellen += aa
    return dellen

#设备上传的考勤记录

def trigger_event(msg):
    try:
        q = queqe_server()
        id = q.incr("RTE_COUNT")
        l = q.llen(REALTIME_EVENT)
        if l >= MAX_TRANS_IN_QUEQE: #队列太长，删除部分
            aa = int(MAX_TRANS_IN_QUEQE / 2)
            dellen = aa
            while l - dellen >= MAX_TRANS_IN_QUEQE:
                dellen += aa
            
            q.ltrim(REALTIME_EVENT, 0, l - dellen - 1)  
            
            #print "%s in queqe, and will remove %s, then %s" % (l, dellen, q.llen(REALTIME_EVENT))
        #print "msg:%s"%msg
        q.lpush(REALTIME_EVENT, msg.encode("gb18030")) #写入到实时事件队列中
    except:
        print_exc()

def line_to_log(device, line, event=True):
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]

    #检查员工号码的合法性
    pin = flds[0]
    try:
        if pin in settings.DISABLED_PINS:  return None
    except:
        return None
    if flds[5] == '255' and flds[3] == '3' and flds[0] == flds[4]:
        print u"Swiped a invalid card: \n", line
        return None
    emp = get_employee(pin, device)
    if not emp:
        return None
    if emp.IsNewEmp:
        emp.DeptID_id=1
        emp.attarea=(device.area,)
        emp.save()
        #sync_set_user(devs, [e])
    pin = emp.id

    #检查考勤记录时间的合法性
    try:
        logtime = datetime.datetime.strptime(flds[1], "%Y-%m-%d %H:%M:%S")
    except:
        return None
    now=datetime.datetime.now()
    if event:
        if (now + datetime.timedelta(1, 0, 0)) < logtime: 
            print u"时间比当前时间还要多一天"
            return None
        if logtime<now-datetime.timedelta(days=settings.VALID_DAYS): 
            print u"时间比当前要早...天", settings.VALID_DAYS
            return None

    #检查记录的合法性
    if settings.CHECK_DUPLICATE_LOG or (not event): #检查重复记录
        try:
            if Transaction.objects.filter(TTime=logtime, UserID=emp): 
                print u"该记录已经存在"
                return None
        except: pass
 
    #根据考勤机的时区矫正考勤记录的时区，使之同服务器的时区保持一致
    if device.tz_adj <> None:
        count_minutes = None
        if abs(device.tz_adj)<=13:
            count_minutes = device.tz_adj*3600
        else:
            count_minutes = device.tz_adj*60
        logtime = logtime - datetime.timedelta(0, count_minutes) + server_time_delta #UTC TIM
                
    sql = (pin, logtime, normal_state(flds[2]), normal_verify(flds[3]), None, flds[4], flds[5],device.sn)
#    if event:
#        msg = "id=%s\tPIN=%s\tEName=%s\tTTime=%s\tState=%s\tVerify=%s\tDevice=%s" % \
#            (id, emp.PIN, emp.EName, flds[1], flds[2], flds[3], device.id)
#        #print "msg:%s"%msg
#        trigger_event(msg)
    return sql

def card_to_num(card):
    if card and len(card) == 12 and card[0] == '[' and card[-3:] == '00]':
        card = "%s" % (int(card[1:3], 16) + int(card[3:5], 16) * 256 + int(card[5:7], 16) * 256 * 256 + int(card[7:9], 16) * 256 * 256 * 256)
    return card

def line_to_oplog(cursor, device, flds, event=True):
    try: #0        0        2008-08-28 14:07:37        0        0        0        0
        flds = flds.split("\t")
        try:
            logtime = datetime.datetime.strptime(flds[2], "%Y-%m-%d %H:%M:%S")
        except:
            return None
        if (datetime.datetime.now() + datetime.timedelta(1, 0, 0)) < logtime: #时间比当前时间还要多一天
            return None
        if device.TZAdj <> None:
            logtime = logtime-datetime.timedelta(0, device.TZAdj * 60 * 60) + server_time_delta #UTC TIME, then server time
        obj = OpLog(SN=device, admin=flds[1], OP=flds[0], OPTime=logtime,
                    Object=flds[3], Param1=flds[4], Param2=flds[5], Param3=flds[6])
        obj.save()
#        if event:
#            msg = "id=%s\tPIN=%s\tEName=%s\tTTime=%s\tState=%s\tVerify=%s\tDevice=%s" % \
#                (id, flds[1], flds[4], logtime, flds[0], flds[3], device.id)
#            trigger_event(msg)
    except:
        return None

#设备上传的数据命令处理
def line_to_emp(cursor, device, line, Op,event=True):
    from mysite import settings
    import os
  
    try:
        if line.find("\tName=") > 0:
            ops = unicode(line.decode("gb18030")).split(" ", 1)
        else:
            ops = line.split(" ", 1)

    except:
        ops = line.split(" ", 1)
    
    if ops[0] == 'OPLOG':
        return line_to_oplog(cursor, device, ops[1], event)
    flds = {};
    for item in ops[1].split("\t"):
        index = item.find("=")
        if index > 0: flds[item[:index]] = item[index + 1:]
    #print "flds:%s"%flds
    try:
        from mysite import settings
        pin = flds["PIN"]
        if pin in settings.DISABLED_PINS or len(pin)>settings.PIN_WIDTH:
            return
    except:
        return
#                print "PIN : ", line
    e = get_employee(pin, device)
    if not e:
        return
    if str(ops[0]).strip() == "USER":
        #print "upload User"
        #writelog("user.txt", ops)
        if not settings.DEVICE_CREATEUSER_FLAG:
            return 
        
        try:
            ename = unicode(flds["Name"])[:40]
        except:
            ename = ' '
            
        passwd = flds.get("Passwd","")
        card = flds.get("Card", "")
        tmp_card = "" #卡号保存在isssuecard里面
        agrp = flds.get("Grp", "")
        tz = flds.get("TZ","")
        priv = flds.get('Pri', 0)
        fldNames = ['SN', 'utime']
        values = [device.id, str(datetime.datetime.now())[:19]]
        
        if ename and (ename != e.EName):
            fldNames.append('name')
            values.append(ename)
            e.EName = ename
        from base.crypt import encryption#设备传过来的密码没加密   需要加密再和数据库中的比较
        if passwd and (encryption(passwd) != e.Password):
            fldNames.append('password')
            values.append(passwd)
            e.Password = passwd
        if priv and (str(priv) !=str(e.Privilege)):#考虑下数据字段类型
            fldNames.append('privilege')
            values.append(str(priv))
            e.Privilege = str(priv)

        if card and (card_to_num(card) != e.Card):
            if str(card_to_num(card)).strip()!="0":
                vcard=card_to_num(card)
            else:
                vcard=""
            fldNames.append('Card')
            values.append(vcard)
            tmp_card = vcard
            #e.Card = vcard改成issuecard保存卡
            
        if agrp and (str(agrp) != str(e.AccGroup)):
            fldNames.append('AccGroup')
            values.append(str(agrp))
            e.AccGroup = str(agrp)
        if tz != e.TimeZones:
            fldNames.append('TimeZones')
            values.append(tz)
            e.TimeZones = tz
        try:
            #print "e.IsNewEmp:%s"%e.IsNewEmp
            e.IsNewEmp
        except:
            e.IsNewEmp = False
        
        if e.IsNewEmp:    #新增用户
            e.IsNewEmp = False     
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
            
            if tmp_card and not get_option("POS"):
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID
                obj_card = IssueCard()
                obj_card.UserID = e
                obj_card.cardno = tmp_card
                obj_card.cardstatus = CARD_VALID
                obj_card.save()
                
            devs=set(e.search_device_byuser()) 
            if devs:
                try:
                    devs.remove(device)
                except:
                    pass
            #sync_set_userinfo(devs, [e])#同步命令  
            for dev in devs:
                dev.set_user([e], Op,"")
                dev.set_user_fingerprint([e], Op)
                time.sleep(0.01)    
            sql = ''
        elif len(fldNames) > 2: #有新的用户信息
            devs=set(e.search_device_byuser()) 
            e.save()
            
            if tmp_card:#卡处理
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID
                try:
                    obj_card  = IssueCard.objects.get(UserID=e,cardstatus=CARD_VALID)
                except:
                    obj_card = None
                
                if not obj_card and not get_option("POS"):
                    obj_card = IssueCard()
                    obj_card.UserID = e
                    obj_card.cardno = tmp_card
                    obj_card.cardstatus = CARD_VALID
                    obj_card.save()
                else:
                    if not get_option("POS"):#消费的时候不能覆盖
                        obj_card.carno = tmp_card
                        obj_card.save()
            
            if devs:
                try:
                    devs.remove(device)
                except:
                    pass
            #sync_set_userinfo(devs, [e])#同步命令  
                
#            for dev in devs:
#                dev.set_user([e], Op,"")
#                dev.set_user_fingerprint([e], Op)
#                time.sleep(0.01)
            
            #sql = u"update userinfo set %s where badgenumber='%s'" % (','.join([u"%s='%s'" % (fldNames[i], values[i]) for i in range(len(fldNames))]), pin)
        else:
#            if devs:
            pass
#                devs.remove(device)
        return e
#            sql = ''
#        
#        if sql:
#            cursor.execute(sql)
#
#            return e
    elif str(ops[0]).strip() == "FP":
        #print "upload Template"
        #print "flds:%s"%flds    
        #writelog("fp.txt", ops)  
        if not settings.DEVICE_CREATEBIO_FLAG:
            return
          
        if e.IsNewEmp:    #新增用户               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        
        emps=e
        try:
            size=flds["Size"]            
            fp = flds["TMP"]    
                       #saas全部为10.0            
           #            check_length=False
           #            if not device.alg_ver :
           #                device.alg_ver="1.0"
           #                device.save()
           #            try:
           #                if float(device.alg_ver)>=float("2.0"):
           #                    check_length=True
           #            except:
           #                import traceback;traceback.print_exc()
           #                pass
           #            #print "device.alg_ver:%s"%device.alg_ver
           #            if (not check_length) or (check_length and fp and len(fp)==int(size)):
            d_len=len(fp.decode("base64"))
            if fp and (len(fp)==int(size) or d_len==int(size) ):
           
                devs=set(e.search_device_byuser())
                #print "FP devs:%s"%devs
                if devs:
                    try:
                        devs.remove(device)
                    except:
                        pass
                
                e = Template.objects.filter(UserID=e.id, FingerID=int(flds["FID"]),Fpversion=device.Fpversion)
                if len(e)>0:
                    e=e[0]
                    if fp[:100] == e.Template[:100]:
                        pass # Template is same
                    else:                        #指纹有修改
                        e.Template=fp
                        #e.SN=device
                        e.Fpversion=device.Fpversion
                        e.UTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        e.save()
#                        sql="update template set template=%s sn=%s fpversion=%s"%(fp,device.pk,device.Fpversion)
#                        cur=conn.cursor()
#                        cur.execute(sql)
#                        conn._commit()
#                        
                        #sync_set_user_fingerprint(devs,[emps],int(flds["FID"]))#同步指纹
                        for dev in devs:
                            dev.set_user_fingerprint([emps], Op, int(flds["FID"]))
                            time.sleep(0.01)
                else:     #新增指纹
                    e=Template()
                    e.UserID=emps
                    #e.SN=device
                    e.Template=fp
                    e.UTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    e.FingerID=int(flds["FID"])
                    e.Fpversion=device.Fpversion
                    e.Valid=1
                    e.save()
#                    sql="insert into template(userid,sn,template,fingerid,fpversion,valid,bio_type) values(%s,%s,'%s',%s,%s,1,0)"%(emps.pk,device.pk,fp,int(flds["FID"]),device.Fpversion)
#                    cur=conn.cursor()
#                    cur.execute(sql)
#                    conn._commit()
                    #sync_set_user_fingerprint(devs,[emps],int(flds["FID"]))#同步指纹
                    for dev in devs:
                        dev.set_user_fingerprint([emps], Op, int(flds["FID"]))
                        time.sleep(0.01)
                return True
            else:
                print "size:%s   TMP size:%s"%(size,len(fp))
                print "template length error"
        except:
            import traceback; traceback.print_exc();            
        else:
            return False
        
    elif str(ops[0]).strip() == "FACE" :    ######################## 新增人脸模板相关命令处理  ##################
        if e.IsNewEmp:    #-----保存设备新增用户的其他信息               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        emps=e
        try:
            from  new_push import postuser_face
            postuser_face(flds,e,device,Op)
            return True
        except:
            import traceback; traceback.print_exc();            
        else:
            return False
    elif str(ops[0]).strip() == "USERPIC" :    #####################加入用户照片 处理
        if e.IsNewEmp:    #-----保存设备新增用户的其他信息               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        emps=e
        try:
            from  new_push import postuser_photo
            postuser_photo(flds,e,device)
            return True
        except:
            import traceback; traceback.print_exc(); 
        else:
            return False

from mysite.utils import fwVerStd
up_version = fwVerStd(settings.UPGRADE_FWVERSION)

def excsql(sql):
    cursor=conn.cursor()
    count=cursor.execute(sql)   
    conn._commit()
def update_device_sql(sql,sn):
    from mysite.iclock.sql import update_device_sql_sql 
    tsql=update_device_sql_sql(sql,sn)
    #print tsql
    cursor=conn.cursor()
    count=cursor.execute(tsql)   
    conn._commit()
    conn.close()
#    print "count ",count
    device=Device.objects.filter(sn=sn)[0]
#    print device.fp_count
#    print device.transaction_count
#    print device.user_count
#    print device.fw_version
#    print device.ipaddress
#    print device.alias
    
    return device
    
#根据设备sn找对应的设备对象, 若有request,则进行自动注册该设备
def get_device(sn):
    from mysite.iclock.cache_cmds import get_device_raise
    return get_device_raise(sn)
    
#    device=Device.objects.filter(sn=sn)
#    if device:
#        return device[0]
#    else:
#        raise ObjectDoesNotExist

#根据设备http请求找对应的设备对象
def check_device(request, allow_create=False):
    from mysite.iclock.cache_cmds import check_and_init_cmds_cache
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
    try:
        device=get_device(sn)
    except ObjectDoesNotExist: #正在请求的设备没有登记过
        if get_option("ATT") and allow_create and not request.REQUEST.has_key('PIN') and ( #没有查询用户信息的话，可以注册该考勤机 
            len(sn) >= 6 and settings.ICLOCK_AUTO_REG): #若SN正确，且设置可以自动注册
            from mysite.personnel.models.model_area import Area
            device = Device(
                sn=sn, 
                alias="auto_add",
                last_activity=datetime.datetime.now(), 
                area=Area.objects.all()[0],
                ipaddress=request.META["REMOTE_ADDR"])
            device.save(force_insert=True, log_msg=False)
            append_dev_cmd(device, "INFO")
           # append_dev_cmd(device, "CHECK")
        else:
            return None
    if device.status in (STATUS_STOP, STATUS_PAUSED):
        return None
    check_and_init_cmds_cache(device) #检查缓存命令结构是否存在，如果不存在初始化缓存命令结构
    device.last_activity=datetime.datetime.now()
    return device

 
def try_sql(cursor, sql, param={}):
    try:
        cursor.execute(sql, param)
        conn._commit();
    except IntegrityError:
        raise
    except:
        conn.close()
        cursor=conn.cursor()
        cursor.execute(sql, param)
        conn._commit();

#检查来自缓存中的设备对象和数据库中的设备对象是否一致
def sync_dev(key, dev, dev0, q, save_db=True, save_cache=True): #dev is in cache, dev0 is in db
    if (dev0.change_time is None):
        dirty_in_cache=True
    else:
        dirty_in_cache=dev0.change_time>dev.change_time
    print u"#检查是否有直接更新缓存的字段被改变, 有的话写入数据库"
    dirty_in_db=False
    for attr in ['log_stamp', 'last_activity', 'oplog_stamp', 'photo_stamp', 'fp_count', 'transaction_count', 'user_count', 'fw_version', 'ipaddress']:
        value=getattr(dev, attr) 
        if value != getattr(dev0, attr):
            if (attr in ['log_stamp', 'oplog_stamp', 'photo_stamp']) and (getattr(dev0, attr)=='0'): #手动重置的这些值
                dirty_in_cache=True
                setattr(dev0, attr, "1") #避免下次再认为是手动重置
                continue
            #print "%s:%s"%(attr, value)
            dirty_in_db=True
            try:
                setattr(dev0, attr, value)
            except:
                pass
    if dirty_in_db and save_db:
        #print "sync device %s to db"%dev0.sn
        dev0.save(force_update=True, log_msg=False)
    print u"#检查是否数据库中有字段被改变，有的话写入缓存"
    if dirty_in_cache:
        dirty_in_cache=False
        attrs=[isinstance(f, models.ForeignKey) and f.name+"_id" or f.name for f in Device._meta.fields]
        attrs.remove('change_time')
        for attr in attrs:
            try:
                value=getattr(dev0, attr)
                if value!=getattr(dev, attr):
                    #print "%s:%s"%(attr, value)
                    dirty_in_cache=True
                    setattr(dev, attr, value)
            except: pass
        if dirty_in_cache and save_cache:
            #print "sync device %s to cache"%dev.sn
            dev.change_time=dev0.change_time
            q.set(key, pickle.dumps(dev))
    return (dirty_in_cache, dirty_in_db)

def check_sync_devs(q): #定时同步缓存和数据库
    now=int(time.time())
    last=q.get("LAST_UPDATE_ICLOCK")   
#    if (last is None ) :        
#        q.set("LAST_UPDATE_ICLOCK", 0)
#        last=q.get("LAST_UPDATE_ICLOCK")
        
    if (last is None) or (last.strip()=="") or (now-int(last)>settings.SYNC_DEVICE_CACHE): #60秒同步到数据库
        #print "last=%s"%last
        sns=q.lrange("ICLOCKSET", 0, -1)
        dev_list=list(Device.objects.all())
        dev_list=dict([(d.sn, d) for d in dev_list]) #数据库中的设备列表

        for sn in sns:
            key="ICLOCK_%s"%sn
            dev=q.get(key)
            if not dev:
                continue
            try:
                dev=pickle.loads(dev)
                dev0=dev_list.get(sn, None)
                if dev0 is None:  
                    print u"#该设备 %s 已经不存在数据库中"%dev0
                    q.delete(key)
                    continue
                sync_dev(key, dev, dev0, q, True, True)
            except:
                print_exc()
        q.set("LAST_UPDATE_ICLOCK", str(now))

def check_and_save_cache(device, check_sync=True): #更新缓存中的设备信息
    #device.save()
    pass

#log_statement=devview_log_sql()    
#log_statement="""insert into %s (userid, checktime, checktype, verifycode, SN, WorkCode, Reserved,sn_name) \
#values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#
#log_statement_postgresql="""insert into %s (userid, checktime, checktype, verifycode, "SN", "WorkCode", "Reserved",sn_name) \
#values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table

def commit_log_(cursor, sql, cnn):
    #(pin, logtime, normal_state(flds[2]), normal_verify(flds[3]), device.sn, flds[4], flds[5])"
    sql_exc=""
    sql_exc=log_statement
    
    if type(sql)==type([]):
        """sqls="; ".join([log_statement%data for data in sql])
        try:
            cursor.execute("begin; "+sqls+"; end")
        except:
            print_exc()"""
        
        for data in sql: #sqlite3 数据库需要单次执行以减少 “Database is locked 错误”
            #print "data sql:%s     \n %s"%(log_statement,data)
            try:
                cursor.execute(sql_exc, data)
                #cnn._commit()
            except IntegrityError:
                raise IntegrityError
                pass
            except:
                import traceback;traceback.print_exc()

    elif type(sql)==type((0,)):
        cursor.execute(sql_exc, sql)
    else:
        cursor.execute(sql)
    if cnn: cnn._commit()


def commit_log(cursor, sql, cnn):
    try:
        commit_log_(cursor, sql, cnn)
    except IntegrityError:
        raise IntegrityError
    except:
        print_exc()
        print "try again"
        cnn._rollback()
        cnn.close()
        cursor=cnn.cursor()
        commit_log(cursor, sql, cnn)
    return cursor
   
def cdata_get_pin(request, device):
    resp=""
#    save = request.REQUEST.has_key('save') and (request.REQUEST['save'] in ['1', 'Y', 'y', 'yes', 'YES']) or False
    try:
        pin = request.REQUEST['PIN']
        emp = Employee.objects.get(PIN=format_pin(pin))
    except ObjectDoesNotExist:
        resp += "NONE"
    else:
        from base.crypt import encryption,decryption
        cc = u"DATA USER PIN=%s\tName=%s\tPasswd=%s\tGrp=%d\tCard=%s\tTZ=%s\tPri=%s\n" % (emp.pin(), emp.EName or "", decryption(emp.Password) or "", emp.AccGroup or 1, get_normal_card(emp.Card), emp.TimeZones or "", emp.Privilege or 0)
        for fp in Template.objects.filter(UserID=emp,Fpversion=device.Fpversion):
            try:
                cc += u"DATA FP PIN=%s\tFID=%d\tTMP=%s\n" % (emp.pin(), fp.FingerID, fp.temp())
            except:pass
        try:
            resp += cc.encode("gb18030")
        except:
            resp += cc.decode("utf-8").encode("gb18030")
#        if not save: # if not saved user in device, delete it after serveral(5) minutes
#            endTime = datetime.datetime.now() + datetime.timedelta(0, 5 * 60)
#            append_dev_cmd(device, "DATA DEL_USER PIN=%s" % emp.pin(), None, endTime)
    return resp

def cdata_get_options(device):
    resp = "GET OPTION FROM: %s\n" % device.sn
    resp += "Stamp=%s\n" % (device.log_stamp or 0)
    resp += "OpStamp=%s\n" % (device.oplog_stamp or 0)
    resp += "PhotoStamp=%s\n" % (device.photo_stamp or 0)
    resp += "ErrorDelay=%d\n" % max(30, settings.MIN_REQ_DELAY)
    resp += "Delay=%d\n" % max(settings.MIN_REQ_DELAY, device.delay)
    resp += "TransTimes=%s\n" % device.trans_times
    resp += "TransInterval=%d\n" % max(settings.MIN_TRANSINTERVAL, device.trans_interval)
    resp += "TransFlag=%s\n" % device.update_db
    if device.tz_adj is not None:
        resp += "TimeZone=%s\n" % device.tz_adj
    resp += "Realtime=%s\n" % ((settings.TRANS_REALTIME and device.realtime) and "1" or "0")
    resp += "Encrypt=%s\n\n" % (settings.ENCRYPT or device.encrypt)
    return resp

def cdata_post_trans(device, raw_data, head=None,old_head=None):
    cursor = conn.cursor()
    okc = 0;
    errorLines = [] #发生保存错误的记录
    cacheLines = [] #本次提交的行
    errorLogs = []  #解析出错、不正确数据的行
    sqls = []
    commitLineCount = 700 #达到700行就提交一次
    #if settings.DATABASE_ENGINE == "ado_mssql": commitLineCount = 50
    if settings.DATABASE_ENGINE == "sqlserver_ado": commitLineCount = 50
    alog = None
    for line in raw_data.splitlines():
        if line:
            eMsg = ""
            try:
                if head['Z']=='0':
                    log = line_to_log(device, line,False)
                else:
                    log = line_to_log(device, line)
            except Exception, e:  #行数据解析错误
                eMsg = u"%(mg)s" % {"mg":e.message}
                import traceback; traceback.print_exc();
                print eMsg
                log = None
            #print log
            if log:
                sqls.append(log)
                cacheLines.append(line) #先记住还没有提交数据，commit不成功的话可以知道哪些数据没有提交成功
                if len(cacheLines) >= commitLineCount: #达到一定的行就提交一次
                    try:
                        commit_log(cursor, sqls, conn)
                        okc += len(cacheLines)
                        if not alog:
                            alog = cacheLines[0]
                    except IntegrityError:
                        errorLines += cacheLines
                    except Exception, e:
                        print_exc()
                        print "try again"
                        
                        conn.close()
                        cursor = conn.cursor()
                        errorLines += cacheLines
                    cacheLines = []
                    sqls = []
            else:
                if not head['Z']=='0':
                    errorLogs.append("%s\t--%s" % (line, eMsg and eMsg or "Invalid Data"))
    if cacheLines: #有还没有提交的数据
        try:
            commit_log(cursor, sqls, conn)
            okc += len(cacheLines)
            if not alog:
                alog = cacheLines[0]
        except IntegrityError:
            errorLines += cacheLines
        except Exception, e:
            print_exc()
            print "try again"
            conn.close()
            cursor = conn.cursor()
            errorLines += cacheLines

    if errorLines: #重新保存上面提交失败的数据，每条记录提交一次，最小化失败记录数
        cacheLines = errorLines
        errorLines = []
        for line in cacheLines:
            if line not in errorLogs:
                try:
                    if head['Z']=='0':
                        log = line_to_log(device, line,False)
                    else:
                        log = line_to_log(device, line)
                    commit_log(cursor, log, conn)
                    if not alog: alog = cacheLines[0]
                    okc += 1
                except Exception, e:
                    pass
#                    estr = u"%s" % e
#                    if "database is locked" in estr:
#                        try:
#                            conn.close()
#                            cursor = conn.cursor()
#                            log = line_to_log(device, line, False)
#                            commit_log(cursor, log, conn)
#                            if not alog: alog = cacheLines[0]
#                            okc += 1
#                            estr = ""
#                        except Exception, ee:
#                            estr = u"%s" % ee
#                    elif ("UNIQUE KEY" in estr) or ("are not unique" in estr) or (
#                        "Duplicate entry" in estr):
#                        estr = "Duplicated"
#                    errorLines.append("%s\t--%s" % (line, estr))
    errorLines += errorLogs
    dlogObj = ""
    try:
        if okc == 1:
            dlogObj = alog
        elif okc > 1:
            dlogObj = alog + ", ..."
    except:pass
#    if errorLines:
#        #ErrNo:22 (invalid argument)的错误处理。
#        #出错的非重复记录，重新进入到后台处理队列
#        elinedata=[]
#        for el in errorLines:
#            if "Duplicated" not in el:
#                elinedata.append(el.split("\t--")[0])
#        if elinedata:
#            from mysite.iclock.models.model_cmmdata import gen_device_cmmdata    
#            obj=gen_device_cmmdata(device,old_head+"\n"+"\n".join(elinedata),"error")
#        
#        tmpFile("transaction_%s_%s.txt" % (device.sn, datetime.datetime.now().strftime("%Y%m%d%H%M%S")), "\n".join(errorLines))
    #print okc, len(raw_data.splitlines())
    return (okc, len(errorLines), dlogObj)

def cdata_post_userinfo(device, raw_data,Op, head=None):
    import time
    cursor = conn.cursor()
    c = 0;
    ec = 0;
    user = False
    for line in raw_data.splitlines():
        try:
            if line:
                user = line_to_emp(cursor, device, line,Op)
                c = c + 1
        except Exception, e:
            import traceback;traceback.print_exc()
            ec = ec + 1
            #appendFile("ERROR(cdata=%s):%s" % (line, e))
            if isinstance(e, DatabaseError):
                conn.close()
                cursor = conn.cursor()
        time.sleep(0.1)
    conn._commit()
    dlogObj = "TMP"
    try:
        dlogObj = u"%s" % user
    except: pass
    return (c, ec, dlogObj)

def cdata_post_fpimage(device, raw_data, head):
    pin, fid, image_file=(head['PIN'], head['FID'], head['FPImage'])
    fName = os.path.split(image_file)[1]
    fName = os.path.splitext(fName)
    save_model_file(Template, 
        "%s/%s/%s-%s%s" % (pin, fid, device.id, fName[0].split("_")[-1], fName[1]), 
        raw_data, "fpimage") 
    return "FP"

def write_data(raw_data, device=None,Op=None):
    
    head_data, raw_data=raw_data.split("\n",1)
    stamp_name, head=head_data.split(": ")
    stamp_name=stamp_name[1:]
    head=dict([item.split("=",1) for item in head.split("\t")])
    if device is None:
        device=get_device(head['SN'])
    msg=None
    c=0
    ec=0
    if stamp_name=='log_stamp':
        c, ec, msg=cdata_post_trans(device, raw_data, head,head_data)
    elif stamp_name=='oplog_stamp':
        c, ec, msg=cdata_post_userinfo(device, raw_data,Op, head)
    elif stamp_name=='FPImage':
        c=cdata_post_fpimage(device, raw_data, head)
    #写入上传记录日志表
    if msg is not None:
        try:
            DevLog(SN=device, Cnt=c, OP=stamp_name, ECnt=ec, Object=msg[:20], OpTime=datetime.datetime.now()).save(force_insert=True)
        except:
            print_exc()
    return (c, ec+c, msg)

TRANS_QUEQE='TRANS'
STAMPS={'Stamp':'log_stamp', 'OpStamp': 'oplog_stamp', 'FPImage':'FPImage', 'PhotoStamp':'photo_stamp'}




def cdata_post(request, device): 
    #print        request    
    raw_Data = request.raw_post_data
    #print "raw_Data:%s"%raw_Data
    #print request.META.items()
    if not raw_Data:
        raw_Data = request.META['raw_post_data']
    #print settings.ENCRYPT
    #logger.error(raw_Data)
    if settings.ENCRYPT:
        import lzo
        rawData = lzo.bufferDecrypt(raw_Data, device.sn)
    else:
        rawData = raw_Data

    ######################加入 后台验证信息
    try:
        Auty = request.REQUEST.get('AuthType', None)   
    except:
        Auty =None
    if Auty:
        from new_push import verification
        res = verification(Auty,rawData,device)
        return res

    stamp=None
    for s in STAMPS:
        stamp=request.REQUEST.get(s, None)
        if not (stamp is None):
            stamp_name=STAMPS[s]
            break
    if stamp is None:
        return "UNKNOWN"

    msg=None
    #print stamp_name
    if stamp_name=='FPImage': 
        head_data=":%s: SN=%s\tIP=%s\tTIME=%s\tPIN=%s\tFID=%s\tFPImage=%s\tZ=%s"%(stamp=='0' and stamp_name+'0' or stamp_name, str(device.sn).strip(),
            request.META["REMOTE_ADDR"], datetime.datetime.now(),
            request.REQUEST["PIN"], request.REQUEST.get("FID",0), request.REQUEST['FPImage'],stamp=='0' and '0' or '1')
    else:
        head_data=":%s: SN=%s\tIP=%s\tTIME=%s\tZ=%s"%(stamp_name, str(device.sn).strip(),
            request.META["REMOTE_ADDR"], datetime.datetime.now(),stamp=='0' and '0' or '1')
    try:
        #s_data="%s\n%s\n\n"%(head_data, rawData.decode(device.lng_encode))
        s_data="%s\n%s\n\n"%(head_data, rawData)
    except:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    #print "settings.WRITEDATA_CONNECTION:%s"%settings.WRITEDATA_CONNECTION
    if settings.WRITEDATA_CONNECTION>0:
        #写入到队列，后台进程在进行实际的数据库写入操作
        
        try:
            obj=""
            try:                
                from mysite.iclock.models.model_cmmdata import gen_device_cmmdata
                obj=gen_device_cmmdata(device,s_data)
            except Exception, e:
                raise 
#            try:
#                q_server=check_and_start_queqe_server()
#                q_server.lpush(DEVICE_POST_DATA, s_data)
#                q_server.connection.disconnect()
#            except Exception, e:
#                if obj:
#                    obj.delete()
#                raise
        except Exception, e:
            import traceback; traceback.print_exc()
            #raise 
            return "save post data error\n"
        c=1
    else:        
        c, lc, msg=write_data(s_data, device)
    if hasattr(device, stamp_name): setattr(device, stamp_name, stamp)
    device.save()
    return "OK:%s\n"%c

def device_response(msg=""): #生成标准的设备通信响应头
    response = HttpResponse(mimetype='text/plain')  #文本格式
    response["Pragma"]="no-cache"                   #不要缓存，避免任何缓存，包括http proxy的缓存
    response["Cache-Control"]="no-store"            #不要缓存
    if msg:
        response.write(msg)
    return response
#========================================消费机======================================
#消费机设备参数修改
def set_pos_options(request):
    from mysite.pos.pos_id.posdevview import set_options
    response = device_response()
    urlcon = request.build_absolute_uri()
    sn = request.REQUEST.get('SN')
    pos_write_log(urlcon,sn,None)
    if get_option("POS_ID"):
        resp = set_options(request)
    else:
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"当前类型设备不能消费")
        resp = resp.encode("GB18030")
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response

def pos_reback(request):#消费回滚
    from mysite.pos.pos_id.posdevview import reback
    urlcon = request.build_absolute_uri()
    sn = request.REQUEST.get('SN')
    cardno = request.REQUEST.get('card')
    pos_write_log(urlcon,sn,cardno)
    response = device_response()
    if get_option("POS_ID"):
        resp = reback(request)
    else:
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"当前类型设备不能消费")
        resp = resp.encode("GB18030")
    response["Content-Length"] = len(resp)
    cache.delete(cardno)
    response.write(resp)
    return response

def pos_getdata(request):#获取消费基本信息
    from mysite.pos.pos_id.posdevview import pos_data
    urlcon = request.build_absolute_uri()
    sn = request.REQUEST.get('SN')
    pos_write_log(urlcon,sn,None)
    response = device_response()
    if get_option("POS_ID"):
        resp = pos_data(request)
    else:
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"当前类型设备不能消费")
        resp = resp.encode("GB18030")
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response

def pos_getreq(request):#消费业务请求
    from mysite.pos.pos_id.posdevview import pos_getreq
    urlcon = request.build_absolute_uri()
    sn = request.REQUEST.get('SN')
    cardno = request.REQUEST.get('card')
    pos_write_log(urlcon,sn,cardno)
    response = device_response()
    if get_option("POS_ID"):
        resp = pos_getreq(request)
    else:
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"当前类型设备不能消费")
        resp = resp.encode("GB18030")
    response["Content-Length"] = len(resp)
    cache.delete(cardno)
    response.write(resp)
    return response

#===============================================================================================================
#设备读取配置信息、或者主动向服务器发送的数据
def cdata(request):
    encrypt = 1
    response = device_response()
    try:
        resp = ""
         #/****语言控制台数pwp start***/
        from mysite import authorize_fun
        language = request.REQUEST.get('language',None)
        device_type = request.REQUEST.get('device_type')#设备类型参数
        pos_device_type = request.REQUEST.get('device_type',None)#兼容ID消费固件，后期统一使用devicetype
        #根据传过来的语言设置settings中的机器台数
        authorize_fun.check_push_device(language, settings.AUTHORIZE_MAGIC_KEY)
        #print device_type,'=======deivce_type', device_type in ['ACP', 'ACD']
        #/****语言控制台数pwp end***/
        if(device_type == POSDEVICE or pos_device_type == POSDEVICE):#ID消费机
            from mysite.pos.pos_id.posdevview import pos_cdata
            if get_option("POS_ID"):
                resp += pos_cdata(request)
            else:#防止IC消费软件，连接ID消费机
                resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"当前类型设备为ID消费机")
                resp = resp.encode("GB18030")
        elif device_type in ['ACP', 'ACD']:#控制器or一体机
            from mysite.iaccess.push_comm_center import acc_cdata
            #print '====ininn___cdata-acc'
            resp += acc_cdata(request)
        else: 
            device = check_device(request, True)
            if device is None: 
                response.write("UNKNOWN DEVICE")
                return response

            if request.REQUEST.has_key('action'):
                resp += "OK\n"
            elif request.method == 'GET':
                if request.REQUEST.has_key('PIN'):
                    resp+=cdata_get_pin(request, device)
                else:
                    alg_ver="1.0"
                    if request.REQUEST.has_key('pushver'):
                        alg_ver=request.REQUEST.get('pushver')    #2010-8-25  device字段alg_ver用来区分新老固件  >=2.0为新固件，默认为旧固件
                    device.alg_ver=alg_ver
                    device.save()
                    resp+=cdata_get_options(device)
                    encrypt = 0
            elif request.method == 'POST':
                try:
                    resp+=cdata_post(request, device)
                except Exception, e:
                    resp = u"ERROR: %s" % e
                    #errorLog(request)
            else:
                resp += "UNKOWN DATA\n"
                resp += "POST from: " + device.sn + "\n"
            check_and_save_cache(device)
    except  Exception, e:
        print '=====error_--cdata'
        from traceback import print_exc
        print_exc()
        #errorLog(request)
        resp = u"%s" % e
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response


from mysite.iclock.cache_cmds import update_and_load_cmds,check_pre_request \
        ,get_pre_request_cmds,get_request_cmds,update_start_end_index,get_prev_save_time \
        ,save_last_activity


#设备读取命令
def getreq(request):
    response = device_response()
    try:
        resp = ""
        device = check_device(request)
        
        if device is None: 
            response.write("UNKNOWN DEVICE")
            return response
        update_and_load_cmds(device) #如果命令全部执行完，更新缓存命令到数据库，重新加载新的命令到缓存
        info = request.GET.get("INFO", "") #版本号，用户数,指纹数,记录数,设备自身IP地址
        
        if info:
            sql=[]
            info = info.split(",")
            device.fw_version=info[0]
            device.user_count=int(info[1])
            device.fp_count=int(info[2])
            device.transaction_count=int(info[3])
#            sql.append("fw_version='%s'"%info[0])
#            sql.append("user_count='%s'"%info[1])
#            sql.append("fp_count='%s'"%info[2])
#            sql.append("transaction_count='%s'"%info[3])
            
            if len(info)>4:
                device.ipaddress=info[4]
                if device.alias=="auto_add":
                    device.alias=info[4]#由于网关问题，使名称对应的IP地址与机器IP不同时的更正。
#                sql.append("ipaddress='%s'"%info[4])
#                sql.append("alias='%s'"%info[4])
            if len(info)>5:             
                device.Fpversion=info[5]   #新版本支持INFO时，算法版本提交
                #sql.append("Fpversion='%s'"%info[5])
            #device=update_device_sql(",".join(sql),device.sn)
            try:
                device.face_count=int(info[8])
                device.face_tmp_count=int(info[7])
                device.face_ver=info[6]
                if device.face_ver!='5' and device.face_ver!='7':
                    device.face_ver=''
            except:
                pass
            try:
                device.push_status='1'+info[9]+ '0'*6
            except:
                pass 
            device.save()
            
        # 自动升级固件功能
        if not hasattr(device, "is_updating_fw"): #该设备现在没有正升级固件
            fw = fwVerStd(device.fw_version) 
            if fw: #该设备具有固件版本号
                up_version=device.get_std_fw_version() #用于升级的设备固件标准版本号
                if up_version>fw:   #该设备固件版本号较低
                    n=int(q_server.get_from_file("UPGRADE_FW_COUNT") or "0")
                    if n < settings.MAX_UPDATE_COUNT: #没有超出许可同时升级固件的范围
                        #升级固件
                        errMsg = dev_update_firmware(device)
                        if not errMsg: 
                            device.is_updating_fw=device.last_activity
                        if errMsg: #升级命令错
                            appendFile((u"%s UPGRADE FW %s:%s" % (device.sn, fw, errMsg)))
                        else:
                            q_server.incr("UPGRADE_FW_COUNT")
        
        
        devcmds = []
        flag_new = False #是否是下发新的命令
        check_ret = check_pre_request(device)#确认上次下发命令，机器是否成功接收到
        if not check_ret:
            devcmds = get_pre_request_cmds(device) #返回上一次下发的命令
        else:
            flag_new = True
            devcmds = get_request_cmds(device)
        
        c=0
        
        maxRet = device.max_comm_count
        maxRetSize = device.max_comm_size * 1024
             
        while devcmds:
            cmd_key = devcmds.pop(0)
            obj_cmd=cache.get(cmd_key)
            cmd_return = obj_cmd.CmdReturn
            
            if settings.GETREQ_THREE_TIMES:#兼容固件不确认的bug
                if not cmd_return:
                    cmd_return = -99996
                else:
                    cmd_return = int(cmd_return) -1
            
            CmdContent=obj_cmd.CmdContent
            if CmdContent.find("DATA UPDATE user")==0 or CmdContent.find("SMS ")==0 or CmdContent.find("DATA UPDATE SMS")==0 : #传送用户命令,需要解码成GB2312
                cc=CmdContent
                try:
                    cc=cc.encode("gb18030")
                except:
                    try:
                        cc=cc.decode("utf-8").encode("gb18030")
                    except:
                        import traceback;traceback.print_exc()
                        pass
                        #errorLog(request)
            else:                    
                cc=str(CmdContent)

            nowcmd=str(cc)
            cc=std_cmd_convert(cc, device)
            if cc: resp+="C:%d:%s\n"%(obj_cmd.id,cc)

            c=c+1
            
            if settings.GETREQ_THREE_TIMES:#兼容固件bug
                obj_cmd.CmdReturn = cmd_return
                
            obj_cmd.CmdTransTime=datetime.datetime.now()
            update_cached_cmd(obj_cmd)
            
            if (c>=maxRet) or (len(resp)>=maxRetSize): break;     #达到了最大命令数或最大命令长度限制
            if CmdContent in ["CHECK","CLEAR DATA","REBOOT", "RESTART"]: break; #重新启动命令只能是最后一条指令  #增加查找到CHECK指令后，直接发送


        if c == 0:#没有发送任何命令时，简单向设备返回 "OK" 即可
            resp += "OK"
        else:
            if flag_new:
                update_start_end_index(device,c) #更新下发命令的起始和结束为止
            
        dt_now = datetime.datetime.now()
        device.last_activity = dt_now
        device.cache_device()

        prev_save_time = get_prev_save_time(device)

        if (dt_now -prev_save_time).seconds>300: #五分钟保存一次
            device.save(log_msg = False)
            save_last_activity(device)


        
    except  Exception, e:
        import traceback;traceback.print_exc()
        resp = u"%s" % e
        #errorLog(request)
    if settings.ENCRYPT:
        import lzo
        resp = lzo.bufferEncrypt(resp + "\n", device.sn)
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response


def get_value_from(data, key):
    for l in data:
        if l.find(key + "=") == 0:
            return l[len(key) + 1:]
    return ""

def parse_dev_info(device, pdata): #把设备上传的options.cfg等内容解析成设备对象的各个字段, 更新设备对象信息
    info_list = {
        'FWVersion':"fw_version", 
        'FPCount':"fp_count", 
        'TransactionCount':"transaction_count", 
        'UserCount':"user_count", 
        'MainTime':"main_time", 
        '~MaxFingerCount':"max_finger_count", 
        '~LockFunOn':"lockfun_on",
        '~MaxAttLogCount':"max_attlog_count", 
        '~DeviceName':"device_name", 
        #'~AlgVer':"alg_ver", 
        'FlashSize':"flash_size", 
        'FreeFlashSize':"free_flash_size", 
        'Language':"language",
        #'VOLUME':"valume", 
        'DtFmt':"dt_fmt", 
        'IPAddress':"ipaddress", 
        'IsTFT':"is_tft", 
        '~Platform':"platform", 
        'Brightness':"brightness", 
        '~OEMVendor':"oem_vendor",
        '~ZKFPVersion':"Fpversion",
    }
    pd = dict([ line.split("=",1) for line in pdata.splitlines() if line.find("=")>0 ])
    for k,v in pd.items():
        if k in info_list:
            try:
                value=device.__getattribute__(info_list[k])
                if value!=v:
                    device.__setattr__(info_list[k], v)
            except:
                print_exc()
    if device.platform and device.platform.find("TFT")>0:
        device.is_tft=1
    #设备的别名是IP地址的话，自动更新
    if IP4_RE.search(device.alias) and IP4_RE.search(device.ipaddress):
        device.alias = device.ipaddress

def check_upgrade_fw(device, cmdobj):
    if cmdobj.CmdContent.find("PutFile file/fw/") == 0 and cmdobj.CmdContent.find("main.") > 0: #it is an upgrade firmware command
        if hasattr(device, "is_updating_fw"): del device.is_updating_fw
        url, fname = getFW(device)
        q_server=check_and_start_queqe_server()
        q_server.decr("UPGRADE_FW_COUNT")
        diff = int(cmdobj.CmdReturn)-os.path.getsize(fname) #返回的文件字节数和实际的文件字节数比较
        if diff in [0, 1]: #升级成功, 有一旧版本的固件下载文件后会多出一个字节
            fname=os.path.split(fname)[1]
            if cmdobj.CmdContent.find("%s.tmp"%fname) > 0: #如果是下载固件到临时文件的话需要改名
                append_dev_cmd(device, "Shell mv %s.tmp /mnt/mtdblock/%s"%(fname, fname))
            append_dev_cmd(device, "REBOOT") #重新启动机器
        else:
            append_dev_cmd(device, cmdobj.CmdContent) #重新失败，重新发送升级命令
        q_server.connection.disconnect()

def check_upload_file(request, data):
    d = request.raw_post_data
    index = d.find("Content=")
    if not index: return
    d = d[index + 8:]
    if not d: return
    try:
        fname = data['FILENAME']
    except:
        fname = ""
    if not fname: return
    save_model_file(Device, "%s/%s-%s"%(data["SN"], fname, data['ID']), 
        d, "upload_file")
    
def check_att_sum(data,device):
#    try:
    from django.db.models import Q
    from mysite.iclock.models import Transaction
    from mysite.iclock.models.device_extend import create_att_cmd
    StartTime = data['StartTime']
    EndTime = data['EndTime']
    AttlogSum = int(data['AttlogCount'])
    q = {'TTime__gte':StartTime,'TTime__lte':EndTime,'SN':device}
    count = len(Transaction.objects.filter(Q(**q)))
    if AttlogSum!=count:
        create_att_cmd(device,StartTime,EndTime,1)
#    except:
#        pass 

def check_upgradefile(id,data,device,ret):
#    try:
    from mysite.iclock.cache_cmds import get_cached_cmd,update_cached_cmd
    import os
    cmdobj = get_cached_cmd(id)
    if not cmdobj:
        flag =  False
    if cmdobj.SN_id!=device.id: 
        print u"ERROR: 命令对应的设备与指定设备不一致(%s != %s)"%(cmdobj.SN_id, device.id)
        flag = False
    content = str(cmdobj.CmdContent)
    path = content.split(' ')[1].split('\t')[0].replace('file/',settings.ADDITION_FILE_ROOT)
    if os.path.exists(path):
        size_f = os.path.getsize(path)
        if size_f ==long(ret):
            flag = True
        else: 
            flag = False
    else:
        flag = False
    cmdobj.CmdOverTime=datetime.datetime.now()
    if ret==0:ret=-1
    if flag:
        ret = '0'
    cmdobj.CmdReturn=ret#flag and 0 or ret
    update_cached_cmd(cmdobj)#更新命令到缓存
    cmdobj.SN=device
#    except:
#        pass 

def response_str(response, str):
    response["Content-Length"] = len(str)
    response.write(str)
    return response

def parse_a_post(data, split):
    p = {}
    ditems = data.split(split)
    for i in range(len(ditems)):
        if not ditems[i]: continue
#                print ditems[i]
        k = ditems[i].split("=", 1)
        if k[0] == 'Content':
            p['Content'] = k[1] + split + split.join(ditems[i + 1:])
            break;
        elif ditems[i].find("CMD=INFO") >= 0:
            p['CMD'] = "INFO"
            p['Content'] = split.join(ditems[i + 1:])
            break;
        elif len(k) == 2:
            p[k[0]] = k[1]
    return p

def parse_posts(data):
    posts = []
    lines = data.split("\n")
    if len(lines) == 0: return posts
    firstline = lines[0].split("&")
    if len(firstline) < 2: #just a posts
        return [parse_a_post(data, "\n")]
    if "CMD=INFO" in firstline:
        d = parse_a_post(lines[0], "&")
        d['CMD'] = "INFO"
        d['Content'] = "\n".join(lines[1:])
        return [d]
    for l in lines:
        if l:
            posts.append(parse_a_post(l, "&"))
    return posts

from mysite.iclock.cache_cmds import update_cached_cmd,get_cached_cmd,post_check_update
def update_cmd(device, id, ret, q_server=None):
    
    cmdobj = get_cached_cmd(id)
    if not cmdobj:
        return None
    if cmdobj.SN_id!=device.id: 
        print u"ERROR: 命令对应的设备与指定设备不一致(%s != %s)"%(cmdobj.SN_id, device.id)
        return None
    cmdobj.CmdOverTime=datetime.datetime.now()
    cmdobj.CmdReturn=ret
    update_cached_cmd(cmdobj)#更新命令到缓存
    cmdobj.SN=device
    return cmdobj

def update_cmds(device, rets):
    post_check_update(device,rets)#更新下发命令，起始结束标示
    for id in rets:
        update_cmd(device, id, rets[id],None)
            
def  save_dev_info(device, apost):
    #print "save_dev_info:%s"%apost
    option=apost.split("\n")
    #print "optoin:%s"%option
    opt={}
    for p in option:
        if p.find("=")>0:
            opt[p.split("=")[0]]=p.split("=")[1]
    #print "opt:%s"opt
    if opt.has_key('~ZKFPVersion'):    #指纹识别算法版本
        device.Fpversion=opt['~ZKFPVersion']    
    if opt.has_key('~DeviceName'):
        device.device_name=opt['~DeviceName'] 
    if opt.has_key('UserCount'):
        device.user_count=opt['UserCount']
    if opt.has_key('FPCount'):
        device.fp_count=opt['FPCount']        
    if opt.has_key('TransactionCount'):
        device.transaction_count=opt['TransactionCount']    
    device.save()


#设备返回数据
def devpost(request):
    response = device_response()
    resp = ""
    device = check_device(request)
    if device is None: 
        response.write("UNKNOWN DEVICE")
        return response
    try:
        rd = request.raw_post_data
        if settings.ENCRYPT:
            try:
                import lzo
                rawData = lzo.bufferDecrypt(rd, device.sn)
            except:
                rawData = rd
        else:
            rawData = rd
        try:
            data0 = rawData.decode("gb18030")
        except:
            data0 = rawData
        rets = {}
        pdata = parse_posts(data0)
        #print "ppost:%s"%pdata
        for apost in pdata:
            id = int(apost["ID"])
            ret = apost["Return"]
            if apost["CMD"] == "INFO":
                #save_dev_info(device, apost['Content'])
                
                parse_dev_info(device, apost['Content'])
                device.save()
                rets[id] = ret
            elif (apost["CMD"] == "GetFile" or apost["CMD"] == "Shell") and ret > 0:
                check_upload_file(request, apost)
                rets[id] = ret
            elif apost["CMD"] == "VERIFY SUM" and ret > 0:
                check_att_sum(apost,device)
                rets[id] = ret
            elif apost["CMD"] == "PutFile":
                check_upgradefile(id,apost,device,ret)
                post_check_update(device,[ret])
                #rets[id] = ret
            else:
                rets[id] = ret
        if len(rets) > 0:
            update_cmds(device, rets)
        resp += "OK"
        #check_and_save_cache(device)
        
    except:
        pass
        #errorLog(request)
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response

# Photo
#        /iclock/fdata?SN=88888888&PIN=20081119172119-4.jpg&PhotoStamp=285528079

def post_photo(request):
    response = device_response()
    device = check_device(request)
    if device is None: 
        response.write("UNKNOWN DEVICE")
        return response
    try:
        pin = request.REQUEST.get("PIN","")
        
        pin = pin.split(".")[0].split("-")
        dt = pin[0]
        if len(pin) == 2: #Success Picture
            pin = pin[1]
        else:
            pin = ""
        d = request.raw_post_data
        if "CMD=uploadphoto" in d: d = d.split("CMD=uploadphoto")[1][1:]
        if "CMD=realupload" in d: d = d.split("CMD=realupload")[1][1:]
        if len(d)>0:
            save_model_file(Transaction,
            "%s/%s/%s" % (device.sn, dt[:4], dt[4:8])+"/"+ pin+"_"+ dt[8:] + ".jpg", 
            d, "picture")
        else:
            response.write("No photo data!\n")
            return response
            
        if request.REQUEST.has_key('PhotoStamp'):
            DevLog(SN=device, Cnt=1, OP=u"PICTURE", Object=pin, OpTime=datetime.datetime.now()).save()
            device.photo_stamp = request.REQUEST['PhotoStamp']
            device.save()
            
        #check_and_save_cache(device)
    except:
        pass
        #errorLog(request)
    response.write("OK\n")
    return response


#def pre_save_device(sender, instance, **kwargs):
#    key = "ICLOCK_%s"%instance.sn
#    q_server = check_and_start_queqe_server()
#    device = q_server.get_from_file(key)
#    if device:
#        try:
#            device = pickle.loads(device)
#        except:
#            device = None
#    if device:
#        new_c, new_db=sync_dev(key, device, instance, q, False, True) 
#        if new_c:
#            append_dev_cmd(device, "CHECK")
#
#from django.db.models.signals import pre_save
#pre_save.connect(pre_save_device, sender=Device)
#
#from django.db.models.signals import pre_save
#pre_save.connect(pre_save_device, sender=Device)

#from django.db.models.signals import pre_save
#pre_save.connect(pre_save_device, sender=Device)
#
