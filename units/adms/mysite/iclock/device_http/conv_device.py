# coding=utf-8
from mysite.iclock.models import  OpLog,Device
from django.conf import settings
import datetime
import time
from base.cached_model import STATUS_PAUSED, STATUS_STOP
from db_utils import append_dev_cmd
from django.core.exceptions import ObjectDoesNotExist

from commen_utils import server_time_delta

try:
    import cPickle as pickle
except:
    import pickle

def line_to_oplog(cursor, device, flds, event=True):
    '''
    处理设备操作日志数据
    '''
    try: #0        0        2008-08-28 14:07:37        0        0        0        0
        flds = flds.split("\t")
        try:
            logtime = datetime.datetime.strptime(flds[2], "%Y-%m-%d %H:%M:%S")
        except:
            return None
        if (datetime.datetime.now() + datetime.timedelta(1, 0, 0)) < logtime: #时间比当前时间还要多一天
            return None
        if device.TZAdj <> None:
            logtime = logtime-datetime.timedelta(0, device.TZAdj * 60 * 60) + server_time_delta() #UTC TIME, then server time
        obj = OpLog(SN=device, admin=flds[1], OP=flds[0], OPTime=logtime,
                    Object=flds[3], Param1=flds[4], Param2=flds[5], Param3=flds[6])
        obj.save()
    except:
        return None
    
def update_device_sql(sql,sn):
    from commen_utils import excsql
    from mysite.iclock.sql import update_device_sql_sql
    tsql=update_device_sql_sql(sql,sn)
    excsql(tsql)
    device=Device.objects.filter(sn=sn)[0]
    return device


def get_device(sn):
    '''
    根据设备sn找对应的设备对象
    '''
    from cmds_api import get_device_raise
    return get_device_raise(sn)

#    device=Device.objects.filter(sn=sn)
#    if device:
#        return device[0]
#    else:   #---请求服务器的设备没有登记过 
#        raise ObjectDoesNotExist
    
def check_device(request, allow_create=True):
    '''
    根据设备的http请求 检查设备的注册情况返回有效设备对象
    涉及http参数 HITACDMFun、SN、device_type
    '''
#    try:    #---参数 HITACDMFun 必须为 ['HIT','HIT Corporation','iCON','Rentris','Secure'] 成员
#        re_device =  request.GET["HITACDMFun"]
#        if re_device:
#            if re_device not in ['HIT','HIT Corporation','iCON','Rentris','Secure']:
#                return None
#        else:
#            return None
#    except:
#        return None
    from cmds_api import check_and_init_cmds_cache
    from protocol_content import POSDEVICE
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
    try:
        device=get_device(sn)
    except ObjectDoesNotExist: #---正在请求服务器的设备没有登记过
        from mysite.utils import get_option 
        if get_option("ATT") and allow_create and not request.REQUEST.has_key('PIN') and ( #没有查询用户信息的话，可以注册该考勤机 
            len(sn) >= 6 and settings.ICLOCK_AUTO_REG): #若SN正确，且设置可以自动注册
            from mysite.personnel.models.model_area import Area
            device = Device(
                sn=sn, 
                alias="auto_add",   #---设备别名
                last_activity=datetime.datetime.now(), 
                area=Area.objects.get(pk=1),#Area.objects.all()[0], #---默认设在第一个考勤区域
                ipaddress=request.META["REMOTE_ADDR"])
            device.save(force_insert=True, log_msg=False)
            append_dev_cmd(device, "INFO")  #---添加设备请求命令 定义此为 INFO 操作
        else:
            return None
    if device.status in (STATUS_STOP, STATUS_PAUSED):   #--- 设备处于暂停或者停止状态
        return None
    check_and_init_cmds_cache(device) #检查缓存命令结构是否存在，如果不存在初始化缓存命令结构
    device.last_activity=datetime.datetime.now()
    deviceType = request.REQUEST.get('device_type')
    if(deviceType==POSDEVICE):#消费机
        device.deviceType = POSDEVICE
    else:
        device.deviceType = ""
    return device

def sync_dev(key, dev, dev0, q, save_db=True, save_cache=True): #dev is in cache, dev0 is in db
    '''
    检查来自缓存中的设备对象和数据库中的设备对象是否一致
    '''
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
            dirty_in_db=True
            try:
                setattr(dev0, attr, value)
            except:
                pass
    if dirty_in_db and save_db:
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
                    dirty_in_cache=True
                    setattr(dev, attr, value)
            except: pass
        if dirty_in_cache and save_cache:
            dev.change_time=dev0.change_time
            q.set(key, pickle.dumps(dev))
    return (dirty_in_cache, dirty_in_db)

def check_sync_devs(q): #---定时同步缓存和数据库    [没有被任何地方使用]
    now=int(time.time())
    last=q.get("LAST_UPDATE_ICLOCK")   
    if (last is None) or (last.strip()=="") or (now-int(last)>settings.SYNC_DEVICE_CACHE): #60秒同步到数据库
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
                import traceback; traceback.print_exc()
        q.set("LAST_UPDATE_ICLOCK", str(now))
        
def check_and_save_cache(device, check_sync=True): 
    '''
    更新缓存中的设备信息
    '''
    pass

def cdata_get_options(device):
    '''
    返回设备相关的其他一些配置信息
    '''
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

def parse_dev_info(device, pdata):
    '''
    把设备上传的options.cfg等内容解析成设备对象的各个字段, 更新设备对象信息
    处理设备信息相关的命令字符串
    '''
    from constant import IP4_RE
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
        'FlashSize':"flash_size", 
        'FreeFlashSize':"free_flash_size", 
        'Language':"language",
        'DtFmt':"dt_fmt", 
        'IPAddress':"ipaddress", 
        'IsTFT':"is_tft", 
        '~Platform':"platform", 
        'Brightness':"brightness", 
        '~OEMVendor':"oem_vendor",
        '~ZKFPVersion':"Fpversion",
        '~IsOnlyRFMachine':"only_RFMachine",
    }
    pd = dict([ line.split("=",1) for line in pdata.splitlines() if line.find("=")>0 ])
    for k,v in pd.items():
        if k in info_list:
            try:
                value=device.__getattribute__(info_list[k])
                if value!=v:
                    device.__setattr__(info_list[k], v)
            except:
                import traceback; traceback.print_exc()
    if device.platform and device.platform.find("TFT")>0:
        device.is_tft=1
    #设备的别名是IP地址的话，自动更新
    if IP4_RE.search(device.alias) and IP4_RE.search(device.ipaddress):
        device.alias = device.ipaddress
    print 'leaving from parse_dev_info'
        
#def  save_dev_info(device, apost):
#    option=apost.split("\n")
#    opt={}
#    for p in option:
#        if p.find("=")>0:
#            opt[p.split("=")[0]]=p.split("=")[1]
#    if opt.has_key('~ZKFPVersion'):    #指纹识别算法版本
#        device.Fpversion=opt['~ZKFPVersion']    
#    if opt.has_key('~DeviceName'):
#        device.device_name=opt['~DeviceName'] 
#    if opt.has_key('UserCount'):
#        device.user_count=opt['UserCount']
#    if opt.has_key('FPCount'):
#        device.fp_count=opt['FPCount']        
#    if opt.has_key('TransactionCount'):
#        device.transaction_count=opt['TransactionCount']    
#    device.save()

def deal_pushver(request,device):
    '''
    更新设备push版本
    '''
    alg_ver="1.0"
    if request.REQUEST.has_key('pushver'):
        alg_ver=request.REQUEST.get('pushver')    #device字段alg_ver用来区分新老固件  >=2.0为新固件，默认为旧固件
    device.alg_ver=alg_ver
    device.save()