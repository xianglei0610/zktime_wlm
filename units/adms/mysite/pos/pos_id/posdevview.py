# -*- coding: utf-8 -*-
import datetime
import time
import os
from dbapp.utils import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections, IntegrityError, DatabaseError, models
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
#from dataprocaction import append_dev_cmd
from base.cached_model import STATUS_PAUSED, STATUS_STOP
from traceback import print_exc
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _

from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
from mysite.pos.models.model_carcashsz import CarCashSZ
from mysite.personnel.models.model_meal import Meal
from mysite.pos.models.model_timeslice import TimeSlice
from mysite.pos.models.model_splittime import SplitTime
from mysite.pos.models.model_carcashtype import CarCashType
from mysite.iclock.models.model_dininghall import Dininghall
from mysite.pos.models.model_merchandise import Merchandise
from mysite.pos.models.model_keyvalue import KeyValue
from mysite.pos.models.model_batchtime import BatchTime
from mysite.pos.models.model_cardmanage import CardManage
from mysite.pos.models.model_errors import Errors
from decimal import Decimal
from mysite.pos.models.model_timebrush import TimeBrush
from django.db import transaction
from django.core.cache import cache
from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_VALID
from mysite.pos.pos_constant import TIMEOUT,POS_DEBUG
from mysite.personnel.models.model_emp import Employee,getuserinfo,get_dept
from mysite.pos.models.model_loseunitecard import LoseUniteCard
from mysite.iclock.models.dev_comm_operate import update_pos_device_info,sync_delete_user,sync_delete_user_privilege,sync_delete_user,sync_report_user,delete_pos_device_info
from mysite.utils import get_option
def device_response(msg=""): #生成标准的设备通信响应头
    response = HttpResponse(mimetype='text/plain')  #文本格式
    response["Pragma"]="no-cache"                   #不要缓存，避免任何缓存，包括http proxy的缓存
    response["Cache-Control"]="no-store"            #不要缓存
    if msg:
        response.write(msg)
    return response

#根据设备sn找对应的设备对象
def get_posdevice(request,allow_create=False):
    from mysite.iclock.models.model_device import Device
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
    try:
        device=Device.objects.get(sn=sn)
    except:
        device=None
    return device
#    if device:
#        device.last_activity=datetime.datetime.now()
#        if request.REQUEST.has_key('fversion'):
#            fversion = request.REQUEST.get('fversion')
#            device.fw_version =fversion
#        if request.REQUEST.has_key('devicename'):
#            devicename = request.REQUEST.get('devicename')
#            device.device_name = devicename
#        return device
#    else:
#        return None
    
def read_timebrush(cardno):
    cf_path = (settings.WORK_PATH + "/files/zkpos/pos_timebrush/").replace('\\','/')
    if not os.path.exists(cf_path):
        os.makedirs(cf_path)
    filename=cf_path+'%s.txt'%(cardno)
    if os.path.exists(filename):
        try:
            f = open(filename,'r')
            content  = f.read().strip()
        except Exception,e:
            pass
        finally:
            f.close()
        if content:
            return content
        else:
            return False
    else:
        return False
        
''' 
1:计时开始
2：计时结束
3：计时开始回滚
4：计时结束回滚
'''    
def get_timebrush_from_txt(cardno,flag):
    cf_path = (settings.WORK_PATH + "/files/zkpos/pos_timebrush/").replace('\\','/')
    if not os.path.exists(cf_path):
        os.makedirs(cf_path)
    filename=cf_path+'%s.txt'%(cardno)
    strnowtime=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    content=None
    if os.path.exists(filename):
        try:
            f = open(filename,'r+')
            content  = f.read().strip()
            if flag=='1':
               strvalue=flag+":"+strnowtime
            elif flag=='2':
               list_val= content.split(':')
               strvalue = flag+":"+list_val[1]+":"+strnowtime
            if flag=='3':
               strvalue="3"
            if flag=='4':
               list_val= content.split(':')
               strvalue = '1'+":"+list_val[1]
            f.seek(0)
            f.write(str(strvalue))
        finally:
            f.close()
    else:
        try:  
            f = open(filename,'w')
            strvalue=flag+":"+strnowtime
            f.write(strvalue)
        finally:
            f.close()
    return content
    
#缓存设置
def cache_device(sn,device):
    cache.set(sn,device,TIMEOUT)
def get_cache_device(request,key):
    dev = cache.get(key)
    if dev==None:
        device = get_posdevice(request,True)
        cache.set(key,device,TIMEOUT)
        dev =device
    return dev

#获取餐别缓存
def get_cache_meal():
    cacheobj = cache.get("Meal")
    if not cacheobj and not type(cacheobj)==list:
        cacheobj = Meal.objects.all().filter(available=1)
        cache.set("Meal",list(cacheobj),TIMEOUT)
    return cacheobj
#获取当前餐别
def get_now_meal():
    timenow = datetime.datetime.now().time()
    mealobj = get_cache_meal()
    for obj in mealobj:
        if obj.starttime<=timenow and obj.endtime>=timenow:
            return obj

#获取消费时间段缓存
def get_cache_batchtime(code):
    key="BatchTime_"+str(code)
    cacheobj = cache.get(key)
    if not cacheobj and not type(cacheobj)==list:
        cacheobj = BatchTime.objects.filter(code=code,isvalid=1)
        cache.set(key,list(cacheobj),TIMEOUT)
    return cacheobj

#获取当前消费时间段
def get_now_batchtime(code):
    timenow = datetime.datetime.now().time()
    batchlobj = get_cache_batchtime(code)
    for obj in batchlobj:
        if obj.starttime<=timenow and obj.endtime>=timenow:
            return obj


#获取分段定值信息缓存
def get_cache_splittime():
    cacheobj = cache.get("SplitTime")
    if not cacheobj and not type(cacheobj)==list:
        cacheobj = SplitTime.objects.all().filter(isvalid=1)
        cache.set("SplitTime",list(cacheobj),TIMEOUT)
    return cacheobj

#获取商品信息缓存
def get_cache_merchandise():
    cacheobj = cache.get("Merchandise")
    if not cacheobj and not type(cacheobj)==list:
        cacheobj = Merchandise.objects.all()
        cache.set("Merchandise",list(cacheobj),TIMEOUT)
    return cacheobj

#设置管理卡信息缓存
def set_cache_cardmanage(device):
#    cacheobj = cache.get("CardManage")
#    if not cacheobj and not type(cacheobj)==list:
    from mysite.pos.models.model_cardmanage import CardManage
    cacheobj = CardManage.objects.filter(cardstatus = CARD_VALID,dining = device.dining)
    cache.set("CardManage",list(cacheobj),TIMEOUT)
    for obj in cacheobj:
       iskey="CardManage_%s_%s" %(device.dining_id,obj.card_no)
       cache.set(iskey,obj,TIMEOUT)
    return cacheobj

#获取管理卡
def get_cache_cardmanage(key,device):
    manageKey="CardManage_%s_%s" %(device.dining_id,key)
    cacheobj = cache.get(manageKey)
    if cacheobj==None:
       try:
         from mysite.pos.models.model_cardmanage import CardManage
         obj=CardManage.objects.get(card_no = key)
       except:
         obj=None
       if obj:
           iskey="CardManage_%s_%s" %(device.dining_id,key)
           cache.set(iskey,obj,TIMEOUT)
           cacheobj = obj
    return cacheobj
    

#获取错误信息缓存
def get_cache_errors():
    cacheobj = cache.get("Errors")
    if not cacheobj and not type(cacheobj)==list:
       cacheobj = Errors.objects.all()
       cache.set("Errors",list(cacheobj),TIMEOUT)
    return cacheobj

#获取键值信息缓存
def get_cache_keyvalue():
    cacheobj = cache.get("KeyValue")
    if not cacheobj and not type(cacheobj)==list:
        cacheobj = KeyValue.objects.all()
        cache.set("KeyValue",list(cacheobj),TIMEOUT)
    return cacheobj

def get_cache_issuecard(key):
    cacheobj = cache.get(key)
    if cacheobj==None:
       cadno=key.split('_')[1]
       try:
         obj=IssueCard.objects.get(cardno=int(cadno))
       except:
         obj=None
       if obj:
           iskey="IssueCard_"+obj.cardno
           cache.set(iskey,obj,TIMEOUT)
           cacheobj = obj
    return cacheobj

#缓存卡信息
def set_cache_issucard():
    carcache = cache.get("ALLIssueCard")
    if not carcache and not type(carcache)==list:
        cache_log_msg(u"获取卡信息开始")
        allcard = IssueCard.objects.all()
        cache_log_msg(u"获取卡信息结束")
        cache.set("ALLIssueCard","tag_ALLIssueCard",TIMEOUT)
        for obj in allcard:
           iskey="IssueCard_%s" %obj.cardno
           cache.set(iskey,obj,TIMEOUT)
        
#ICcard 获取卡类信息缓存
def get_cache_iccard(key):
    cacheobj = cache.get(key)
    if cacheobj==None:
       for obj in ICcard.objects.all():
           iskey="ICcard_%s" %obj.pk
           cache.set(iskey,obj,TIMEOUT)
       cacheobj = cache.get(key)
    return cacheobj


#CarCashSZ 卡收支表信息缓存
def get_cache_carcashsz(sn,sequ):
    iskey="CarCashSZ_"+sequ+sn 
    cacheobj = cache.get(iskey)
    if cacheobj==None:
       obj=CarCashSZ.objects.filter(serialnum=sequ,sn_name=sn,type=CarCashType.objects.get(id=6))
       if obj:
           iskey="CarCashSZ_%s%s" %(obj[0].serialnum,obj[0].sn_name)
           cache.set(iskey,obj[0],3600)
           cacheobj = obj[0]
    return cacheobj

import sys 
#from time import ctime 
is_log=True
 
def log_msg(card,msg,self=None,file_name='/tmp/trace.log'): 
        import codecs
        path=settings.APP_HOME.replace('\\','/')
        debug_file_name = path+file_name
        if card=="3342382142" or card=="2788227628":
            if is_log==False: 
                return
            try: 
                raise Exception 
            except: 
                f = sys.exc_info()[2].tb_frame.f_back 
                fp=codecs.open(debug_file_name,'a','utf-8')
                if self is None: 
                    fp.write('['+datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f")+']<'+f.f_code.co_name+'>'+str(f.f_lineno)+':') 
                else: 
                    fp.write('['+datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f")+']<'+self.__class__.__name__+'.'+f.f_code.co_name+'>'+str(f.f_lineno)+':') 
                fp.write(unicode(msg, 'utf-8')+card+'\r\n') 
                fp.close()

def cache_log_msg(msg,self=None,file_name='/tmp/select.log'): 
        import codecs
        path=settings.APP_HOME.replace('\\','/')
        debug_file_name = path+file_name
        if is_log==False: 
            return
        try: 
            raise Exception 
        except: 
            f = sys.exc_info()[2].tb_frame.f_back 
            fp=codecs.open(debug_file_name,'a','utf-8')
            if self is None: 
                fp.write('['+datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f")+']<'+f.f_code.co_name+'>'+str(f.f_lineno)+':') 
            else: 
                fp.write('['+datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f")+']<'+self.__class__.__name__+'.'+f.f_code.co_name+'>'+str(f.f_lineno)+':') 
            fp.write(msg+'\r\n') 
            fp.close()

def pos_write_log(str,sn,cardno):
        import codecs,os,sys
        if POS_DEBUG:
            try:
                dt=datetime.datetime.now()
                path=settings.APP_HOME.replace('\\','/') + '/tmp/zkpos/poslog/%s/%s/'%(sn,datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(path):
                    os.makedirs(path)
                mfile=path+'poslog_%s_%s_%s.txt'%(datetime.datetime.now().strftime("%Y-%m-%d"),sn,cardno)
                f=codecs.open(mfile,'a','utf-8')
                wstr='RESPONSE-%s-%s\r\n'%(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f"),str)
                f.write(wstr)
                f.close()
            except:
                print_exc()
                pass


#设备读取配置信息、或者主动向服务器发送的数据

#获取系统信息
def pos_data(request):
    try:
        resp = ""
        from mysite import authorize_fun
        language=request.REQUEST.get('language',None)
        datatype = request.REQUEST.get('datatype')
        charcode = request.REQUEST.get('char_code')
        sn = request.REQUEST.get('SN')
        urlcon = request.build_absolute_uri()
        device = get_cache_device(request,sn)
        if not device: 
            #设备不存在  设备未注册
            resp+="Ret=No\nretnumber=208\nerrmsg=%s"%_(u"设备不存在")
            return resp.encode('GB18030')
        elif datatype=='3':#获取键值信息
            try:
                objkv = get_cache_keyvalue()
                if objkv:
                    count = len(objkv)
                    resp+="Ret=OK\nrecordcount=%s\n" %count
                    for obj in objkv:
                        resp+="keyid=%s\tmoney=%s\n" %(obj.code,obj.money*100)
                    save_posdev_cmd(sn,None,None,None,20,urlcon,resp[0:100],0)
                else:#没有数据
                    resp+="Ret=OK\nrecordcount=0"
                    save_posdev_cmd(sn,None,None,None,20,urlcon,resp,300)
            except:
                resp+="Ret=NO\nretnumber=-1"
                save_posdev_cmd(sn,None,None,None,20,urlcon,resp,-1)
        elif datatype=='1':#获取系统时间
            try:
                key = str(device.sn).strip()+"_update_db"
                newrecord = cache.get(key)
                if device:
                    device.last_activity= datetime.datetime.now()
                    device.save(force_update=True,log_msg=False)
                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                resp+="Ret=OK\ndatetime=%s\nnewrecord=%s" %(dtime,newrecord or 0)
                cache.set(key,0,TIMEOUT)
#                save_posdev_cmd(sn,None,None,None,16,urlcon,resp,0)
            except:
                resp+="Ret=NO\nretnumber=-1"
#                save_posdev_cmd(sn,None,None,None,16,urlcon,resp,-1)
        
        elif datatype=='5':#获取商品信息
            try:
#                objmer = Merchandise.objects.all()
                objmer = get_cache_merchandise()
                if objmer:
                    count = len(objmer)
                    resp+="Ret=OK\nrecordcount=%s\n" % count
                    for obj in objmer:
                        resp+="storeno=%s\tstorename=%s\tbarcode=%s\tprice=%s\tagio=%s\n" %(obj.code,obj.name,obj.barcode,obj.money*100,obj.rebate)
                    save_posdev_cmd(sn,None,None,None,21,urlcon,resp[0:100],0)
                else:
                    resp="Ret=OK\nrecordcount=0"
                    save_posdev_cmd(sn,None,None,None,21,urlcon,resp,300)
            except:
                resp+="Ret=NO\nretnumber=-1"
                save_posdev_cmd(sn,None,None,None,21,urlcon,resp,-1)
        elif datatype=='2':#下载管理卡信息
            try:
#                objmana = CardManage.objects.all()
                objmana = set_cache_cardmanage(device)
                if objmana:
                    count = len(objmana)
                    resp+="Ret=Ok\nrecordcount=%s\n" %count
                    for obj in objmana:
                        resp+="cardno=%s\tpasswd=%s\tprivage=%s\n" %(obj.card_no,obj.pass_word,obj.card_privage)
                    save_posdev_cmd(sn,None,None,None,17,urlcon,resp[0:100],0)
                else:
                    resp+="Ret=OK\nrecordcount=0"
                    save_posdev_cmd(sn,None,None,None,17,urlcon,resp,300)
            except:
                resp+="Ret=NO\nretnumber=-1"
                save_posdev_cmd(sn,None,None,None,17,urlcon,resp,-1)
        elif datatype=='6':#下载消费错误信息
            try:
#               objmana = Errors.objects.all()
               objmana = get_cache_errors()
               if objmana:
                   count = len(objmana)
                   resp+="Ret=OK\nrecordcount=%s\n" %count
                   for obj in objmana:
                       resp+="errno=%s\terrmsg=%s\n" %(obj.errno,obj.errmsg)
                   save_posdev_cmd(sn,None,None,None,18,urlcon,resp[0:100],0)
               else:
                   resp+="Ret=OK\nrecordcount=0"
                   save_posdev_cmd(sn,None,None,None,18,urlcon,resp,300)
            except:
               resp+="Ret=NO\nretnumber=-1"
               save_posdev_cmd(sn,None,None,None,18,urlcon,resp,-1)
        return resp.encode('GB18030')
    except  Exception, e:
            errorLog(request)
            err = u"%s" % e
            resp+="Ret=NO\nretnumber=-1"
            save_posdev_cmd(sn,None,None,None,18,urlcon,err,-1)
            
            
#消费机联机信息初始化
def pos_cdata(request):
    resp = ""
    from mysite import authorize_fun
    language=request.REQUEST.get('language',None)
    deviceType = request.REQUEST.get('device_type')#设备类型参数
    datatype = request.REQUEST.get('datatype')
    charcode = request.REQUEST.get('char_code')
    sn = request.REQUEST.get('SN')
    try:
        device = get_cache_device(request,sn)
        set_cache_issucard()#添加卡信息缓存
        if not device: 
            #设备不存在  设备未注册
            resp+="Ret=No\nretnumber=208\nerrmsg=%s" % _(u"设备不存在")
            return resp.encode('GB18030')
        else:
            alg_ver="1.0"
            if request.REQUEST.has_key('pushver'):
                alg_ver=request.REQUEST.get('pushver')    #2010-8-25  device字段alg_ver用来区分新老固件  >=2.0为新固件，默认为旧固件
            device.alg_ver=alg_ver
            if request.REQUEST.has_key('fversion'):
                fversion = request.REQUEST.get('fversion')
                device.fw_version =fversion
            if request.REQUEST.has_key('devicename'):
                devicename = request.REQUEST.get('devicename')
                device.device_name = devicename
            device.ipaddress = request.META["REMOTE_ADDR"]
            device.save(force_update=True,log_msg=False)
            resp+=cdata_get_PosOptions(device)
            return resp.encode('GB18030')
           
    except  Exception, e:
        errorLog(request)
        err = u"sysError-------%s" % e
        sn = request.REQUEST.get('SN')
        save_posdev_cmd(sn,None,None,None,None,request.build_absolute_uri(),err,-1)#保存设备通讯日志        
        pos_write_log(err,sn,None)
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        return resp
    
#消费回滚
def reback(request):
    urlcon=request.build_absolute_uri()
    try:
        resp=""
        from mysite.personnel.models.model_issuecard import IssueCard
        sequ= request.REQUEST.get('sequ')
        card= int(request.REQUEST.get('card'))
        sn = request.REQUEST.get('SN')
        postype = request.REQUEST.get('postype')
        if request.REQUEST.get('posmoney'):
            posmoney = int(request.REQUEST.get('posmoney'))
            pommey = Decimal(str(round(posmoney/100.00,2)))
        objcard = get_cache_issuecard("IssueCard_"+str(card))
        iccardobj = get_cache_iccard("ICcard_"+str(objcard.type_id))
        device = get_cache_device(request,sn)
        cache.set(card,card,5)
        if postype =='6':#计时回滚
#            objbatch = get_cache_timebrush(sequ,card)
            objbatch = read_timebrush(card)
            type=objbatch.split(':')[0]
            if type<>'3':
                type=objbatch.split(':')[0]
                if type =='1':#计时开始回滚
                    resp=reback_set_card_param(request,postype,objcard,0,iccardobj,type,sn,card)
                    get_timebrush_from_txt(card,'3')
                    resp+="Ret=Ok"
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                    save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,0,objcard.blance)#保存计时开始回滚记录
                    return resp
                else:#计时结束回滚
                    objsz=get_cache_carcashsz(sn,sequ)
                    if objsz:
                        if(sn==objsz.sn_name and sequ==objsz.serialnum and objsz.type_id==9):
                            resp+="Ret=Ok"
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                            save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,objsz.money,objsz.blance)#保存计时扣费回滚记录
                            return resp
                        else:
                            resp=reback_set_card_param(request,postype,objcard,pommey,iccardobj,type,sn,card)
                            newblance = objcard.blance+objsz.money
                            objcard.blance=newblance
                            objcard.save(force_update=True,log_msg=False)
                            get_timebrush_from_txt(card,'4')
                            CarCashSZ(user_id=objcard.UserID_id,
                                     dept_id = get_dept(objcard.UserID_id).id,
                                     card = card,
                                     serialnum=sequ,
                                     checktime=datetime.datetime.now(),
                                     type=CarCashType.objects.get(id=9),
                                     money=objsz.money,
                                     sn_name = sn,
                                     discount=objsz.discount,
                                     hide_column=9,
                                     dining = device.dining,
                                     blance=newblance,).save(force_insert=True,log_msg=False)
                            resp+="Ret=Ok"
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                            save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,objsz.money,newblance)#保存计时扣费回滚记录
                            return resp
                    else:
                         resp+="Ret=Ok"
                         save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,212)#没有消费记录
                         return resp
                     
            else:
                resp+="Ret=Ok"
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,212)#没有消费记录
                return resp
           
        elif postype =='4':
            objsz=get_cache_carcashsz(sn,sequ)
            if objsz:
               if(sn==objsz.sn_name and sequ==objsz.serialnum and objsz.type_id==12):
                    resp+="Ret=Ok"
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                    save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,objsz.money,objsz.blance)#保存计次回滚记录
                    return resp
               else:
                   resp=reback_set_card_param(request,postype,objcard,0,iccardobj,None,sn,card)
                   CarCashSZ(user_id=objcard.UserID_id,
                            dept_id = get_dept(objcard.UserID_id).id,
                            card = card,
                            serialnum=sequ,
                            checktime=datetime.datetime.now(),
                            type=CarCashType.objects.get(id=12),#计次回滚
                            money=objsz.money,
                            sn_name = sn,
                            discount=0,
                            dining = device.dining,
                            hide_column=12,
                            blance=objsz.blance).save(force_insert=True,log_msg=False)
                   resp+="Ret=Ok"
                   save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                   save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,objsz.money,objsz.blance)#保存计次回滚记录
                   return resp
            else:
               resp+="Ret=Ok"
               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,212)#没有消费记录
               return resp
        else:
            objsz=get_cache_carcashsz(sn,sequ)
            if objsz:
                if(sn==objsz.sn_name and sequ==objsz.serialnum and objsz.type_id==9):
                    resp+="Ret=Ok"
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                    save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,7,objsz.money,objsz.blance)#保存消费回滚记录
                    return resp
                else:
                    resp=reback_set_card_param(request,postype,objcard,objsz.money,iccardobj,None,sn,card)
                    newblance = objcard.blance+objsz.money
                    objcard.blance=newblance
                    objcard.save(force_update=True,log_msg=False)
                    CarCashSZ(user_id=objcard.UserID_id,
                             dept_id = get_dept(objcard.UserID_id).id,
                             card = card,
                             serialnum=sequ,
                             checktime=datetime.datetime.now(),
                             type=CarCashType.objects.get(id=9),#消费回滚
                             money=objsz.money,
                             sn_name = sn,
                             discount=objsz.discount,
                             hide_column=9,
                             dining = device.dining,
                             blance=newblance,).save(force_insert=True,log_msg=False)#新增消费记录
                    resp+="Ret=Ok"
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,120)#回滚成功
                    save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,7,objsz.money,newblance)#保存消费回滚记录
                    return resp 
            else:
                resp+="Ret=Ok"
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,12,urlcon,resp,212)#没有消费记录
                return resp
        return resp.encode('GB18030')
    except Exception, e:
            errorLog(request)
            err = u"%s" % e
            resp+="Ret=Ok"
            save_posdev_cmd(sn,None,None,None,12,urlcon,err,-1)
            return resp
    
    
#设备参数修改
def set_options(request):
    try:
        resp=""
        sn = request.REQUEST.get('SN')
        consmod = request.REQUEST.get('Consmod')
        fixmoney = request.REQUEST.get('FixMoney')
        timeSegMod = request.REQUEST.get('TimeSegMod')
        getIntmod = request.REQUEST.get('GetIntmod')
        hourPrice = request.REQUEST.get('HourPrice')
        device = get_cache_device(request,sn)
        urlcon=request.build_absolute_uri()      
        if not device: 
            #设备不存在  设备未注册
            resp+="Ret=No\nbalance=0\nretnumber=208\nerrmsg=%s" %_(u"设备不存在")
            save_posdev_cmd(sn,None,None,None,13,urlcon,resp,208)
            return resp.encode('GB18030')
        if timeSegMod=='1':
            device.dz_money=None
            device.consume_model=1
            device.save(force_update=True,log_msg=False)
            resp+="Ret=OK\nretnumber=0"
            save_posdev_cmd(sn,None,None,None,13,urlcon,resp,0)
        elif timeSegMod=='0':
            device.dz_money=Decimal(str(round(int(fixmoney)/100.00,2)))
            device.consume_model=1
            device.save(force_update=True,log_msg=False)
            resp+="Ret=OK\nretnumber=0"
            save_posdev_cmd(sn,None,None,None,13,urlcon,resp,0)
        elif getIntmod is not None:#计时模式参数
            device.time_price = Decimal(str(round(int(hourPrice)/100.00,2)))
            device.long_time = getIntmod
            device.save(force_update=True,log_msg=False)
            resp+="Ret=OK\nretnumber=0"
            save_posdev_cmd(sn,None,None,None,13,urlcon,resp,0)
        else:
            device.consume_model = int(consmod)
            device.save(force_update=True,log_msg=False)
            resp+="Ret=OK\nretnumber=0"
            save_posdev_cmd(sn,None,None,None,13,urlcon,resp,0)
        return resp.encode('GB18030')
    except Exception, e:
        errorLog(request)
        err = u"%s" % e
        resp+="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        save_posdev_cmd(sn,None,None,None,13,urlcon,err,-1)
        return resp
    

def cdata_get_PosOptions(device):
        import time
        resp = ""
        resp += "Ret=OK\nConsmod=%s\t" % device.consume_model
#        objsplit = SplitTime.objects.filter(isvalid=1)
        objsplit = get_cache_splittime()
        i=0
        if device.dz_money is not None:
            resp += "FixMoney=%s\tTimeSegMod=0\t"% int(device.dz_money*100)
        else:
            resp += "FixMoney=0\tTimeSegMod=1\t"
        if objsplit:
            for obj in objsplit :
                i+=1
                resp += "TimeSeg%s=%s%s-%s\t" % (i,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':',''),obj.fixedmonery*100)
        while i<8:
              i+=1
              resp +="TimeSeg%s=0\t" % i
        resp += "GetIntmod=%s\t" % device.long_time
        resp += "HourPrice=%s" % int(device.time_price*100)
        return resp

def querytype_action(request,device,objcard,sn,sequ,card,managecard):
    resp=""
    querytype= request.REQUEST.get('querytype')
    password = request.REQUEST.get('password')
    try:
        if objcard:
            oldpassword = objcard.Password
        urlcon=request.build_absolute_uri()
        if querytype =='11':#挂失卡
            if  managecard: 
                resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                save_posdev_cmd(sn,sequ,None,card,14,urlcon,resp,4)
                return  resp
            elif  not objcard: 
                #卡不存在
                resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
                save_posdev_cmd(sn,sequ,None,card,14,urlcon,resp,2)
                return resp
            elif(objcard.cardstatus=='3'):#黑名单 挂失
                resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,14,urlcon,resp,1)
                return resp
            elif objcard.cardstatus=='2':#无效卡
                resp+="Ret=NO\nretnumber=2\nerrmsg=%s" %_(u"无效卡")
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,14,urlcon,resp,2)
                return resp
            elif objcard.cardstatus=='5':#停用卡
                resp+="Ret=NO\nretnumber=2\nerrmsg=%s" %_(u"停用卡")
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,14,urlcon,resp,5)
                return resp
            
            elif(oldpassword==password):
                resp+="Ret=OK\nretnumber=0"
                objcard.cardstatus='3'
                objcard.save(force_update=True,log_msg=False)
#                objcard.sys_emp_card()
                LoseUniteCard(UserID = objcard.UserID,
                             cardno = objcard.cardno,
                             type = objcard.type,
                             cardstatus='3',
                             time = datetime.datetime.now()).save()
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,14,urlcon,resp,0)
                
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
                return resp
            else:
                resp+="Ret=NO\nretnumber=216\nerrmsg=%s"%_(u"密码错误")
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,14,urlcon,resp,216)
                return resp
        elif querytype =='12':#解挂卡
             if  managecard: 
                 resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                 save_posdev_cmd(sn,sequ,None,card,7,urlcon,resp,4)
                 return  resp
             elif  not objcard: 
                #卡不存在
                resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
                save_posdev_cmd(sn,sequ,None,card,7,urlcon,resp,2)
                return resp
#            elif(objcard.cardstatus=='3'):#黑名单
#                resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100)
#                save_posdev_cmd(sn,sequ,card,7,urlcon,resp,1)
#                return resp
             elif objcard.cardstatus=='2':
                    resp+="Ret=NO\nretnumber=2\nerrmsg=%s" %_(u"无效卡")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,7,urlcon,resp,2)
                    return resp
             elif(oldpassword==password):
               resp+="Ret=Ok\nretnumber=0"
               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,7,urlcon,resp,0)
               objcard.cardstatus='1'
               objcard.save(force_update=True,log_msg=False)
#               objcard.sys_emp_card()
               LoseUniteCard(UserID = objcard.UserID,
                            cardno = objcard.cardno,
                            type = objcard.type,
                            cardstatus='1',
                            time = datetime.datetime.now()).save()
               
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
               return resp
             else:
               resp+="Ret=No\nretnumber=216\nerrmsg=%s"%_(u"密码错误")
               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,7,urlcon,resp,216)
               return resp
            
        elif querytype == '13':#修改密码
                newpass = request.REQUEST.get('newpwd')
                oldpwd = request.REQUEST.get('oldpwd')
                if  managecard: 
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                    save_posdev_cmd(sn,sequ,None,card,15,urlcon,resp,4)
                    return  resp
                elif  not objcard: 
                #卡不存在
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
                    save_posdev_cmd(sn,sequ,None,card,15,urlcon,resp,2)
                    return resp
                elif(objcard.cardstatus=='3'):#黑名单
                    resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,15,urlcon,resp,1)
                    return resp
                elif objcard.cardstatus=='2':#无效卡
                    resp+="Ret=NO\nretnumber=2\nerrmsg=%s" % _(u"无效卡")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,15,urlcon,resp,2)
                    return resp    
                elif(oldpwd==oldpassword):
                    objcard.Password=newpass
                    objcard.save(force_update=True,log_msg=False)
                    resp+="Ret=Ok\nretnumber=0"
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,15,urlcon,resp,0)
                    return resp
                else:
                    resp+="Ret=No\nretnumber=216\nerrmsg=%s"%_(u"密码错误")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,15,urlcon,resp,216)
                    return resp
        elif querytype == '1':#余额查询
                if  managecard: 
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                    save_posdev_cmd(sn,sequ,None,card,8,urlcon,resp,4)
                    return  resp
                elif  not objcard: 
                #卡不存在
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s"%(sequ,_(u"无效卡"))
                    save_posdev_cmd(sn,sequ,None,card,8,urlcon,resp,2)
                    return resp
                elif(objcard.cardstatus=='3'):#黑名单
                    resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,urlcon,resp,1)
                    return resp
                elif objcard.cardstatus=='2':#无效卡
                    resp+="Ret=NO\nretnumber=2\nerrmsg=%s" %_(u"无效卡")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,urlcon,resp,2)
                    return resp    
                elif objcard.cardstatus=='5':#停用卡
                    resp+="Ret=NO\nretnumber=2\nerrmsg=%s" %_(u"停用卡")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,urlcon,resp,5)
                    return resp
                
                else:
                    blance = objcard.blance*100
                    resp+="Ret=OK\nbalance=%s\nusername=%s" %(blance,getuserinfo(objcard.UserID_id,"EName"))
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,8,urlcon,resp,0)
                    return resp
        elif querytype == '2':#个人消费明细查询
                if  managecard: 
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                    save_posdev_cmd(sn,sequ,None,card,9,urlcon,resp,4)
                    return  resp
                elif  not objcard: 
                 #卡不存在
                     resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
                     save_posdev_cmd(sn,sequ,None,card,9,urlcon,resp,2)
                     return resp
                elif(objcard.cardstatus=='3'):#黑名单
                     resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
                     save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,urlcon,resp,1)
                     return resp
                elif objcard.cardstatus=='2':#无效卡
                    resp+="Ret=NO\nretnumber=2\nerrmsg=%s"%_(u"无效卡")
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,urlcon,resp,2)
                    return resp    
                else:
                    try:
                        start = request.REQUEST.get('start')
                        end = request.REQUEST.get('end')
                        starttime = datetime.datetime.strptime(start,"%Y%m%d%H%M%S")
                        endtime = datetime.datetime.strptime(end,"%Y%m%d%H%M%S")
                        from mysite.pos.models.model_poslog import PosLog
                        allpos = PosLog.objects.filter(posOpTime__lte=endtime,posOpTime__gte=starttime,sn=sn,carno=card).order_by("-posOpTime")[:100]
                        if allpos:
                            count =allpos.count()
                            resp+="Ret=OK\nrecordcount=%s\nusername=%s\n" %(count,getuserinfo(objcard.UserID_id,"EName"))
                            for obj in allpos:
                                postime = obj.posOpTime.strftime("%Y%m%d%H%M%S")
                                if obj.posmodel==4:
                                    resp+="postime=%s\tposmoney=%s\tbalance=%s\tpostype=%s\n" % (postime,1,0,obj.posmodel)
                                else:
                                    posmoney = obj.posmoney*100
                                    blance = obj.blance*100
                                    postype = obj.posmodel
                                    resp+="postime=%s\tposmoney=%s\tbalance=%s\tpostype=%s\n" % (postime,posmoney,blance,postype)
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,urlcon,resp,0)
                            return resp
                        else:#无记录
                            resp+="Ret=OK\nrecordcount=0\nusername=%s\n"%getuserinfo(objcard.UserID_id,"EName")
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,urlcon,resp,212)
                            return resp 
                    except Exception,e:
                            errorLog(request)
                            resp+="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
                            err = u"%s" % e
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,9,urlcon,err,-1)
                            return resp    
        elif querytype=='3':#个人汇总查询
                if  managecard: 
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
                    save_posdev_cmd(sn,sequ,None,card,10,urlcon,resp,4)
                    return  resp
                elif  not objcard: 
                #卡不存在
                    resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
                    save_posdev_cmd(sn,sequ,None,card,10,urlcon,resp,2)
                    return resp
                elif(objcard.cardstatus=='3'):#黑名单
                    resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,urlcon,resp,1)
                    return resp
                elif objcard.cardstatus=='2':#无效卡
                   resp+="Ret=NO\nretnumber=2\nerrmsg=%s"% _(u"无效卡")
                   save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,urlcon,resp,2)
                   return resp    
                else:
                    try:
                        start = request.REQUEST.get('start')
                        end = request.REQUEST.get('end')
                        starttime = datetime.datetime.strptime(start,"%Y%m%d%H%M%S")
                        endtime = datetime.datetime.strptime(end,"%Y%m%d%H%M%S")
                        from mysite.pos.models.model_poslog import PosLog
                        from mysite.pos.pos_id.id_posdevview_sql import get_id_emp_query
                        from mysite.sql_utils import get_sql_exe_result
                        sql = get_id_emp_query(card,starttime,endtime,sn)
                        allpos = get_sql_exe_result(sql)
#                        allpos = CarCashSZ.objects.filter(checktime__lte=endtime,checktime__gte=starttime,sn_name=sn,card=card,type__in=[6,8,9,10,12]).values_list('type_id','money')
                        gathermoney = 0
                        pos_money = 0
                        rebackmoney = 0
                        pos_count = 0
                        back_count = 0
                        gather_count = 0
                        if allpos:
                            for obj in allpos:
                               if obj[0]==6 or obj[0]==8 or obj[0]==10:
                                   posmoney = obj[1]*100
                                   pos_money += posmoney
                                   pos_count += 1
                               else:
                                   rmoney = obj[1]*100
                                   rebackmoney += rmoney
                                   back_count += 1
                            gathermoney=pos_money-rebackmoney
                            gather_count = pos_count - back_count#2012-07-11加的消费次数参数
                            resp+="Ret=OK\nposmoney=%s\nusername=%s\nposrecord=%s" % (gathermoney,getuserinfo(objcard.UserID_id,"EName"),gather_count)
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,urlcon,resp,0)
                            return resp
                        else:#无记录
                            resp+="Ret=OK\nposmoney=0\nusername=%s\nposrecord=0"% getuserinfo(objcard.UserID_id,"EName")
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,urlcon,resp,212)
                            return resp 
                    except Exception,e:
                            errorLog(request)
                            err = u"%s" % e
                            resp+="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,10,urlcon,err,-1)
                            return resp  
        elif querytype=='4':#设备汇总查询
                try:
                    start = request.REQUEST.get('start')
                    end = request.REQUEST.get('end')
                    starttime = datetime.datetime.strptime(start,"%Y%m%d%H%M%S")
                    endtime = datetime.datetime.strptime(end,"%Y%m%d%H%M%S")
                    from mysite.pos.pos_id.id_posdevview_sql import get_id_device_query
                    from mysite.sql_utils import get_sql_exe_result
                    import time
                    a = time.time()
                    sql = get_id_device_query(sn,starttime,endtime)
                    allpos = get_sql_exe_result(sql)
                    b = time.time()
                    print "query_time==================",b-a
#                    allpos = CarCashSZ.objects.filter(checktime__lte=endtime,checktime__gte=starttime,sn_name=sn,type__in=[6,8,9,10,12]).values_list('type_id','money')
                    pos_money = 0
                    rebackmoney = 0
                    pos_count = 0
                    back_count = 0
                    gather_count = 0
                    
                    if allpos:
                        for obj in allpos:
                            if obj[0]==6 or obj[0]==8 or obj[0]==10:
                                posmoney = obj[1]*100
                                pos_money += posmoney
                                pos_count += 1
                            else:
                                rmoney = obj[1]*100
                                rebackmoney += rmoney
                                back_count += 1
                        gathermoney=pos_money-rebackmoney #2012-07-11加的消费次数参数
                        gather_count = pos_count - back_count
                        resp+="Ret=OK\nposmoney=%s\nposrecord=%s" %(gathermoney,gather_count)
                        save_posdev_cmd(sn,sequ,None,card,11,urlcon,resp,0)
                        c = time.time()
                        print "reponse_time==================",c-a
                        return resp
                    else:#无记录
                        resp+="Ret=OK\nrecordcount=0\nposrecord=0"
                        save_posdev_cmd(sn,sequ,None,card,11,urlcon,resp,212)
                        return resp 
                except Exception,e:
                        errorLog(request)
                        err = u"%s" % e
                        resp+="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
                        save_posdev_cmd(sn,sequ,None,card,11,urlcon,err,-1)
                        return resp  
    except Exception,e:
        errorLog(request)
        err = u"%s" % e
        resp+="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        save_posdev_cmd(sn,sequ,None,card,19,urlcon,err,-1)
        return resp
    
    
#消费机通讯业务请求处理
def pos_getreq(request):
    
    resp = ""
     #/****语言控制台数pwp start***/
    from mysite import authorize_fun
    language=request.REQUEST.get('language',None)
    #deviceType = request.REQUEST.get('device_type')#设备类型参数
    sequ= request.REQUEST.get('sequ')
    card= request.REQUEST.get('card')
    sn = request.REQUEST.get('SN')
    postype = request.REQUEST.get('postype')
    querytype = request.REQUEST.get('querytype')
    urlcon=request.build_absolute_uri()
    device = get_cache_device(request,sn)
    try:
        #objemp = Employee.objects.filter(Card=card)
        if card:
            card = int(card)
            objcard = get_cache_issuecard("IssueCard_"+str(card))#从缓存中获取卡信息
        else:
            objcard = None
        if card and device:
            managecard = get_cache_cardmanage(card,device)#从缓存中获取管理卡卡信息
        else:
            managecard = None
        
        iccardobj=None
        if not device: 
            #设备不存在  设备未注册
            resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=208\nerrmsg=%s" % (sequ,_(u"设备不存在"))
            save_posdev_cmd(sn,sequ,None,card,postype,urlcon,resp,208)
            return resp.encode("GB18030")
        elif managecard: 
            resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=4\nerrmsg=%s" % (sequ,_(u"管理卡"))
            save_posdev_cmd(sn,sequ,None,card,postype,urlcon,resp,4)
            return  resp.encode("GB18030")
        
        elif querytype is not None:#挂失，解挂，修改密码,查询
            resp=querytype_action(request,device,objcard,sn,sequ,card,managecard)
            return resp.encode("GB18030")
        elif  not objcard: 
            resp+="Ret=No\nsequ=%s\nbalance=0\nretnumber=2\nerrmsg=%s" % (sequ,_(u"无效卡"))
            save_posdev_cmd(sn,sequ,None,card,postype,urlcon,resp,2)
            return  resp.encode("GB18030")
        elif(objcard.cardstatus=='3'):#黑名单
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"黑名单"))
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,1)
            return resp.encode("GB18030")
        elif objcard.cardstatus=='5':#停用卡
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=1\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"停用卡"))
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,5)
            return resp.encode("GB18030")
        #过期卡
        elif(objcard.cardstatus=='4'):
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=101\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"卡片已过有效期")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,101)
            return resp.encode("GB18030")
        elif(objcard.card_privage=='1'):
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=2\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"无效卡"))
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,2)
            return resp.encode("GB18030")
        else:
            key = "pos_tag_"+str(card)
            poscard=cache.get(key)
            if poscard!=card:
                iccardobj = get_cache_iccard("ICcard_"+str(objcard.type_id))     
                objcard.card_from_dev=True 
                resp=posmodveryfy(request,device,objcard,iccardobj,sn,card,postype,sequ,urlcon)  
                objcard.card_from_dev=False
                return resp.encode("GB18030")
            else:
                resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"重复刷卡消费失败")
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,-2)
                return resp.encode("GB18030")
    except  Exception, e:
        errorLog(request)
        err = u"sysError-------%s" % e
        pos_write_log(err,sn,card)
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,err,-1)#保存设备通讯日志
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        return resp
        
   

def validate_cardtype(request,device,objcard,pos_money,postype,iccardobj,sn,card,sequ,urlcon,mealobj) :#验证有卡类的卡
    resp=""
    response = device_response()
    use_device = get_device_code(iccardobj)#卡类可用设备
    posmeal = get_meal_code(iccardobj)#卡类餐别
    postime = iccardobj.pos_time#消费时间段
    lessmoney = iccardobj.less_money#卡类最小余额
    maxmoney = iccardobj.max_money#卡类最大余额
    datemaxmoney=iccardobj.date_max_money#日消费最大金额
    permaxmoney=iccardobj.per_max_money#次消费最大金额
    newblance = objcard.blance-pos_money
    if newblance<0:
        resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=3\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"余额不足")) 
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,3)#保存设备通讯日志
        return resp
    if newblance<lessmoney and lessmoney>0:#314 超出卡最小余额
        resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=314\nerrmsg=%s" % (sequ,objcard.blance*100,(u"低于卡最小余额")) 
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,314)#保存设备通讯日志
        return resp
    if newblance >maxmoney and maxmoney>0:#超出卡最大余额
        resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=315\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"超出卡最大余额"))   
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,315)#保存设备通讯日志
        return resp
    if iccardobj is None:#卡类不存在
        resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=104\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"卡类不存在")) 
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,104)
        return resp
#    if(daycount>usedate and usedate>0):#卡是否过期
#        resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=101\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"卡片已过有效期")) 
#        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,101)
#        return resp
    if use_device:#103、无消费权限（卡片不可在此机器上使用）
         listSN=[]
         for obj in use_device:#获取该卡所属设备列表
            listSN.append(obj.sn)
         flag = sn in listSN
         if(not flag):
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=103\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"无消费权限")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,103)
            return resp
    if postime:#消费时间段验证
         codelist=[]
         battime = get_now_batchtime(postime)
         if not battime:#系统没有当前消费时间段
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=102\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"不在消费时间段")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,102)
            return resp
    if posmeal:
         meallist=[]
         if not mealobj:#系统无当前消费时间餐别
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=107\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"无此餐别")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,107)
            return resp
         else:
            for obj in posmeal:
               meallist.append(obj.code)
            melcode = mealobj.code
            flags = melcode in meallist
            if(not flags):#没有该餐别的权限
               resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=106\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"无此餐别权限")) 
               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,106)
               return resp
    if(pos_money>permaxmoney and permaxmoney>0):
       #超出次消费最大金额
       resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=109\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"单次消费超额")) 
       save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,109)#保存设备通讯日志
       return resp  
    return resp
#回滚卡类参数
def reback_set_card_param(request,postype,objcard,posmoney,iccardobj,type,sn,card):
    try:
        date_money =objcard.date_money
        date_count =objcard.date_count
        meal_money =objcard.meal_money
        meal_count =objcard.meal_count
        datemaxmoney=iccardobj.date_max_money#日消费最大金额
        mealmaxmoney=iccardobj.meal_max_money#餐消费最大金额
        mealmaxcount=iccardobj.meal_max_count#餐消费最大次数
        datemaxcount =iccardobj.date_max_count#日消费最大次数
        resp=""
        if postype==6:
            if type=='1':#计时结束
                dmoney = date_money - posmoney
                mmoney = meal_money - posmoney
                dcount=date_count
                mcount=meal_count
            else:
                dmoney=date_money
                mmoney=meal_money
                dcount = date_count - 1
                mcount = meal_count - 1
        else:
            dmoney = date_money - posmoney
            mmoney = meal_money - posmoney
            dcount = date_count - 1
            mcount = meal_count - 1
        if datemaxmoney>0:
            objcard.date_money=dmoney
        if datemaxcount>0:
            objcard.date_count=dcount
        if mealmaxmoney>0:
            objcard.meal_money=mmoney
        if mealmaxcount>0:
            objcard.meal_count=mcount
        objcard.save(force_update=True,log_msg=False)
        return resp
    except  Exception, e:
           errorLog(request)
           resp = u"sysError-------%s" % e
           pos_write_log(resp,sn,card)
           save_posdev_cmd(sn,None,getuserinfo(objcard.UserID_id,"PIN"),card,postype,request.build_absolute_uri(),resp,-1)#保存设备通讯日志
           resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
           return resp
        

#设置卡类验证参数
def set_card_param(request,postype,objcard,posmoney,iccardobj,sn,card,sequ,urlcon,mealobj,objtime):
    try:
        date_money =objcard.date_money
        date_count =objcard.date_count
        meal_money =objcard.meal_money
        meal_count =objcard.meal_count
        if postype=='6':
            if objtime:
                type = objtime.split(':')[0]
                if type=='1':#计时结束
                    dmoney = date_money + posmoney
                    mmoney = meal_money + posmoney
                    dcount=date_count
                    mcount=meal_count
                else:
                    dmoney=date_money
                    mmoney=meal_money
                    dcount = date_count + 1
                    mcount = meal_count + 1
            else:
                dmoney=date_money
                mmoney=meal_money
                dcount = date_count + 1
                mcount = meal_count + 1
        else:
            dmoney = date_money + posmoney
            mmoney = meal_money + posmoney
            dcount = date_count + 1
            mcount = meal_count + 1
        datemaxmoney=iccardobj.date_max_money#日消费最大金额
        mealmaxmoney=iccardobj.meal_max_money#餐消费最大金额
        mealmaxcount=iccardobj.meal_max_count#餐消费最大次数
        datemaxcount =iccardobj.date_max_count#日消费最大次数
        mpostype =str(objcard.meal_type)
        date = objcard.pos_date
        nowdate = datetime.datetime.now().date()
        if mealobj:
            mtype = mealobj.code
        else:
            mtype=0
        resp=""
        if(mealmaxcount<mcount and mealmaxcount>0 and date == nowdate and mtype==mpostype):
           #超出餐消费最大次数
           resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=204\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"餐消费超次")) 
           save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,204)#保存设备通讯日志
           return resp
        elif(datemaxcount<dcount and datemaxcount>0 and date == nowdate ):
               #超出日消费最大次数
           resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=202\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"日消费超次")) 
           save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,202)#保存设备通讯日志
           return resp
        
        elif(mmoney>mealmaxmoney and mealmaxmoney>0 and date == nowdate and mtype==mpostype):
            #超出餐消费最大金额
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=203\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"餐消费超额")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,203)#保存设备通讯日志
            return resp
        elif(dmoney>datemaxmoney and datemaxmoney>0 and date == nowdate):
            #超出日消费金额
            resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=201\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"日消费超额")) 
            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,201)#保存设备通讯日志
            return resp
       
        else:
            if date == nowdate:#消费日期是否在同一天
                if mtype==mpostype:
                    objcard.pos_time=nowdate
                    objcard.pos_date=nowdate
                    if datemaxmoney>0:
                        objcard.date_money=dmoney
                    if datemaxcount>0:
                        objcard.date_count=dcount
                    if mealmaxmoney>0:
                        objcard.meal_money=mmoney
                    if mealmaxcount>0:
                        objcard.meal_count=mcount
                    objcard.meal_type=mtype
                    objcard.save(force_update=True,log_msg=False)
                    return resp
                else:#餐别不同
                    objcard.pos_time=nowdate
                    objcard.pos_date=nowdate
                    if datemaxmoney>0:
                        objcard.date_money=dmoney
                    if datemaxcount>0:
                        objcard.date_count=dcount
                    if mealmaxmoney>0:
                        objcard.meal_money=posmoney
                    if mealmaxcount>0:
                        objcard.meal_count=1
                    objcard.meal_type=mtype
                    objcard.save(force_update=True,log_msg=False)
                    return resp
            else:
                objcard.pos_time=nowdate
                objcard.pos_date=nowdate
                if datemaxmoney>0:
                    objcard.date_money=posmoney
                if datemaxcount>0:
                    objcard.date_count=1
                if mealmaxmoney>0:
                    objcard.meal_money=posmoney
                if mealmaxcount>0:
                    objcard.meal_count=1
                objcard.meal_type=mtype
                objcard.save(force_update=True,log_msg=False)
                return resp
    except  Exception, e:
           errorLog(request)
           resp = u"sysError-------%s" % e
           pos_write_log(resp,sn,card)
           save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,-1)#保存设备通讯日志
           resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
           return resp
           
#定值模式处理
@transaction.commit_on_success
def set_value_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj):
    a = time.time()
    try:
        resp=""
        posmoney=int(request.REQUEST.get('posmoney'))
        if iccardobj.discount:
            posmoney=Decimal(str(round(posmoney/100.00,2)))*Decimal(str(round(iccardobj.discount/100.00,2)))
        else:
            posmoney=Decimal(str(round(posmoney/100.00,2)))
        posmoney = Decimal(str(round(posmoney,2)))
        resp=validate_cardtype(request,device,objcard,posmoney,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        if resp=="":
            resp=set_card_param(request,postype,objcard,posmoney,iccardobj,sn,card,sequ,urlcon,mealobj,None)
            if resp=="":
                n_blance = objcard.blance-posmoney
                newblance=Decimal(str(round(n_blance,2)))
                objcard.blance=newblance
                objcard.save(force_update=True,log_msg=False) #扣款
                CarCashSZ(user_id=objcard.UserID_id,
                         dept_id = get_dept(objcard.UserID_id).id,
                         card = card,
                         serialnum=sequ,
                         checktime=datetime.datetime.now(),
                         type_id=6,#消费类型
                         money=posmoney,
                         sn_name = device.sn,
                         discount= iccardobj.discount,
                         hide_column=6,
                         dining = device.dining,
                         blance=newblance,
                         ).save(force_insert=True,log_msg=False)#新增消费记录
                #消费成功
                resp+="Ret=OK\nsequ=%s\nbalance=%s\nretnumber=0\nusername=%s" % (sequ,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName")) 
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,0)#保存设备通讯日志
                save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,posmoney,newblance)#保存消费记录
                b = time.time()
#                print "tttttttttttttttttttt===",b-a
                return resp
            return resp
        return resp
    except  Exception, e:
           errorLog(request)
           resp = u"sysError----%s" % e
           pos_write_log(resp,sn,card)
           save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,-1)#保存设备通讯日志
           resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
           return resp

#金额模式
@transaction.commit_on_success
def money_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj):
    try:
        resp=""
        posmoney=int(request.REQUEST.get('posmoney'))
#        if(objcard.type is not None):
        if iccardobj.discount:
            pos_money=Decimal(str(round(posmoney/100.00,2)))*Decimal(str(round(iccardobj.discount/100.00,2)))
        else:
            pos_money=Decimal(str(round(posmoney/100.00,2)))
        pos_money=Decimal(str(round(pos_money,2)))
        resp+=validate_cardtype(request,device,objcard,pos_money,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        if resp =="":
            resp=set_card_param(request,postype,objcard,pos_money,iccardobj,sn,card,sequ,urlcon,mealobj,None)
            if resp =="":
                n_blance = objcard.blance-pos_money
                newblance = Decimal(str(round(n_blance,2))) #获取消费后余额
                objcard.blance=newblance
                objcard.save(force_update=True,log_msg=False) #扣款
                CarCashSZ(user_id=objcard.UserID_id,
                      dept_id = get_dept(objcard.UserID_id).id,
                      card = card,
                      serialnum=sequ,
                      checktime=datetime.datetime.now(),
                      type_id=6,#消费类型
                      money=pos_money,
                      sn_name = device.sn,
                      discount = iccardobj.discount,
                      hide_column=6,
                      dining = device.dining,
                      blance = newblance
                      ).save(force_insert=True,log_msg=False)#新增消费记录
                #消费成功
                resp+="Ret=OK\nsequ=%s\nbalance=%s\nretnumber=0\nusername=%s" % (sequ,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName")) 
                save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,pos_money,newblance)
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,0)#保存设备通讯日志
                return resp
            return resp
        return resp
    except Exception, e:
        errorLog(request)
        resp = u"sysError-----%s" % e
        pos_write_log(resp,sn,card)
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,123)#保存设备通讯日志
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        return resp

#计次模式
@transaction.commit_on_success
def set_plan_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj):
    try:
        resp=""
        timenow = datetime.datetime.now().time()
        if mealobj:
            pos_money=mealobj.money
        else:
            pos_money=0
        resp+=validate_cardtype(request,device,objcard,0,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        if resp=="":
            resp=set_card_param(request,postype,objcard,0,iccardobj,sn,card,sequ,urlcon,mealobj,None)
            if resp =="":
                CarCashSZ(user_id=objcard.UserID_id,
                        dept_id = get_dept(objcard.UserID_id).id,
                        card = card,
                        serialnum=sequ,
                        checktime=datetime.datetime.now(),
                        type_id=10,#消费类型
                        money=pos_money,
                        sn_name = device.sn,
                        discount = 0,
                        hide_column=10,
                        dining = device.dining,
                        blance = objcard.blance,
                        ).save(force_insert=True,log_msg=False)#新增消费记录
                #消费成功
                resp+="Ret=OK\nsequ=%s\nbalance=%s\nretnumber=0\nusername=%s" % (sequ,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName")) 
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,0)#保存设备通讯日志
                save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,pos_money,objcard.blance)
                return resp    
            else:
                return resp
        else:return resp
    except Exception,e:
        errorLog(request)
        resp = u"sysError-----%s" % e
        pos_write_log(resp,sn,card)
        save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,123)#保存设备通讯日志
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        return resp

#计时模式
@transaction.commit_on_success
def set_time_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj):
        try:
            resp=""
            long_time = int(device.long_time)
            time_price = device.time_price
            from mysite.pos.models.model_timebrush import TimeBrush
            try:
                 objtime = read_timebrush(card)
            except:
                objtime=None
            lessmoney = iccardobj.less_money#卡类最小余额
            maxmoney = iccardobj.max_money#卡类最大余额
            permaxmoney = iccardobj.per_max_money#次消费最大金额
            resp+=validate_cardtype(request,device,objcard,0,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
            if resp=="":
                    if not objtime:#计时开始
                        resp=set_card_param(request,postype,objcard,0,iccardobj,sn,card,sequ,urlcon,mealobj,objtime)
                        if resp =="":
                            get_timebrush_from_txt(card,"1")
                            objcard.save(force_update=True,log_msg=False)
                            resp+="Ret=OK\nsequ=%s\nposmoney=0\nbalance=%s\nretnumber=1\nusername=%s" %(sequ,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName"))
                            save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,123)#保存设备通讯日志
                            return resp
                        else:
                             return resp
                    else:
                        type = objtime.split(':')[0]
                        bgtime = datetime.datetime.strptime(objtime.split(':')[1],"%Y%m%d%H%M%S")
#                        if objtime.type==1:#计时结束
                        if type=='1':
                            posmoney=0
                            timediffer=0
                            nowtime = datetime.datetime.now()
                            if (nowtime-bgtime).days>0:
                               timediffer = (nowtime-bgtime).seconds#消费时间差
                               time = (nowtime-bgtime).days*24+Decimal(str(round(timediffer/3600.00,2)))#换算成小时
                            else :
                               timediffer = (nowtime-bgtime).seconds
                               time = Decimal(str(round(timediffer/3600.00,2)))#换算成小时
                            if time>=1:
                                time_hour = str(time).split('.')[0]#获取小时
                                minute = Decimal(str(round(timediffer/60.00,2)))   
                                ptime = Decimal(str(round(minute/long_time,1)))
                                s_time = str(ptime).split('.')[1]#获取小数位
                                if s_time != '0':
                                     pos_time = (int(str(ptime).split('.')[0])+1)*long_time
                                else:
                                     pos_time = int(str(ptime).split('.')[0])*long_time
                                if (nowtime-bgtime).days>0:
                                    posmoney = pos_time/60.00*float(time_price) + int(time_hour)*float(time_price)
                                else:
                                    posmoney = pos_time/60.00*float(time_price)
                            else:
                                 minute = time*60 #换算成分钟
                                 if minute<=long_time:
                                    #ltime = Decimal(str(round(long_time/60.00,3)))
                                    posmoney = long_time/60.00*float(time_price)
                                 else:#时长取整
                                    ptime = float(minute/long_time)
                                    s_time = str(ptime).split('.')[1]#获取小时
                                    if s_time != '0':
                                         pos_time = (int(str(ptime).split('.')[0])+1)*long_time
                                    else:
                                         pos_time = int(str(ptime).split('.')[0])*long_time
                                    #l_time = Decimal(str(round(pos_time/60.00,2)))
                                    posmoney = pos_time/60.00*float(time_price)
                            if iccardobj.discount:
                                pos_money = Decimal(str(posmoney))*Decimal(str(round(iccardobj.discount/100.00,2)))
                            else:
                                pos_money = Decimal(str(posmoney))
                            pos_money=Decimal(str(round(pos_money,2)))
                            newblance = objcard.blance-pos_money
                            newblance = Decimal(str(round(newblance,2)))
                            if newblance<0:
                               resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=3\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"余额不足")) 
                               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,3)#保存设备通讯日志
                               return resp
                            elif newblance<lessmoney and lessmoney>0:#超出最小余额
                               resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=314\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"低于卡最小余额")) 
                               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,314)#保存设备通讯日志
                               return resp
                            elif newblance >maxmoney and maxmoney>0:#超出卡最大余额
                               resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=315\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"超出卡最大余额"))   
                               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,315)#保存设备通讯日志
                               return resp
                            elif(pos_money>permaxmoney and permaxmoney>0):
                               #超出次消费最大金额
                               resp+="Ret=No\nsequ=%s\nbalance=%s\nretnumber=109\nerrmsg=%s" % (sequ,objcard.blance*100,_(u"单次消费超额")) 
                               save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,109)#保存设备通讯日志
                               return resp  
                            else:
                                resp=set_card_param(request,postype,objcard,pos_money,iccardobj,sn,card,sequ,urlcon,mealobj,objtime)
                                if resp=="":
                                    objcard.blance=newblance
                                    objcard.save(force_update=True,log_msg=False) #扣款
                                    CarCashSZ(user_id=objcard.UserID_id,
                                             dept_id = get_dept(objcard.UserID_id).id,
                                             card = card,
                                             serialnum=sequ,
                                             checktime=datetime.datetime.now(),
                                             type_id=6,#消费类型
                                             money=pos_money,
                                             sn_name = device.sn,
                                             discount = iccardobj.discount,
                                             hide_column=6,
                                             dining = device.dining,
                                             blance = newblance
                                             ).save(force_insert=True,log_msg=False)#新增消费记录  加参数优化
                                    get_timebrush_from_txt(card,"2")
                                    resp+="Ret=OK\nsequ=%s\nposmoney=%s\nbalance=%s\nretnumber=2\nusername=%s" %(sequ,pos_money*100,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName")) 
                                    save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,124)#保存设备通讯日志
                                    save_pos_cmd(device.alias,sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,pos_money,newblance)#保存消费记录
                                    return resp
                                else:
                                    return resp
                
                        else:
                            resp=set_card_param(request,postype,objcard,0,iccardobj,sn,card,sequ,urlcon,mealobj,objtime)
                            if resp=="":
                                get_timebrush_from_txt(card,"1")
                                objcard.save(force_update=True,log_msg=False)
                                resp+="Ret=OK\nsequ=%s\nposmoney=0\nbalance=%s\nretnumber=1\nusername=%s" %(sequ,objcard.blance*100,getuserinfo(objcard.UserID_id,"EName"))
                                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,resp,123)#保存设备通讯日志
                                return resp
                            else:
                                return resp
            else:
                return resp
        except  Exception, e:
                errorLog(request)
                err = u"sysError-----%s" % e
                pos_write_log(err,sn,card)
                save_posdev_cmd(sn,sequ,getuserinfo(objcard.UserID_id,"PIN"),card,postype,urlcon,err,123)#保存设备通讯日志
                resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
                return resp
    

  
def posmodveryfy(request,device,objcard,iccardobj,sn,card,postype,sequ,urlcon):
    try:
        try:
            key = "pos_tag_"+str(card)
            posflag=cache.set(key,card,5)
            mealobj=get_now_meal()
        except:
            mealobj=None
#        if postype is not None:    
        if(postype=='1'):#定值模式
            return set_value_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        elif(postype=='2'):#金额模式
            return money_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        elif(postype=='3'):#键值模式
            return money_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        elif(postype=='5'):#商品模式
            return money_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        elif(postype=='4'):#计次模式
            return set_plan_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
        elif(postype=='6'):#计时模式
            return set_time_model(request,device,objcard,postype,iccardobj,sn,card,sequ,urlcon,mealobj)
    except  Exception, e:
        errorLog(request)
        resp = u"sysError----%s" % e
        pos_write_log(resp,sn,card)
        resp="Ret=NO\nretnumber=-1\nerrmsg=%s"% _(u"消费失败")
        return resp
        
        

#保存消费日志
@transaction.commit_on_success
def save_pos_cmd(name,sn,sequ,pin,card,postype,money,carblance):
    from mysite.pos.models.model_poslog import PosLog
    try:
        PosLog(
                devname=name,
                sn=sn,
                serialnum=sequ,
                pin=pin,
                carno=card,
                posmodel=postype,#消费类型
                posmoney=money,
                blance=carblance,
                posOpTime = datetime.datetime.now(),
                ).save()#新增消费记录
    except:
            print_exc()
            
            
#保存消费机通讯命令日志 
@transaction.commit_on_success
def save_posdev_cmd(sn,sequ,pin,card,postype,content,returncontent,renumber):
    from mysite.pos.models.model_posdevlog import PosDevLog
    pos_write_log("returnValue---"+returncontent,sn,card);
    try:
        if POS_DEBUG:
            PosDevLog(
                    sn=sn,
                    serialnum=sequ,
                    pin=pin,#人员编号
                    carno=card,
                    posmodel=postype,#消费类型
                    content=content,#命令内容
                    returncon=returncontent,#返回内容
                    remark = renumber,
                    posOpTime = datetime.datetime.now(),
                    ).save()#新增通讯命令记录
    except:
            print_exc()

