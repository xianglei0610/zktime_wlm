# -*- coding: utf-8 -*-
import datetime
import time
import os
from dbapp.utils import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections, IntegrityError, DatabaseError, models
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
#from dataprocaction import append_dev_cmd
from base.cached_model import STATUS_PAUSED, STATUS_STOP
from traceback import print_exc
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _

from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
from mysite.pos.models.model_carcashsz import CarCashSZ
from mysite.pos.models.model_cardcashszbak import CarCashSZBak
from mysite.pos.models.model_timeslice import TimeSlice
from mysite.pos.models.model_splittime import SplitTime
from mysite.pos.models.model_carcashtype import CarCashType
from mysite.pos.models.model_merchandise import Merchandise
from mysite.pos.models.model_keyvalue import KeyValue
from mysite.pos.models.model_batchtime import BatchTime
from mysite.pos.models.model_cardmanage import CardManage
from mysite.pos.models.model_errors import Errors
from decimal import Decimal
from mysite.pos.models.model_timebrush import TimeBrush
from django.db import transaction
from django.core.cache import cache
from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_VALID,CARD_STOP,CARD_OVERDUE,CARD_LOST,POS_CARD
from mysite.pos.pos_constant import TIMEOUT
from mysite.personnel.models.model_emp import Employee,getuserinfo
from mysite.pos.models.model_loseunitecard import LoseUniteCard

from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
from mysite.iclock.dataprocaction import append_dev_cmd
from mysite.pos.models.model_icconsumerlist import ICConsumerList
from mysite.pos.models.model_icconsumerlistbak import ICConsumerListBak
from mysite.iclock.models.model_devlog import DevLog
from mysite.iclock.cmdconvert import std_cmd_convert
from decimal import Decimal
from mysite.pos.pos_ic.ic_cache_cmds import update_cached_cmd,get_cached_cmd,post_check_update
from mysite.pos.models.model_storedetail import StoreDetail
from mysite.pos.models.model_keydetail import KeyDetail
from mysite.pos.models.model_timedetail import TimeDetail
from mysite.iclock.constant import IP4_RE
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE
from mysite.pos.pos_ic.ic_sync_model import Pos_Device
from mysite.pos.pos_ic.ic_sync_action import init_ic_pos_device
from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
conn = connections['default']
DEVICE_POS_IC = 5
MONEY_MODEL = 2 #金额模式
POS_DEVICE = 0 #消费机
ALLOWANCE_DEVICE = 1#补贴机
TELLER_DEVICE = 2#出纳机

IC_CARD_LOST = '2'#挂失
CARD_REVERT = '3'#解挂
CHANGE_PWD_OK = '5' #修改密码成功
IS_CHANGE_PWD = '4' #是否可以修改

LOGTYPE={'pos_log_stamp':'6',#消费
         'full_log_stamp': '1', #充值
         'allow_log_stamp':'2',
         'pos_log_bak_stamp':'6',
         'full_log_bak_stamp':'1',
         'allow_log_bak_stamp':'2', }#补贴
        
DEVICE_CMD =["CHECK OPTION",
"SET OPTION",
"CLEAR DATA",
"CHECK FULLLOG",
"CHECK POSLOG",
"CHECK ALLOWLOG",
"CHECK ALL",
"RELOAD OPTIONS",
"REBOOT",
"RESTART",
"CLEAR POSLOG",
"CLEAR FULLVALUE",
"CLEAR SIDYLOG",
]

import logging
def pos_write_log(str,sn):
    import codecs,os,sys
    if settings.DEBUG:
        try:
            dt=datetime.datetime.now()
            path=settings.APP_HOME.replace('\\','/') + '/tmp/zkpos/poslog/'
            if not os.path.exists(path):
                os.makedirs(path)
            mfile=path+'poslog_%s_%s.txt'%(datetime.datetime.now().strftime("%Y-%m-%d"),sn)
            f=codecs.open(mfile,'a','utf-8')
            wstr='RESPONSE-%s-%s\r\n'%(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f"),str)
            f.write(wstr)
            f.close()
        except:
            f.close()
            pass

logger = logging.getLogger()
hdlr = logging.FileHandler(settings.APP_HOME+"/tmp/pos_dev_post.log")
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)


#根据设备sn找对应的设备对象, 若有request,则进行自动注册该设备
def get_device(sn):
    from mysite.iclock.cache_cmds import get_device_raise
    return get_device_raise(sn)

def get_redis_device(device):
    r_device = Pos_Device(device.sn)
    response = device_response()
    try:
        pos_device=r_device.get()
        return pos_device
    except PosDeviceDoesNotExist:
        init_ic_pos_device(device)
        pos_device=r_device.get()
        return pos_device
    
def device_response(msg=""): #生成标准的设备通信响应头
    response = HttpResponse(mimetype='text/plain')  #文本格式
    response["Pragma"]="no-cache"                   #不要缓存，避免任何缓存，包括http proxy的缓存
    response["Cache-Control"]="no-store"            #不要缓存
    if msg:
        response.write(msg)
    return response

#根据设备http请求找对应的消费设备对象
def check_pos_device(request, allow_create=False):
    from mysite.iclock.cache_cmds import check_and_init_cmds_cache
    from mysite.utils import get_option 
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
    try:
        device=get_device(sn)
    except ObjectDoesNotExist: #正在请求的设备没有登记过
        from mysite.iclock.models.model_dininghall import Dininghall
        if  allow_create and get_option("POS_IC") and ( 
            len(sn) >= 6 and settings.ICLOCK_AUTO_REG): #若SN正确，且设置可以自动注册
            from mysite.personnel.models.model_area import Area
            device = Device(
                sn = sn, 
                alias="auto_add",
                last_activity=datetime.datetime.now(), 
                dining = Dininghall.objects.all()[0],
                consume_model = MONEY_MODEL,
                device_use_type = POS_DEVICE,
                device_type = DEVICE_POS_IC,
                check_black_list = True,
                area=Area.objects.all()[0],
                ipaddress=request.META["REMOTE_ADDR"])
            device.save(force_insert=True, log_msg=False)
            device.set_pos_device_option()
            init_ic_pos_device(device)
        else:
            return None
    if device.status in (STATUS_STOP, STATUS_PAUSED):
        return None
    check_and_init_cmds_cache(device) #检查缓存命令结构是否存在，如果不存在初始化缓存命令结构
    pos_device = get_redis_device(device)
    pos_device.last_activity = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pos_device.set('last_activity')
    return device


from mysite.pos.pos_ic.ic_cache_cmds import update_and_load_cmds,check_pre_request \
        ,get_pre_request_cmds,get_request_cmds,update_start_end_index,get_prev_save_time \
        ,save_last_activity


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

#设备挂失，解挂，修改密码操作
def pos_business(request,device):
    from mysite.pos.models.model_loseunitecard import LoseUniteCard
    from mysite.iclock.models.dev_comm_operate import update_pos_device_info,sync_delete_user,sync_delete_user_privilege,sync_delete_user,sync_report_user,delete_pos_device_info
    from mysite.utils import get_option
    rep_type = request.REQUEST.get('RepType')
    card = request.REQUEST.get('Card','')
    card_pwd = request.REQUEST.get('Pwd','')
    old_pwd = request.REQUEST.get('OldPwd','')
    new_pwd = request.REQUEST.get('NewPwd','')
    resp = ""
    if card:
        try:
            objcard = IssueCard.objects.get(sys_card_no = card)
        except:
            return "NO"
            pass
    if objcard and objcard.card_privage <>  POS_CARD:#管理卡直接返回失败
        return "NO"
    if card_pwd and objcard.Password <> card_pwd:
        return "NO"
    if old_pwd and objcard.Password <> old_pwd:
        return "NO"
    if rep_type == IC_CARD_LOST:
        if objcard.cardstatus==CARD_LOST:
            return "NO" 
        if objcard.cardstatus==CARD_STOP:
            return "NO" 
        if objcard.cardstatus==CARD_OVERDUE:
            return "NO"
        objcard.cardstatus = CARD_LOST
        objcard.save(force_update=True,log_msg=False)
        LoseUniteCard(UserID_id = objcard.UserID_id,
           cardno = objcard.cardno,
           type = objcard.type,
           cardstatus='3',#挂失
           sys_card_no=objcard.sys_card_no,
           Password=objcard.Password,
           time = datetime.datetime.now()).save()
        dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
        update_pos_device_info(dev,[objcard],"USERINFO")
        if get_option("ATT"):
            from base.sync_api import SYNC_MODEL
            if not SYNC_MODEL:
                oldObj=objcard.UserID
                devs=oldObj.search_device_byuser()
                sync_report_user(devs, [oldObj])
        if get_option("IACCESS"):
            oldObj=objcard.UserID
            if oldObj.check_accprivilege():
                devs=oldObj.search_accdev_byuser()
                sync_report_user(devs,[oldObj]) 
#                sync_delete_user_privilege(devs,[oldObj])
        return "OK"
    elif rep_type == CARD_REVERT:
        if objcard.cardstatus==CARD_VALID:
            return "NO" 
        if objcard.cardstatus==CARD_STOP:
            return "NO" 
        if objcard.cardstatus==CARD_OVERDUE:
            return "NO"
        obj = IssueCard.objects.filter(UserID = objcard.UserID,cardstatus = CARD_VALID)
        if obj:
            return "NO"
        objcard.cardstatus = CARD_VALID
        objcard.save(force_update=True,log_msg=False)
        LoseUniteCard(UserID_id = objcard.UserID_id,
           cardno = objcard.cardno,
           type = objcard.type,
           cardstatus='1',#解挂
           sys_card_no=objcard.sys_card_no,
           Password=objcard.Password,
           time = datetime.datetime.now()).save()
        dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
        delete_pos_device_info(dev,[objcard],"USERINFO")
        if get_option("ATT"):
            from base.sync_api import SYNC_MODEL
            if not SYNC_MODEL:
                from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                adj_user_cmmdata(objcard.UserID, [],objcard.UserID.attarea.all())
        if get_option("IACCESS"):
            from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege    #-----2012.02.02   xiaoxiaojun                 
            newObj=objcard.UserID
            accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
            sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
#            sync_set_user_privilege(accdev, [newObj]) #下放人员权限到设备
        return "OK"
    elif rep_type == CHANGE_PWD_OK:
        objcard.Password = new_pwd
        objcard.save(force_update=True,log_msg=False)
        return "OK"
    elif rep_type == IS_CHANGE_PWD:
        return "OK"


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


#设备读取命令返回值
def pos_devpost(request):
    response = device_response()
    resp = ""
    device = check_pos_device(request)
    if device is None : 
        response.write("UNKNOWNDEVICE")
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
#        print u"执行指令返回后返回值=======%s"%request.build_absolute_uri()
#        print "ppost:%s"%pdata
        dev_return = "设备执行指令后请求===%s返回值=======%s"%(request.build_absolute_uri(),pdata)
        pos_write_log(dev_return,device.sn)
#        logger.error(pdata)
        for apost in pdata:
            id = int(apost["ID"])
            ret = apost["Return"]
            if apost["CMD"] == "INFO":#消费设备暂时没有用到
                #save_dev_info(device, apost['Content'])
                
                parse_dev_info(device, apost['Content'])
                device.save(force_update=True,log_msg=False)
                rets[id] = ret
#            elif apost['CMD'] == 'PutFile' and ret > 100 * 1024:  #可能是固件升级命令
#                cmdobj = update_cmd(device, id, ret)
#                post_check_update(device,[ret])#更新下发命令，起始结束标示
#                if cmdobj: check_upgrade_fw(device, cmdobj, request)
#            elif (apost["CMD"] == "GetFile" or apost["CMD"] == "Shell") and ret > 0:
#                check_upload_file(request, apost)
#                rets[id] = ret
#            elif apost["CMD"] == "VERIFY SUM" and ret > 0:
#                check_att_sum(apost,device)
#                rets[id] = ret
#            elif apost["CMD"] == "PutFile":
#                check_upgradefile(id,apost,device,ret)
#                post_check_update(device,[ret])
                #rets[id] = ret
            else:
                rets[id] = ret
        if len(rets) > 0:
            update_cmds(device, rets)
        resp += "OK"
    #check_and_save_cache(device)
    
    except:
        import traceback;traceback.print_exc()
        errorLog(request)
        pass
        
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response


#设备读取命令
def pos_getreq(request):
    response = device_response()
    try:
        resp = ""
        device = check_pos_device(request)
        
        if device is None: 
            response.write("UNKNOWNDEVICE")
            return response
#-------------------------------------验证设备记录是否已经全部上传------------------------------------------
        pos_device = get_redis_device(device)
        if request.REQUEST.has_key('type'):
            type = request.REQUEST.get('type')
            devno = request.REQUEST.get('devno')
            if type == "pos":
                pos_log_stamp_id = pos_device.pos_log_stamp_id
                if int(pos_log_stamp_id) >= int(devno) :
                    pos_device.pos_dev_data_status = True
                    pos_device.set("pos_dev_data_status")
                else:
                    pos_device.pos_dev_data_status = False
                    pos_device.set("pos_dev_data_status")
            elif type == "full":
                full_log_stamp_id = pos_device.full_log_stamp_id 
                if int(full_log_stamp_id) >= int(devno) :
                    pos_device.pos_dev_data_status = True
                    pos_device.set("pos_dev_data_status")
                else:
                    pos_device.pos_dev_data_status = False
                    pos_device.set("pos_dev_data_status")
            elif type == "allow":
                allow_log_stamp_id = device.allow_log_stamp_id
                if int(allow_log_stamp_id) >= int(devno) :
                    pos_device.pos_dev_data_status = True
                    pos_device.set("pos_dev_data_status")
                else:
                    pos_device.pos_dev_data_status = False
                    pos_device.set("pos_dev_data_status")
#            device.save(force_update=True,log_msg=False)
#-------------------------------------验证设备记录是否已经全部上传------------------------------------------
        
        if request.REQUEST.has_key('RepType'):
                resp+=pos_business(request,device)
                
        else:
            update_and_load_cmds(device) #如果命令全部执行完，更新缓存命令到数据库，重新加载新的命令到缓存
            info = request.GET.get("INFO", "") #版本号，用户数,指纹数,记录数,设备自身IP地址
    #        resp+="CHECKLOG"

            devcmds = []
            flag_new = False #是否是下发新的命令
            check_ret = check_pre_request(device)#确认上次下发命令，机器是否成功接收到
#            print u"设备命令是否执行成功%s",check_ret
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

                CmdContent=obj_cmd.CmdContent
#                if CmdContent.find("DATA UPDATE user")==0 or CmdContent.find("SMS ")==0 or CmdContent.find("DATA UPDATE SMS")==0 : #传送用户命令,需要解码成GB2312
                cc=CmdContent
#                print u"设备获取下发指令%s"%cc
                try:
                    cc=cc.encode("gb18030")
                except:
                    try:
                        cc=cc.decode("utf-8").encode("gb18030")
                    except:
                        import traceback;traceback.print_exc()
                        pass
                        errorLog(request)
                nowcmd=str(cc)
                cc=std_cmd_convert(cc, device)
                if cc: resp+="C:%d:%s\n"%(obj_cmd.id,cc)

                c=c+1
                obj_cmd.CmdTransTime=datetime.datetime.now()
                update_cached_cmd(obj_cmd)
                
                if (c>=maxRet) or (len(resp)>=maxRetSize): break;     #达到了最大命令数或最大命令长度限制
                if CmdContent in DEVICE_CMD: break; #重新启动命令只能是最后一条指令  #增加查找到CHECK指令后，直接发送


            if c == 0:#没有发送任何命令时，简单向设备返回 "OK" 即可
                resp += "OK"
            else:
                if flag_new:
                    update_start_end_index(device,c) #更新下发命令的起始和结束为止
                
#            dt_now = datetime.datetime.now()
#            device.last_activity = dt_now
##            device.cache_device()
#            prev_save_time = get_prev_save_time(device)
#            if (dt_now -prev_save_time).seconds>300: #五分钟保存一次
#                device.save(force_update=True,log_msg=False)
#                save_last_activity(device)
    except  Exception, e:
        import traceback;traceback.print_exc()
        resp = u"%s" % e
        errorLog(request)
#    if settings.ENCRYPT:
#        import lzo
#        resp = lzo.bufferEncrypt(resp + "\n", device.sn)
    response["Content-Length"] = len(resp)
    response.write(resp)
#    print u"resp==设备获取下发指令系统返回值",resp
    dev_log = "resp==设备获取指令请求%s++++++++++返回值%s"%(request.build_absolute_uri(),resp)
    pos_write_log(dev_log,device.sn)
    return response


def cdata_get_options(device):
    pos_device = get_redis_device(device)
    resp = "GET OPTION FROM: %s\n" % device.sn
    resp += "Stamp=%s\n" % (device.log_stamp or 0)
    resp += "OpStamp=%s\n" % (device.oplog_stamp or 0)
    resp += "PosLogStamp=%s\n" % (pos_device.pos_log_stamp or 0)
    resp += "FullLogStamp=%s\n" % (pos_device.full_log_stamp or 0)
    resp += "AllowLogStamp=%s\n" % (pos_device.allow_log_stamp or 0)
    #为设备最后上传消费记录的记录戳标记20120827修改
    resp += "PosLogStampId=%s\n" % (pos_device.pos_log_stamp_id or 0)
    resp += "FullLogStampId=%s\n" % (pos_device.full_log_stamp_id or 0)
    resp += "AllowLogStampId=%s\n" % (pos_device.allow_log_stamp_id or 0)
    #备份记录标示
    resp += "PosBakLogStampId=%s\n" % (pos_device.pos_log_bak_stamp_id or 0)
    resp += "FullBakLogStampId=%s\n" % (pos_device.full_log_bak_stamp_id or 0)
    resp += "AllowBakLogStampId=%s\n" % (pos_device.allow_log_bak_stamp_id or 0)
    
    resp += "UseStampId=1\n" #启动机器流水号标记上传消费记录(直接设置UseStampId=1) 
    
    resp += "TableNameStamp=%s\n" % (device.table_name_stamp or 0)
    resp += "PhotoStamp=%s\n" % (device.photo_stamp or 0)
    resp += "ErrorDelay=%d\n" % max(30, settings.MIN_REQ_DELAY)
    resp += "Delay=%d\n" % max(settings.POS_MIN_REQ_DELAY, device.delay)
    resp += "TransTimes=%s\n" % device.trans_times
    resp += "TransInterval=%d\n" % max(settings.MIN_TRANSINTERVAL, device.trans_interval)
    resp += "TransFlag=%s\n" % device.update_db
    resp += "SyncTime=%s\n" % (settings.POS_SYNC_TIME or 0)
    if device.fw_version is None:
        from mysite.pos.models.model_posparam import PosParam
        from base.crypt import encryption,decryption
        from mysite.pos.pos_utils import enc
        pos_param = PosParam.objects.all()[0]
        resp += "UseSection=%s\n" % pos_param.main_fan_area
        resp += "BackSection=%s\n" % pos_param.minor_fan_area
        resp += "CardPass=%s\n" % enc(decryption(pos_param.pwd_again))
    if device.tz_adj is not None:
        resp += "TimeZone=%s\n" % device.tz_adj
    resp += "Realtime=%s\n" % ((settings.TRANS_REALTIME and device.realtime) and "1" or "0")
    resp += "Encrypt=%s\n\n" % (settings.ENCRYPT or device.encrypt)
    return resp

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
        #根据传过来的语言设置settings中的机器台数
        authorize_fun.check_push_device(language, settings.AUTHORIZE_MAGIC_KEY)
        #/****语言控制台数pwp end***/
        if request.REQUEST.has_key('type'):#获取服务器时间
            dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            resp +="Time=%s\n" %dt
        else:
            device = check_pos_device(request, True)
            if device is None : 
                response.write("UNKNOWNDEVICE")
                return response
            elif request.method == 'GET':
                resp+=cdata_get_options(device)
                dev_return = u"设备自动注册请求%s，服务器返回值=======%s"%(request.build_absolute_uri(),resp)
                pos_write_log(dev_return,device.sn)
                if request.REQUEST.has_key('devicename'):
                    device.device_name = request.REQUEST.get('devicename')
                    device.ipaddress = request.META["REMOTE_ADDR"]
                if request.REQUEST.has_key('fireVer'):
                    device.fw_version=request.REQUEST.get('fireVer') 
                    device.save()
                encrypt = 0
            elif request.method == 'POST':
                try:
                    resp+=cdata_post(request, device)
                    dev_return = "设备上传数据请求%s，服务器返回值=======%s"%(request.build_absolute_uri(),resp)
                    pos_write_log(dev_return,device.sn)
                except Exception, e:
                    resp = u"ERROR: %s" % e
                    errorLog(request)
            else:
                resp += "UNKOWN DATA\n"
                resp += "POST from: " + device.sn + "\n"
#        check_and_save_cache(device)
    except  Exception, e:
        errorLog(request)
        resp = u"%s" % e
    response["Content-Length"] = len(resp)
    response.write(resp)
    return response


def commit_log_(cursor, sql, cnn,stamp_name):
    sql_exc=""
    if stamp_name == 'pos_log_stamp' :
        sql_exc = pos_log_statement
    elif stamp_name == 'pos_log_bak_stamp' :
        sql_exc = pos_log_bak_statement
    elif stamp_name == 'full_log_stamp':
        sql_exc = full_log_statement
    elif stamp_name == 'full_log_bak_stamp':
        sql_exc = full_log_bak_statement
    elif stamp_name == 'allow_log_stamp':
        sql_exc = allow_log_statement
    elif stamp_name == 'allow_log_bak_stamp':
        sql_exc = allow_log_bak_statement
    elif stamp_name == 'store_detail':
        sql_exc = store_detail_statement
    elif stamp_name == 'key_detail':
        sql_exc = key_detail_statement
    elif stamp_name == 'time_detail':
        sql_exc = time_detail_statement
    
    if type(sql)==type([]):
        for data in sql: #sqlite3 数据库需要单次执行以减少 “Database is locked 错误”
#            print "data sql:%s     \n %s"%(stamp_name,data)
            try:
                if settings.DATABASE_ENGINE == "sqlserver_ado":
                    check_factor = check_repeated_data(stamp_name,data)
                    sql_s = check_factor + sql_exc
                    cursor.execute(sql_s, data)
                else:
                    cursor.execute(sql_exc, data)
                if stamp_name == 'allow_log_stamp':
                    from mysite.pos.models.model_allowance import Allowance#按月补贴
                    from django.db import models
                    sys_card_no = data[2] #卡编号
                    batch = data[13] #补贴批次
                    base_batch = data[14] #补贴基次
                    re_money = data[9] #领取金额
                    re_date = datetime.datetime.strptime(data[6],"%Y-%m-%d %H:%M:%S")#领取时间
                    try:
                        obj = Allowance.objects.get(sys_card_no = sys_card_no,batch = batch)
                        obj.is_ok = 1
                        obj.receive_money = re_money
                        obj.receive_date = re_date
                        obj.base_batch = base_batch
                        models.Model.save(obj,force_update=True)
                    except:
                        pass
            except IntegrityError:
                raise IntegrityError
                pass
            except Exception,e:
                import traceback;traceback.print_exc()

    elif type(sql)==type((0,)):
        if settings.DATABASE_ENGINE == "sqlserver_ado":
            check_factor = check_repeated_data(stamp_name,data)
            sql_s = check_factor + sql_exc
            cursor.execute(sql_s, sql)
        else:
            cursor.execute(sql_exc, sql)
        if stamp_name == 'allow_log_stamp':
            from mysite.pos.models.model_allowance import Allowance#按月补贴
            from django.db import models
            sys_card_no = sql[2] #卡编号
            batch = sql[13] #补贴批次
            base_batch = sql[14] #补贴基次
            obj = Allowance.objects.get(sys_card_no = sys_card_no,batch = batch)
            obj.is_ok = 1
            obj.base_batch = base_batch
            models.Model.save(obj,force_update=True)
    else:
        cursor.execute(sql)
    if cnn: cnn._commit()


def commit_log(cursor, sql, cnn,stamp_name):
    try:
        commit_log_(cursor, sql, cnn,stamp_name)
    except IntegrityError:
        raise IntegrityError
    except:
        import traceback;traceback.print_exc()
        print "try again"
        cnn._rollback()
        cnn.close()
        cursor=cnn.cursor()
        commit_log(cursor, sql, cnn,stamp_name)
    return cursor
   
#消费记录
pos_log_statement="""insert into %s (user_id,user_pin, user_name, dept_id, card, sys_card_no, dev_sn, card_serial_num,dev_serial_num,pos_time,convey_time,\
type_name,money,balance,pos_model,dining_id,meal_id,meal_data,create_operator,log_flag)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s,%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s, %%s,%%s,%%s)""" % ICConsumerList._meta.db_table

#消费记录备份
pos_log_bak_statement="""insert into %s (user_id,user_pin, user_name, dept_id, card, sys_card_no, dev_sn, card_serial_num,dev_serial_num,pos_time,convey_time,\
type_name,money,balance,pos_model,dining_id,meal_id,meal_data,create_operator,log_flag)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s,%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s, %%s,%%s,%%s)""" % ICConsumerListBak._meta.db_table

#消费记录备份
def line_to_pos_bak_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    pos_time = datetime.datetime.strptime(flds[2],"%Y-%m-%d %H:%M:%S")
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[2])
        pos_time = datetime.datetime.strptime(flds[2],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= pos_time:#过滤掉无卡退卡后的卡所产生的消费记录
            if flds[6] == '9':
                logtype = 9 #纠错记录
                pos_money = Decimal(flds[3])/100
            elif flds[6] == '4':#计次消费消费金额转为0
                logtype = 10 #计次消费
                pos_money = 0
            else:
                logtype = LOGTYPE[stamp_name]
                pos_money = Decimal(flds[3])/100
            if flds[7] == '0':
                meal_id = None
            else:
                meal_id = flds[7]
    #       sql = (card.UserID_id, card.UserID.EName,card.UserID.DeptID.name,card.cardno,card.sys_card_no,device.sn,flds[5],flds[9],flds[2],now,1,flds[3],flds[4], flds[6],device.dining,flds[7],flds[8], flds[10],1)
            sql = (card.UserID_id,card.UserID.PIN, card.UserID.EName,card.UserID.DeptID.pk,card.cardno,flds[1],device.sn,flds[5],flds[9],flds[2],now,logtype,pos_money,Decimal(flds[4])/100, flds[6],device.dining.pk,meal_id,flds[2], flds[10],1)
            return sql
        else:
            return None
    except:
#        import traceback; traceback.print_exc();
        return None


#消费记录
def line_to_pos_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    pos_time = datetime.datetime.strptime(flds[2],"%Y-%m-%d %H:%M:%S")
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[2])
        pos_time = datetime.datetime.strptime(flds[2],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= pos_time:#过滤掉无卡退卡后的卡所产生的消费记录
            if flds[6] == '9':
                logtype = 9 #纠错记录
                pos_money = Decimal(flds[3])/100
            elif flds[6] == '4':#计次消费消费金额转为0
                logtype = 10 #计次消费
                pos_money = 0
            else:
                logtype = LOGTYPE[stamp_name]
                pos_money = Decimal(flds[3])/100
            if flds[7] == '0':
                meal_id = None
            else:
                meal_id = flds[7]
    #       sql = (card.UserID_id, card.UserID.EName,card.UserID.DeptID.name,card.cardno,card.sys_card_no,device.sn,flds[5],flds[9],flds[2],now,1,flds[3],flds[4], flds[6],device.dining,flds[7],flds[8], flds[10],1)
            sql = (card.UserID_id,card.UserID.PIN, card.UserID.EName,card.UserID.DeptID.pk,card.cardno,flds[1],device.sn,flds[5],flds[9],flds[2],now,logtype,pos_money,Decimal(flds[4])/100, flds[6],device.dining.pk,meal_id,flds[2], flds[10],1)
            return sql
        else:
            return None
    except:
        import traceback;traceback.print_exc()
        return None

full_log_statement="""insert into %s (user_id, card, sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,\
type_id,money,blance,hide_column,create_operator,log_flag,status)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s, %%s, %%s, %%s, %%s,%%s,%%s)""" % CarCashSZ._meta.db_table

full_log_bak_statement="""insert into %s (user_pin, user_name, DeptName,physical_card_no,sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,\
money,blance,hide_column,create_operator,log_flag,status)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s, %%s, %%s, %%s, %%s,%%s,%%s,%%s)""" % CarCashSZBak._meta.db_table


def cashier_state(state):
    if state == '0': return 1#充值
    if state == '1': return 5#退款
    if state == '2': return 13#优惠记录
    return state

#充值记录
def line_to_full_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[3])
        full_time = datetime.datetime.strptime(flds[3],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= full_time:#过滤掉无卡退卡后的卡所产生的充值记录
            logtype = cashier_state(flds[6])
            sql = (card.UserID_id,card.cardno,flds[1],device.sn,flds[2],flds[7],flds[3],now,logtype,Decimal(flds[4])/100,Decimal(flds[5])/100, logtype,flds[8],1,0)
            return sql
        else:
            return None
    except:
        return None
    
#充值备份记录
def line_to_full_bak_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    from mysite.personnel.models.model_emp import get_dept
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[3])
        full_time = datetime.datetime.strptime(flds[3],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= full_time:#过滤掉无卡退卡后的卡所产生的充值记录
            logtype = cashier_state(flds[6])
            user_pin = getuserinfo(card.UserID_id,"PIN")
            user_name = getuserinfo(card.UserID_id,"EName")
            user_dept_name = get_dept(card.UserID_id).name
            sql = (user_pin,user_name,user_dept_name,card.cardno,flds[1],device.sn,flds[2],flds[7],flds[3],now,Decimal(flds[4])/100,Decimal(flds[5])/100, logtype,flds[8],1,0)
            return sql
        else:
            return None
    except:
        return None


allow_log_statement="""insert into %s (user_id, card, sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,\
type_id,money,blance,hide_column,allow_type,allow_batch,allow_base_batch,log_flag,status)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s, %%s, %%s, %%s, %%s,%%s, %%s, %%s,%%s)""" % CarCashSZ._meta.db_table

allow_log_bak_statement="""insert into %s (user_pin, user_name, DeptName,physical_card_no,sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,\
money,blance,hide_column,allow_type,allow_batch,allow_base_batch,log_flag,status)
values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s,%%s, %%s, %%s, %%s, %%s,%%s, %%s, %%s,%%s, %%s)""" % CarCashSZBak._meta.db_table


#补贴记录
def line_to_allow_bak_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    from mysite.personnel.models.model_emp import get_dept
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[4])
        allow_time = datetime.datetime.strptime(flds[4],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= allow_time:#过滤掉无卡退卡后的卡所产生的补贴记录
            logtype = LOGTYPE[stamp_name]
            user_pin = getuserinfo(card.UserID_id,"PIN")
            user_name = getuserinfo(card.UserID_id,"EName")
            user_dept_name = get_dept(card.UserID_id).name
            sql = (user_pin,user_name,user_dept_name,card.cardno,flds[1],device.sn,flds[2],flds[9],flds[4],now,Decimal(flds[5])/100,Decimal(flds[6])/100, logtype,flds[7],flds[3],flds[8],1,0)
            return sql
        else:
            return None
    except:
#        import traceback; traceback.print_exc();
        return None



#补贴记录
def line_to_allow_log(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE,CARD_INVALID
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        card = IssueCard.all_objects.get(sys_card_no=flds[1],create_time__lte=flds[4])
        allow_time = datetime.datetime.strptime(flds[4],"%Y-%m-%d %H:%M:%S")
        if card.failuredate is None or card.failuredate >= allow_time:#过滤掉无卡退卡后的卡所产生的补贴记录
            logtype = LOGTYPE[stamp_name]
            sql = (card.UserID_id,card.cardno,flds[1],device.sn,flds[2],flds[9],flds[4],now,logtype,Decimal(flds[5])/100,Decimal(flds[6])/100, logtype,flds[7],flds[3],flds[8],1,0)
            return sql
        else:
            return None
    except:
        return None
    
store_detail_statement="""insert into %s (list_code_id, dev_sn,dev_serial_num, store_code, money, RecSum,convey_time)values(%%s, %%s, %%s,%%s, %%s, %%s, %%s)""" % StoreDetail._meta.db_table

#商品模式明细 记录
def line_to_store_detail(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        list = ICConsumerList.objects.get(dev_sn=device.sn,dev_serial_num = flds[0])
        sql = (list.id,device.sn,int(flds[0]),flds[1],Decimal(flds[2])/100,flds[3],now)
        return sql
    except:
#        import traceback; traceback.print_exc();
        return None
    
key_detail_statement="""insert into %s (list_code_id,dev_sn, dev_serial_num, key_code, money, RecSum,convey_time)values(%%s, %%s,%%s, %%s, %%s, %%s, %%s)""" % KeyDetail._meta.db_table

#键值模式明细 记录
def line_to_key_detail(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        list = ICConsumerList.objects.get(dev_sn=device.sn,dev_serial_num = flds[0])
        sql = (list.id,device.sn,flds[0],flds[1],Decimal(flds[2])/100,flds[3],now)
        return sql
    except:
#        import traceback; traceback.print_exc();
        return None

time_detail_statement="""insert into %s (list_code_id,dev_sn, dev_serial_num, begin_time, begin_money, end_time,end_money,convey_time)values(%%s,%%s,%%s, %%s, %%s,%%s,%%s,%%s)""" % TimeDetail._meta.db_table

#计时模式明细 记录
def line_to_time_detail(device, line, stamp_name,event=True):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]
    now=datetime.datetime.now()
    try:
        list = ICConsumerList.objects.get(dev_sn=device.sn,dev_serial_num = flds[0])
        sql = (list.id,device.sn,flds[0],flds[1],Decimal(flds[2])/100,flds[3],Decimal(flds[4])/100,now)
        return sql
    except:
#        import traceback; traceback.print_exc();
        return None

def check_repeated_data(stamp_name,data):
    if stamp_name == 'pos_log_stamp' :
       SELECT_ICCONSUMERLIST = "if  not exists(select user_id from pos_icconsumerlist where (dev_sn='%s' and sys_card_no='%s' and money='%s' and card_serial_num='%s'and dev_serial_num='%s' and pos_time ='%s'))" % (data[6],data[5],data[12],data[7],data[8],data[9])
       return SELECT_ICCONSUMERLIST
    elif stamp_name == 'pos_log_bak_stamp' :
           SELECT_ICCONSUMERLIST = "if  not exists(select user_id from pos_icconsumerlistbak where (dev_sn='%s' and sys_card_no='%s' and money='%s' and card_serial_num='%s'and dev_serial_num='%s' and pos_time ='%s'))" % (data[6],data[5],data[12],data[7],data[8],data[9])
           return SELECT_ICCONSUMERLIST
    elif stamp_name == 'full_log_stamp':
       SELECT_FULL = "if not exists(select user_id from pos_carcashsz where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data[3],data[11],data[2],data[9],data[6])
       return SELECT_FULL
    elif stamp_name == 'full_log_bak_stamp':
       SELECT_FULL = "if not exists(select user_id from pos_carcashszbak where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data[3],data[11],data[2],data[9],data[6])
       return SELECT_FULL
    elif stamp_name == 'allow_log_stamp':
       SELECT_ALLOW ="if not exists(select user_id from pos_carcashsz where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data[3],data[11],data[2],data[9],data[6])
       return SELECT_ALLOW
    elif stamp_name == 'allow_log_bak_stamp':
       SELECT_ALLOW ="if not exists(select user_id from pos_carcashszbak where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data[3],data[11],data[2],data[9],data[6])
       return SELECT_ALLOW
    elif stamp_name == 'store_detail':
       SELECT_STORE ="if not exists(select list_code_id from pos_storedetail where (list_code_id='%s' and RecSum='%s'))" %(data[0],data[5])
       return SELECT_STORE
    elif stamp_name == 'key_detail':
       SELECT_KEY ="if not exists(select list_code_id from pos_keydetail where (list_code_id='%s' and RecSum='%s'))" %(data[0],data[5])
       return SELECT_KEY
    elif stamp_name == 'time_detail':
       SELECT_TIME ="if not exists(select list_code_id from pos_timedetail where (list_code_id='%s' and dev_sn='%s' and dev_serial_num = '%s' ))" %(data[0],data[1],data[2])
       return SELECT_TIME
    

def cdata_post_trans(device, raw_data,stamp_name, head=None,old_head=None):
    cursor = conn.cursor()
    okc = 0;#成功提交数据count
    errorLines = [] #发生保存错误的记录
    cacheLines = [] #本次提交的行
    errorLogs = []  #解析出错、不正确数据的行
    sqls = []
    commitLineCount = POS_DEAL_BAT_SIZE #达到700行就提交一次
    cardno_list = []
    card_dict = {}
    #if settings.DATABASE_ENGINE == "ado_mssql": commitLineCount = 50
    if settings.DATABASE_ENGINE == "sqlserver_ado": commitLineCount = 50
    alog = None
#    print raw_data.splitlines()
    pos_device = get_redis_device(device)
    for line in raw_data:
        if line:
            eMsg = ""
            card_blance = None
            log = None
            flds = line.split("\t")
            try:
                if stamp_name == 'pos_log_stamp' :
                    pos_device.pos_log_stamp = head['STAMP']
                    pos_device.set('pos_log_stamp')
                    if int(head['STAMPID']) > int(pos_device.pos_log_stamp_id):
                        pos_device.pos_log_stamp_id = head['STAMPID']
                        pos_device.set('pos_log_stamp_id')
                    log = line_to_pos_log(device, line,stamp_name)
                    card_blance = Decimal(flds[4])/100
                if stamp_name == 'pos_log_bak_stamp' :
                    if int(head['STAMPID']) > int(pos_device.pos_log_bak_stamp_id):
                        pos_device.pos_log_bak_stamp_id = head['STAMPID']
                        pos_device.set('pos_log_bak_stamp_id')
                    log = line_to_pos_bak_log(device, line,stamp_name)
                    card_blance = Decimal(flds[4])/100
                elif stamp_name == 'full_log_stamp':
                    pos_device.full_log_stamp = head['STAMP']
                    pos_device.set('full_log_stamp')
                    if int(head['STAMPID']) > int(pos_device.full_log_stamp_id):
                        pos_device.full_log_stamp_id = head['STAMPID']
                        pos_device.set('full_log_stamp_id')
                    log = line_to_full_log(device, line,stamp_name)
                    card_blance = Decimal(flds[5])/100
                elif stamp_name == 'full_log_bak_stamp':
                    if int(head['STAMPID']) > int(pos_device.full_log_bak_stamp_id):
                        pos_device.full_log_bak_stamp_id = head['STAMPID']
                        pos_device.set('full_log_bak_stamp_id')
                    log = line_to_full_bak_log(device, line,stamp_name)
                    card_blance = Decimal(flds[5])/100
                elif stamp_name == 'allow_log_stamp':
                    pos_device.allow_log_stamp = head['STAMP']
                    pos_device.set('allow_log_stamp')
                    if int(head['STAMPID']) > int(pos_device.allow_log_stamp_id):
                        pos_device.allow_log_stamp_id = head['STAMPID']
                        pos_device.set('allow_log_stamp_id')
                    log = line_to_allow_log(device, line,stamp_name)
                    card_blance = Decimal(flds[6])/100
                elif stamp_name == 'allow_log_bak_stamp':
                    if int(head['STAMPID']) > int(pos_device.allow_log_bak_stamp_id):
                        pos_device.allow_log_bak_stamp_id = head['STAMPID']
                        pos_device.set('allow_log_bak_stamp_id')
                    log = line_to_allow_bak_log(device, line,stamp_name)
                    card_blance = Decimal(flds[6])/100
                elif stamp_name == 'store_detail':
                    log = line_to_store_detail(device, line,stamp_name)
                elif stamp_name == 'key_detail':
                    log = line_to_key_detail(device, line,stamp_name)
                elif stamp_name == 'time_detail':
                    log = line_to_time_detail(device, line,stamp_name)
                
            except Exception, e:  #行数据解析错误
                eMsg = u"%(mg)s" % {"mg":e.message}
                import traceback; traceback.print_exc();
                log = None
#            print "log=================",log
            if log:
                if cardno_list.count(flds[0]) == 0:
                    cardno_list.append(flds[0])
                    if stamp_name in ['full_log_stamp','allow_log_stamp']  :
                        card_dict[flds[0]] = flds[2]+":"+str(card_blance)
                    elif stamp_name == 'pos_log_stamp':
                        card_dict[flds[0]] = flds[5]+":"+str(card_blance)
                else:
                    if stamp_name in ['full_log_stamp','allow_log_stamp'] and card_dict and int(card_dict[flds[0]].split(':')[0])<= int(flds[2]) :
                        card_dict[flds[0]] = flds[2]+":"+str(card_blance)
                    elif  stamp_name == 'pos_log_stamp' and card_dict and int(card_dict[flds[0]].split(':')[0])< int(flds[5]):
                        card_dict[flds[0]] = flds[5]+":"+str(card_blance)
                sqls.append(log)
                cacheLines.append(line) #先记住还没有提交数据，commit不成功的话可以知道哪些数据没有提交成功
                if len(cacheLines) >= commitLineCount: #达到一定的行就提交一次
                    try:
                        commit_log(cursor, sqls, conn,stamp_name)
                        okc += len(cacheLines)
                        if not alog:
                            alog = cacheLines[0]
                    except IntegrityError:
                        errorLines += cacheLines
                        pass
                    except Exception, e:
#                        print_exc() 
                        print "cdata_post_trans_error"
                        conn.close()
                        cursor = conn.cursor()
                        errorLines += cacheLines
                    cacheLines = []
                    sqls = []
            else:
                if not head['Z']=='0':
                    errorLogs.append("%s\t------------%s\n" % (line, eMsg and eMsg or "Invalid Data"))
    if cacheLines: #有还没有提交的数据
        try:
            commit_log(cursor, sqls, conn,stamp_name)
            okc += len(cacheLines)
            if not alog:
                alog = cacheLines[0]
        except IntegrityError:
            errorLines += cacheLines
            pass
        except Exception, e:
            print_exc()
            print "try again***"
            conn.close()
            cursor = conn.cursor()
            errorLines += cacheLines
    if errorLines: #重新保存上面提交失败的数据，每条记录提交一次，最小化失败记录数
        cacheLines = errorLines
        errorLines = []
        for line in cacheLines:
            if line not in errorLogs:
                try:
                    if stamp_name == 'pos_log_stamp' :
                       log = line_to_pos_log(device, line,stamp_name)
                    elif stamp_name == 'pos_log_bak_stamp' :
                       log = line_to_pos_bak_log(device, line,stamp_name)
                    elif stamp_name == 'full_log_stamp':
                       log = line_to_full_log(device, line,stamp_name)
                    elif stamp_name == 'full_log_bak_stamp':
                       log = line_to_full_bak_log(device, line,stamp_name)
                    elif stamp_name == 'allow_log_stamp':
                       log = line_to_allow_log(device, line,stamp_name)
                    elif stamp_name == 'allow_log_bak_stamp':
                       log = line_to_allow_bak_log(device, line,stamp_name)
                    elif stamp_name == 'store_detail':
                        log = line_to_store_detail(device, line,stamp_name)
                    elif stamp_name == 'key_detail':
                        log = line_to_key_detail(device, line,stamp_name)
                    elif stamp_name == 'time_detail':
                        log = line_to_time_detail(device, line,stamp_name)
                    commit_log(cursor, log, conn,stamp_name)
                    if not alog: alog = cacheLines[0]
                    okc += 1
                except IntegrityError:
                    pass
                except Exception, e:
#                    import traceback; traceback.print_exc();
                    logger.error(e)
                    errorLines.append(line)
                    pass
    errorLines += errorLogs
    dlogObj = ""
    try:
        if okc == 1:
            dlogObj = alog
        elif okc > 1:
            dlogObj = alog + ", ..."
    except:pass
#    print "card_dict",card_dict
    if stamp_name in ['pos_log_stamp','full_log_stamp','allow_log_stamp']:
        update_card_blance(card_dict,stamp_name,more_data=True)
#    if len(cacheLines) > 1:
#        update_card_blance(card_dict,stamp_name,more_data=True)
#    elif len(cacheLines) == 1:
#        update_card_blance(card_dict,stamp_name,card_blance)
        
    if errorLines:
        #ErrNo:22 (invalid argument)的错误处理。
        #出错的非重复记录，写入错误日志文件tmp/device.sn/error
        elinedata=[]
        for el in errorLines:
            elinedata.append(el.split("\t--")[0])
        if elinedata:
            from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata    
            obj=pos_gen_device_cmmdata(device,old_head+"\n"+"\n".join(elinedata),"error")
#    device.save(force_update=True,log_msg=False)
#    device.cache_device(is_new=False)
#    super(Device, device).save(force_update=True,log_msg=False)
    return (okc, len(errorLines), dlogObj)

def my_custom_sql(sql):
    from django.db import connection
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row 
    except Exception, e:
        import traceback; traceback.print_exc();

def update_card_blance(card_dict,stamp_name,blance=None,more_data=False):
    select_issuecard = "SELECT  max(card_serial_num) FROM personnel_issuecard where sys_card_no = %s"
    for dit in card_dict:
#        print _(u'更新卡余额'),card_dict
        if more_data:
            max_serial = card_dict[dit].split(':')[0]#当前上传记录的卡号最大卡流水号值
            blance = card_dict[dit].split(':')[1]
            max_card_serial = None
            if stamp_name == 'pos_log_stamp' :#上传消费记录 
                obj_con = my_custom_sql(select_issuecard%dit)
                max_con_serial = obj_con[0]
                if int(max_serial) > int(max_con_serial) :
#                    print "pos_log______________________________________"
                    try:
                        obj_card =IssueCard.all_objects.get(sys_card_no = dit)
                        obj_card.blance = blance
                        obj_card.card_serial_num = max_serial
                        obj_card.save(force_update=True,log_msg=False)
                    except:
                        import traceback; traceback.print_exc();
                        pass
            elif stamp_name in ['full_log_stamp','allow_log_stamp']:
                
                obj_con = my_custom_sql(select_issuecard%dit)
                max_con_serial = obj_con[0]
                if int(max_serial) > int(max_con_serial) :
#                    print "full_log***************************************"
                    obj_card =IssueCard.all_objects.get(sys_card_no = dit)
                    obj_card.blance = blance
                    obj_card.card_serial_num = max_serial
                    obj_card.save(force_update=True,log_msg=False)
                    
#                    try:
#                        objsz = CarCashSZ.objects.get(sys_card_no = dit,cardserial = max_sz_serial)
#                    except MultipleObjectsReturned: #拦截优惠充值模式下卡流水号异常
#                        try:
#                            objsz = CarCashSZ.objects.get(sys_card_no = dit,cardserial = max_sz_serial,hide_column=13)#充值优惠记录卡流水号相同
#                        except ObjectDoesNotExist:#拦截退卡的时候数据库中卡流水号重复，导致这里会报错的问题（实际属于正常业务情况）
#                            objsz = None
#                            pass
#                        pass
#                    obj_card = IssueCard.all_objects.get(sys_card_no = dit)
#                    if objsz:
#                        obj_card.blance = objsz.blance
#                    obj_card.save(force_update=True,log_msg=False)
        else:
            if stamp_name in ['full_log_stamp','allow_log_stamp','pos_log_stamp']:#上传单条记录
                try:
                    obj_card = IssueCard.all_objects.get(sys_card_no = dit)
                    obj_card.blance = blance
                    obj_card.save(force_update=True,log_msg=False)
                except:
                    pass
            
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
    c, ec, msg=cdata_post_trans(device,raw_data.splitlines(),stamp_name, head,head_data)
#    print u"成功解析设备上传数据===",msg
    #写入上传记录日志表
    if msg is not None:
        try:
            DevLog(SN=device, Cnt=c, OP=stamp_name, ECnt=ec, Object=msg[:20], OpTime=datetime.datetime.now()).save(force_insert=True)
        except:
            print_exc()
#    return (c, ec+c, msg)

TRANS_QUEQE='TRANS'
STAMPS={'BUYLOG':'pos_log_stamp', 
'FULLLOG': 'full_log_stamp', 
'ALLOWLOG':'allow_log_stamp', 
'TableNameStamp':'table_name_stamp',
'storedetail':'store_detail',
'keydetail':'key_detail',
'timedetail':'time_detail',
'BUYLOGBAK':'pos_log_bak_stamp',
'FULLLOGBAK': 'full_log_bak_stamp', 
'ALLOWLOGBAK':'allow_log_bak_stamp', 
}



def cdata_post(request, device):  
    raw_Data = request.raw_post_data
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
#    try:
#        Auty = request.REQUEST.get('AuthType', None)   
#    except:
#        Auty =None
#    if Auty:
#        from new_push import verification
#        res = verification(Auty,rawData,device)
#        return res

    stamp=request.REQUEST.get("Stamp", None)#设备上传数据时间戳
    table = request.REQUEST.get("table", None)#设备上传数据流水号（20120827重新修订时间戳方式改为根据设备流水号上传）
    stamp_id = request.REQUEST.get("StampId", 0)
    if not (stamp is None):
        stamp_name=STAMPS[table]
    if stamp is None:
        return "UNKNOWN"

    msg=None
    head_data=":%s: SN=%s\tIP=%s\tTIME=%s\tSTAMP=%s\tSTAMPID=%s\tZ=%s"%(stamp_name, str(device.sn).strip(),
        request.META["REMOTE_ADDR"], datetime.datetime.now(),stamp,stamp_id,stamp=='0' and '0' or '1')
    try:
        #s_data="%s\n%s\n\n"%(head_data, rawData.decode(device.lng_encode))
        s_data="%s\n%s\n\n"%(head_data, rawData)
    except:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    #print "settings.WRITEDATA_CONNECTION:%s"%settings.WRITEDATA_CONNECTION
#    print u"设备主动上传的数据",s_data
    if settings.WRITEDATA_CONNECTION>0:
        #写入到队列，后台进程在进行实际的数据库写入操作
        try:
            obj=""
            try:                
                from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata
                from mysite.pos.pos_ic.ic_sync_store import save_pos_file
                if POS_IC_ADMS_MODEL:
                    obj = save_pos_file(device,s_data)
                else:
                    obj=pos_gen_device_cmmdata(device,s_data)
            except Exception, e:
                raise 
        except Exception, e:
            import traceback; traceback.print_exc()
            #raise 
            return "save post data error\n"
        c=1
    else:        
#        c, lc, msg=write_data(s_data, device)
        write_data(s_data, device)
    if hasattr(device, stamp_name): setattr(device, stamp_name, stamp)
#    device.save(force_update=True,log_msg=False)
    return "OK"
