# coding=utf-8
import datetime
from hashlib import md5


from django.conf import settings

from commen_utils import server_time_delta

STATUS_PAUSED, STATUS_STOP = 2,3
MIN_REQ_DELAY = 60
MIN_TRANSINTERVAL=2 #最小传输数据间隔时间(分钟）
TRANS_REALTIME=1        #设备是否实时上传记录
ENCRYPT=0

time_fmt = "%Y-%m-%d %H:%M:%S"

from db_utils import append_dev_cmd

from sync_models import Device,ObjectDoesNotExist 
from commen_utils import create_logger

try:
    import cPickle as pickle
except:
    import pickle
    
    
''' 设备管理员操作日志 '''
log_op = create_logger(settings.APP_HOME+"/tmp/dev_op.log")

def Check_ClientCode(code, SN): 
    m = md5()
    m.update(code + SN)
    return m.hexdigest()

def line_to_oplog(device, flds):
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
        log_op.info("%s %s %s at %s on %s with [%s, %s, %s]"%(flds[1],flds[0],flds[3], logtime,device.sn,flds[4],flds[5],flds[6]))
        return True
    except:
        return None
    
def check_device(request, allow_create=True,commkey_check=False):
    '''
    根据设备的http请求 检查设备的注册情况返回有效设备对象, 当为新设备时会触发set()
    涉及http参数 HITACDMFun、SN、device_type
    device 属性 
    '''
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
    device=Device(sn)
    try:
        device=device.get()
    except ObjectDoesNotExist: #---设备没有登记过
        if request.method == 'GET' and commkey_check:
            from mysite import authorize_fun
            language=request.REQUEST.get('language',None)   #---获得语言参数
            authorize_fun.check_push_device(language, settings.AUTHORIZE_MAGIC_KEY)   #---连接设备数量控制

        
        if allow_create and not request.REQUEST.has_key('PIN') and len(sn) >= 6: #若SN正确，且设置可以自动注册
            device.alias = 'auto_add'
            device.ipaddress = request.META["REMOTE_ADDR"]
            device.status = 1
            str_now = datetime.datetime.now().strftime(time_fmt)
            device.last_activity = str_now
        else:
            return None

    if request.method == 'GET' and commkey_check:
        from constant import PUSH_COMM_KEY_CHECK
        if PUSH_COMM_KEY_CHECK:
            pushcommkey = request.GET.get("pushcommkey",None)
            if not pushcommkey:
                raise  Exception('hase no pushcommkey param.')
                return None
            dec = Check_ClientCode(sn, settings.CUSTOMER_CODE)
            if dec!=pushcommkey:
                raise  Exception('pushcommkey authentication failed.')
                return None

    if device.status in (STATUS_STOP, STATUS_PAUSED):   #--- 设备处于暂停或者停止状态
        return None
    if device.isnew():
        deviceType = request.REQUEST.get('device_type')
        if(deviceType=='30'):#消费机
            device.deviceType = '30'
        else:
            device.deviceType = ''
        ck_ret = check_count(int(device.total()))
        if ck_ret:
            print ck_ret
            return None
        device.set_area(1)#设置默认区域
        device.set()
    else:
        device.last_activity = datetime.datetime.now().strftime(time_fmt)
        device.set('last_activity')# 更新设备最后访问时间
    return device

def check_count(num):
    from mysite.authorize_fun import get_cache
    from django.core.cache import cache
    from mysite.iclock.models import Device
    zkeco_count = get_cache("ZKECO_DEVICE_LIMIT")
    zktime_count = get_cache("ATT_DEVICE_LIMIT")
    all_dev_count=Device.objects.all().count()
    if num<zktime_count or all_dev_count<zkeco_count:
        return 0
    else:
        return u'已超过允许的设备数目'
    
def parse_dev_info(device, pdata):
    '''
    把设备上传的options.cfg等内容解析成设备对象的各个字段, 更新设备对象信息, 会触发set()
    处理设备信息相关的命令字符串
    '''
    from constant import DEVELOP_MODEL
    if DEVELOP_MODEL:print 'going  to parse_dev_info......'
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
                value=getattr(device,info_list[k])#device.__getattribute__(info_list[k])
                if value!=v:
                    setattr(device,info_list[k],v)
            except:
                import traceback; traceback.print_exc()
    if device.platform and device.platform.find("TFT")>0:
        device.is_tft=1
    #设备的别名是IP地址的话，自动更新
    if IP4_RE.search(device.alias) and IP4_RE.search(device.ipaddress):
        device.alias = device.ipaddress
    device.set()
        