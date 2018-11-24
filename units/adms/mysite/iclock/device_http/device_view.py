# -*- coding: utf-8 -*-

import datetime
import time

from dbapp.utils import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse
from mysite.iclock.models import *
from mysite.iclock.models.modelproc import get_normal_card
from mysite.iclock.models.model_device import device_cmd
from mysite.personnel.models.model_emp import Employee,format_pin
from dbapp.additionfile import save_model_file
import os
from redis_self.server import check_and_start_queqe_server, queqe_server
from traceback import print_exc
from mysite.iclock.models.model_devcmd import DevCmd
from mysite.iclock.models.dev_comm_operate import *
from django.utils.translation import ugettext as _
from network import network_monitor
from mysite.utils import get_option
from mysite.iclock.models.model_face import FaceTemplate
from commen_utils import normal_state, normal_verify, card_to_num, excsql,get_logger
from constant import SYNC_MODEL,ENCRYPT
from constant import DEVELOP_MODEL as develop_model

''' 设备的请求日志 '''
log_path = settings.APP_HOME+"/tmp/dev_post.log"
logger = get_logger(log_path)

''' 设备返回值日志 '''
log_ret_path = settings.APP_HOME+"/tmp/dev_ret.log"
log_ret = get_logger(log_ret_path)

time_fmt = "%Y-%m-%d %H:%M:%S"

if SYNC_MODEL:
    from sync_conv_device import check_device, parse_dev_info
    from sync_conv_emp import cdata_get_pin
else:
    from conv_device import get_device,check_device,sync_dev,check_sync_devs,check_and_save_cache,cdata_get_options, parse_dev_info, deal_pushver
    from conv_emp import cdata_get_pin

from device_response import device_response_write,unknown_device_response,unknown_data_response,ok_response,erro_response,unknown_response

import UrlParas


def write_data(raw_data, device=None,Op=None):
    '''
    解析设备传过来的数据并保存到数据库
    '''
    if develop_model:
        print 'Going to write_data=============\n',raw_data
    import UrlParas
    head_data, raw_data=raw_data.split("\n",1)
    stamp_name, head=head_data.split(": ")
    stamp_name=stamp_name[1:]
    head=dict([item.split("=",1) for item in head.split("\t")])
    if SYNC_MODEL:
        pass
    else:
        if device is None:  #---后处理
            device=get_device(head['SN'])
    msg=None
    c=0
    ec=0
    if stamp_name=='log_stamp': #-------Stamp
        c, ec, msg=UrlParas.cdata_post_trans(device, raw_data, head,head_data)
    elif stamp_name=='oplog_stamp': #----OpStamp
        c, ec, msg=UrlParas.cdata_post_userinfo(device, raw_data,Op, head)
    elif stamp_name=='FPImage':
        c=UrlParas.cdata_post_fpimage(device, raw_data, head)    #---FPImage
    if msg is not None: #---写入上传记录日志表
        if SYNC_MODEL:
            pass
        else:
            try:
                DevLog(SN=device, Cnt=c, OP=stamp_name, ECnt=ec, Object=msg[:20], OpTime=datetime.datetime.now()).save(force_insert=True)
            except:
                import traceback;traceback.print_exc()
    return (c, ec+c, msg)


def make_cmd_data(request,device,stamp_key,stamp_val,rawData):
    '''
    构造内部定义POST命令头 保存到文件或者立即处理入库
    '''
    from protocol_content import STAMPS
    msg=None    #---构造内部定义post命令请求头
    stamp_name = STAMPS[stamp_key]
    stamp = stamp_val
    if stamp_name=='FPImage': 
        head_data=":%s: SN=%s\tIP=%s\tTIME=%s\tPIN=%s\tFID=%s\tFPImage=%s\tZ=%s"%(stamp=='0' and stamp_name+'0' or stamp_name, str(device.sn).strip(),
            request.META["REMOTE_ADDR"], datetime.datetime.now(),
            request.REQUEST["PIN"], request.REQUEST.get("FID",0), request.REQUEST['FPImage'],stamp=='0' and '0' or '1')
    else:
        head_data=":%s: SN=%s\tIP=%s\tTIME=%s\tZ=%s"%(stamp_name, str(device.sn).strip(),
            request.META["REMOTE_ADDR"], datetime.datetime.now(),stamp=='0' and '0' or '1')
    try:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    except:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    if SYNC_MODEL:
        c, lc, msg=write_data(s_data, device)
        setattr(device, stamp_name, stamp) ########更新时间戳
        device.set(stamp_name)
    else:
        if settings.WRITEDATA_CONNECTION>0 and not develop_model:
            try:
                obj=""
                try:                
                    from mysite.iclock.models.model_cmmdata import gen_device_cmmdata
                    obj=gen_device_cmmdata(device,s_data)   #---将整理后的POST数据保存到文件
                except Exception, e:
                    raise 
            except Exception, e:
                import traceback; traceback.print_exc()
                return "save post data error\n"
            c=1
        else:        
            c, lc, msg=write_data(s_data, device)
        if hasattr(device, stamp_name): setattr(device, stamp_name, stamp)
        device.save()
    return "OK:%s\n"%c

def cdata_post(request, device): 
    '''
    处理设备的POST请求
    涉及http参数: "raw_post_data"、stamp_name
    '''
    raw_Data = request.raw_post_data
    if not raw_Data:
        raw_Data = request.META['raw_post_data']
    from setting_proccess import pre_proccess
    rawData = pre_proccess(raw_Data)
#    request.raw_post_data = rawData
#    post_urlPara_handlers.action()

    ######################服务器端验证功能
    Auty = request.REQUEST.get('AuthType', None)   
    if Auty:
        from UrlPara_Auth import verification
        res = verification(request,device,Auty)
        return res
    ###################### stamp相关功能
    stamp = UrlParas.get_request_list(request)
    if stamp:
        stamp_key = stamp[0]
        stamp_val = stamp[1]
        ret =  make_cmd_data(request,device,stamp_key,stamp_val,rawData)
        return device_response_write(ret)
    else:
        return unknown_response()

def cdata_get(request,device):
    '''
    返回用户信息或者设备信息
    '''
    if request.REQUEST.has_key('PIN') or request.REQUEST.has_key('Card'):
        '''异地考勤入口'''
        return cdata_get_pin(request, device)
    else:
        '''服务器下发机器信息(如设备上传标识位)'''
        if SYNC_MODEL:
            alg_ver="1.0"
            if request.REQUEST.has_key('pushver'):
                alg_ver=request.REQUEST.get('pushver')
            device.alg_ver=alg_ver
            device.set("alg_ver")########更新设备版本
            resp =device.get_option()
        else:
            deal_pushver(request,device)
            resp =cdata_get_options(device)
        return device_response_write(resp)

def cdata(request):
    '''
    设备向服务器的http:://xxx/cdata请求
    '''
    from protocol_content import POSDEVICE
    network_monitor(request)
    try:
        device_type = request.REQUEST.get('devicetype')#设备类型参数
        pos_device_type = request.REQUEST.get('device_type',None)#兼容ID消费固件，后期统一使用devicetype
        if(device_type == POSDEVICE or pos_device_type == POSDEVICE):#ID消费机
            from mysite.pos.pos_id.posdevview import pos_cdata
            if get_option("POS_ID"):
                resp = pos_cdata(request)
            else:#防止IC消费软件，连接ID消费机
                from protocol_content import pos_return
                resp = pos_return()
            return device_response_write(resp)
        else:
            device = check_device(request, True,True)    #---检测、验证当前发出请求的设备
            if device is None: 
                return unknown_device_response()
            else:
                if device.deviceType in ['ACP', 'ACD']:#控制器or一体机:
                    from mysite.iaccess.push_comm_center import acc_cdata
                    ret = acc_cdata(request)
                    return device_response_write(ret)
                
                if request.REQUEST.has_key('action'):
                    return ok_response(device)
                elif request.method == 'GET':
                    return cdata_get(request,device)
                elif request.method == 'POST':
                    try:
                        return cdata_post(request, device)
    #                    resp =cdata_post(request, device)
    #                    return device_response_write(resp)
                    except Exception, e:
                        return erro_response(e)
                else:
                    return unknown_data_response(device)
                if not SYNC_MODEL:
                    check_and_save_cache(device)    #----暂为空函数
    except  Exception, e:
        import traceback
        traceback.print_exc()
        return erro_response(e)

def update_device_info(device,info):
    '''
    更新设备信息
    '''
    info = info.split(",")
    device.fw_version=info[0]   #---主版本号
    device.user_count=int(info[1])  #---注册用户数
    device.fp_count=int(info[2])    #---注册指纹数
    device.fp_count=int(info[2])
    device.transaction_count=int(info[3])   #---考勤记录数
    if len(info)>4:
        device.ipaddress=info[4]    #---考勤机IP地址
        if device.alias=="auto_add":
            device.alias=info[4]#由于网关问题，使名称对应的IP地址与机器IP不同时的更正。
    if len(info)>5:             
        device.Fpversion=info[5]   #指纹算法版本
    try:
        device.face_count=int(info[8])
        device.face_tmp_count=int(info[7])
        device.face_ver=info[6]
        if device.face_ver!='5' and device.face_ver!='7':
            device.face_ver=''
    except:
        pass
    try:
        device.push_status='1'+info[9] + '0'*6
    except:
        device.push_status = '0'*10
    if SYNC_MODEL:
        device.set()#触发服务器更新设备信息
    else:
        device.save()
    
def deal_device_active(device):
    '''
    设备状态处理(非SYNC_MODLE才用到)
    '''
    dt_now = datetime.datetime.now()
    device.last_activity = dt_now
    device.cache_device()

    prev_save_time = get_prev_save_time(device)

    if (dt_now -prev_save_time).seconds>300: #五分钟保存一次
        device.save()
        save_last_activity(device)

def getreq_get(request,device):
    '''
    获取设备命令 处理请求中带有设备INFO信息
    '''
    info = request.GET.get("INFO", "")
    if info:
        update_device_info(device,info)
    resp = fetch_cmds(device)
    if develop_model:
        print 'Getting cmds=============\n',resp
    deal_device_active(device)
    
    if settings.ENCRYPT:
        import lzo
        resp = lzo.bufferEncrypt(resp + "\n", device.sn)
    return device_response_write(resp)

def sync_getreq_get(request,device):
    '''
    获取设备命令 处理请求中带有设备INFO信息
    '''
    dt_now = datetime.datetime.now()
    str_now = dt_now.strftime(time_fmt)
    device.last_activity = str_now
    device.set('last_activity')# 设备每次请求命令时更新最后访问时间
    info = request.GET.get("INFO", "")
    if info:
        update_device_info(device,info)
    resp = device.fetch_cmds()
    if develop_model:
        print 'Getting cmds=============\n',resp
    if ENCRYPT:
        import lzo
        resp = lzo.bufferEncrypt(resp + "\n", device.sn)
    return device_response_write(resp)
    
def getreq(request):
    '''
    http://xxx/getrequest
    设备读取服务器上存储的命令
    '''
    network_monitor(request)
    try:
        resp = "" #---要直接发送的内容
        device = check_device(request, True)    #---检测、验证当前发出请求的设备
        if device is None: 
            return unknown_device_response()
        else:        
            if request.method == 'GET':
                if SYNC_MODEL:
                    return sync_getreq_get(request,device)
                else:
                    return getreq_get(request,device)
            elif request.method == 'POST':
                pass
            else:
                return unknown_data_response(device)    
        # 自动升级固件功能
        # ......
    except  Exception, e:
        import traceback;traceback.print_exc()
        resp = u"%s" % e
        return device_response_write(resp)


def check_upload_file(request, data):
    '''
    保存模型相关文件
    '''
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

from cmds_api import post_check_update,update_cmds,update_cmd,update_cached_cmd,fetch_cmds,get_prev_save_time ,save_last_activity

    
def check_att_sum(data,device):
    '''
    考勤校对
    '''
    try:
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
    except:
        pass 

def check_upgradefile(id,data,device,ret):
    '''
    远程固件升级
    '''
    try:
        cmdobj =update_cmd(device, id, ret)
        if not cmdobj:
            flag =  False
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
    except:
        pass 

def devpost(request):
    '''
    http://xxx/devicecmd
    设备返回设备命令执行结果的请求
    '''
    from commen_utils import parse_posts
    network_monitor(request)
    
    device = check_device(request)    #---检测、验证当前发出请求的设备
    if device is None: 
        return unknown_device_response()
    else:        
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            try:
                rd = request.raw_post_data
                if settings.ENCRYPT:    #---解密
                    try:
                        import lzo
                        rawData = lzo.bufferDecrypt(rd, device.sn)
                    except:
                        rawData = rd
                else:
                    rawData = rd
                    
                try:
                    data0 = rawData.decode("gb18030")   #---解码
                except:
                    data0 = rawData
                rets = {}
                pdata = parse_posts(data0)  #---解析,结果为字典的数组
                for apost in pdata: #[CMD,ID,Return]
                    if SYNC_MODEL: 
                        id = apost["ID"]
                    else:
                        id = int(apost["ID"])
                    ret = apost["Return"]   #命令执行返回值
                    if apost["CMD"] == "INFO":#更新设备信息
                        parse_dev_info(device, apost['Content'])
                        if not SYNC_MODEL:
                            device.save()
                        rets[id] = ret
                    elif (apost["CMD"] == "GetFile" or apost["CMD"] == "Shell") and ret > 0:
                        check_upload_file(request, apost)
                        rets[id] = ret
                    elif apost["CMD"] == "VERIFY SUM" and ret > 0:  #考勤校对
                        check_att_sum(apost,device)
                        rets[id] = ret
                    elif apost["CMD"] == "PutFile":
                        check_upgradefile(id,apost,device,ret)
                        post_check_update(device,[ret]) #立即单独更新此处理的开始指针
                        #rets[id] = ret
                    else:#默认情况下CMD为DATA
                        rets[id] = ret
                if len(rets) > 0:
                    if SYNC_MODEL:
                        for e in rets.keys():
                            if rets[e] !=u'0':
                                log_ret.error("errors occurred to update or execute the '%s' on device:%s , return value is '%s'"%(e, device.sn , rets[e]))
                    else:
                        update_cmds(device, rets)
                return device_response_write("OK")
            except:
                import traceback;traceback.print_exc()
                return device_response_write("")
        else:
            return unknown_data_response(device)

from sync_store import save_attphoto
def post_photo(request):
    '''
    http://xxx/fdata
    设备采集现场图片并上传到服务器
    '''
    network_monitor(request)
    device = check_device(request)
    if device is None: 
        return unknown_device_response()
    else:
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
                if 0 and SYNC_MODEL:
                    save_attphoto("%s/%s/%s" % (device.sn, dt[:4], dt[4:8])+"/"+ format_pin(pin)+"_"+ dt[8:] + ".jpg", d, "picture")
                else:
                    from mysite.iclock.models import Transaction
                    save_model_file(Transaction,
                    "%s/%s/%s" % (device.sn, dt[:4], dt[4:8])+"/"+ format_pin(pin)+"_"+ dt[8:] + ".jpg", 
                    d, "picture")
            else:
                return device_response_write("No photo data!\n")
                
            if request.REQUEST.has_key('PhotoStamp'):
                if SYNC_MODEL:
                    device.photo_stamp = request.REQUEST['PhotoStamp']
                    device.set('photo_stamp')#####更新考勤照片时间戳
                else:
                    DevLog(SN=device, Cnt=1, OP=u"PICTURE", Object=pin, OpTime=datetime.datetime.now()).save()
                    device.photo_stamp = request.REQUEST['PhotoStamp']
                    device.save()
                
            #check_and_save_cache(device)
        except:
            pass
        return device_response_write("OK\n")