# -*- coding: utf-8 -*-
from django.http import HttpResponse
from dbapp.utils import getJSResponse
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.shortcuts import render_to_response
from dbapp.datautils import NoFound404Response
from django.utils.translation import ugettext_lazy as _
from dbapp.modelutils import GetModel
from django.db.models import Max
import os
import time
import sys
import subprocess
import logging
import datetime
from mysite.worktable.models import InstantMsg
from mysite.utils import get_option
from base.backup import get_attsite_file

FILTER_POS_BREAK_LOG = False
att_file = get_attsite_file()
develop = att_file["Options"]["FILTER_POS_BREAK_LOG"]
if develop.lower()=="true":
    FILTER_POS_BREAK_LOG = True

    
def get_search_from(request,app_label,model_name):
    from dbapp.data_edit import form_for_model
    data_model=GetModel(app_label, model_name)
    if not data_model: return NoFound404Response(request)
    searchform=""
    if hasattr(data_model.Admin,"list_filter"):        
        searchform=form_for_model(data_model,fields=list(data_model.Admin.list_filter))                        
    if searchform:
        has_header=True          
    else:
        has_header=False
    t=loader.get_template("worktable_search_form.html")
    obj_dict={
        'app_label':app_label,
        'model_name':model_name,
        'has_header':has_header,
        'searchform':searchform,
        'query':"&".join([k+"="+v[0] for k,v in dict(request.GET).items()])
    }
    if model_name=="Device":
        device_disable_cols_dic =['acpanel_type','device_use_type','dining.name','consume_model','com_port','com_address','show_enabled|boolean_icon','show_fp_mthreshold','get_dstime_name','device_type','fw_version']
        obj_dict["disable_cols"]=("__").join(device_disable_cols_dic)
    rc=RequestContext(request,obj_dict)
    return HttpResponse(t.render(rc))


def getMaxDay(year,month):
    if month==4 or month==6 or month==9 or month==11:
        return 30  
    if month==2:  
        if (year%4==0 and year%100!=0) or (year%400==0):  
            return 29  
        else:  
            return 28 
    return 31  


#d->datetime,
#n->the count of month
def datetime_offset_month(dd,n):
    y=dd.year
    m=dd.month
    d=dd.day
    madd=m+n 
    #年
    if madd>12:
        if madd%12!=0:
            y+=madd/12
        else:
            y+=madd/12-1
    elif madd<0:
        y+=-((-madd)/12+1)
    elif madd==0:
        y-=1
    #月
    if madd%12!=0:
        m=madd%12
    else:
        m=12
    
    #日
    max_d=getMaxDay(y,m)
    if d>max_d:
        d=max_d
    if hasattr(dd,"hour"):
        return datetime.datetime(year=y,month=m,day=d,hour=dd.hour,
                                minute=dd.minute,second=dd.second,
                                microsecond=dd.microsecond)
    else:
         return datetime.datetime(year=y,month=m,day=d)

def pos_cartype_change():
    from mysite.worktable.models import MsgType
    from mysite.personnel.models.model_iccard import ICcard
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_OVERDUE,CARD_VALID,POS_CARD
    from django.db import models, connection
    from django.core.cache import cache
    from base.cached_model import cache_key
    if get_option("POS_ID"):
        objcard = IssueCard.objects.filter(cardstatus = CARD_VALID,card_privage = POS_CARD)
    else:
        objcard = IssueCard.objects.filter(cardstatus__in = CARD_VALID,card_privage = POS_CARD,sys_card_no__isnull=False)
    if objcard:
        for obj in objcard:
            if(obj.type is not None):
                nowtime = datetime.datetime.now().date()
                objiccard = ICcard.objects.filter(pk=obj.type_id)
                if objiccard:
                    if type(obj.issuedate) == type(datetime.datetime.now()):
                        iscardate = obj.issuedate.date()
                    else:
                        iscardate = obj.issuedate
                    daycount = (nowtime-iscardate).days
                    maxday = objiccard[0].use_date
                    if(daycount>maxday and maxday>0):#卡是否过期
                        obj.cardstatus= CARD_OVERDUE #修改卡状态为过期
                        if get_option("POS_ID"):
                            obj.save(force_update=True,log_msg=False)
                        else:
                            models.Model.save(obj,force_update=True)
                            key = cache_key(obj,obj.pk)
                            cache.delete(key)
                        
                        msg=InstantMsg()
                        msg.content=""
                        if obj.UserID.PIN:
                           msg.content+=u"%s"%_(u"员工工号")+obj.UserID.PIN+";"
                        if obj.UserID.EName:
                           msg.content+=u"%s"%_(u"员工姓名")+obj.UserID.EName+";"
                        if len(msg.content)!=0:
                           msg.content+=u"%s"%_(u"消费卡过期!")
                           msg.monitor_last_time=datetime.datetime.now()
                           msg.msgtype=MsgType.objects.get(pk=5)#写在BaseCode表中消息类型,10代表消费信息
                           msg.save()
                        


#缓存卡信息
def set_cache_issucard():
    from mysite.pos.pos_constant import TIMEOUT
    from django.core.cache import cache
    from mysite.personnel.models.model_issuecard import IssueCard,POS_CARD
    
    allcard = IssueCard.objects.filter(card_privage = POS_CARD)
    cache.set("ALLIssueCard","tag_ALLIssueCard",TIMEOUT)
    for obj in allcard:
        iskey="IssueCard_%s" %obj.cardno
        cache.set(iskey,obj,TIMEOUT)


#员工转正消息
def emp_type_change(dt,max_dt=None):
    from mysite.worktable.models import MsgType
    from mysite.personnel.models import Employee
    d={}
    try:
        m=MsgType.objects.get(id=4)#消息类别
    except:
        return None
    
    begin_date=datetime_offset_month(dt,-3)#开始时间
    end_date=begin_date+datetime.timedelta(days=m.msg_ahead_remind,hours=23,minutes=59,seconds=59)
    d["Hiredday__gte"]=begin_date
    d["Hiredday__lte"]=end_date
    qs=Employee.objects.filter(**d)
    for emp in qs:
        msg=InstantMsg()
        msg.content=""
        if emp.PIN:
            msg.content+=u"%s"%_(u"员工工号")+emp.PIN+";"
        if emp.EName:
            msg.content+=u"%s"%_(u"员工姓名")+emp.EName+";"
        if len(msg.content)!=0:
            if (begin_date.year==emp.Hiredday.year) and (begin_date.month==emp.Hiredday.month) and (begin_date.day==emp.Hiredday.day):
                msg.content+=datetime.datetime.now().strftime("%Y-%m-%d")+u" %s"%_(u"转正！")
            else:
                msg.content+=datetime_offset_month(emp.Hiredday,3).strftime("%Y-%m-%d")+u" %s"%_(u"转正！")
            msg.monitor_last_time=datetime.datetime.now()
            msg.msgtype=MsgType.objects.get(pk=4)#写在BaseCode表中消息类型,6代表人事信息
            msg.save()
                
#过生日的消息
def birthday_msg(dt,max_dt=None):
    from mysite.personnel.models import Employee
    from mysite.worktable.models import MsgType
    from django.db.models import Q
    d={}
    #如果今天已经扫描过，那就扫描最后一次扫描到现在这个时段进来的人的生日
    #if max_dt['monitor_last_time__max']:
       # d["create_time__gt"]=max_dt['monitor_last_time__max']
    try:
        m=MsgType.objects.get(id=4)#消息类别
    except:
        return None
    
    begin_date=dt#开始时间
    end_date=dt+datetime.timedelta(days=m.msg_ahead_remind)#结束时间
    
    days=m.msg_ahead_remind
    in_dates=[]
    for i in range(0,days+1):
        tmp_date=begin_date+datetime.timedelta(days=i)
        if tmp_date<=end_date:
            in_dates.append([tmp_date.month,tmp_date.day])
            
    query="|".join(["(Q(Birthday__month=%s)&Q(Birthday__day=%s))"%(m,dd) for m,dd in in_dates])
    qs=[]
    if query:
        qs=Employee.objects.filter(**d).filter(eval(query))
        
    for emp in qs:
        msg=InstantMsg();
        msg.content=""
        if emp.PIN:
            msg.content+=u"%s"%_(u"员工工号")+emp.PIN+";"
        if emp.EName:
            msg.content+=u"%s"%_(u"员工姓名")+getattr(emp,"EName")+";"
        if len(msg.content)!=0:
            if emp.Birthday.month==dt.month and emp.Birthday.day==dt.day:
                msg.content+=datetime.datetime.now().strftime("%Y-%m-%d")+u" %s"%_(u"过生日！")
            else:
                msg.content+=str(dt.year)+"-"+str(emp.Birthday.month)+"-"+str(emp.Birthday.day)+u" %s"%_(u"过生日！")
            msg.monitor_last_time=datetime.datetime.now()
            msg.msgtype=MsgType.objects.get(pk=4)#人事公告id=4
            msg.save()


#每天的stime开始扫描数据库
def monitor_instant_msg():
    from base.models import appOptions
    from django.conf import settings
    from django.utils import translation
    translation.activate(settings.LANGUAGE_CODE)
   
#    max_dt=InstantMsg.objects.filter(
#               monitor_last_time__year=dt.year,
#               monitor_last_time__month=dt.month,
#               monitor_last_time__day=dt.day
#               ).aggregate(Max("monitor_last_time"))#查找今天最近扫描的一次，以防扫描重复的数据
#   
    if get_option("POS"):
        stime = appOptions["pos_scanner"]
    else:
        stime=appOptions["msg_scanner"]
    if stime:
        h,m=stime.split(":")
        dt_now=datetime.datetime.now()
        dt=datetime.datetime(year=dt_now.year,month=dt_now.month,day=dt_now.day)#设置时分秒为00:00:00
        try:
            while True:#固定在每天的7:01开始监控,测试阶段
                #print 'dt_now.hour:',dt_now.hour,'dt_now.minute:',dt_now.minute,'dt_now.second',dt_now.second,'hhhh:',h,'mmmmmm:',m
                if dt_now.hour==int(h) and dt_now.minute==int(m):
                    birthday_msg(dt)
                    emp_type_change(dt)
                    from django.conf import settings
                    if get_option("POS"):
                        pos_cartype_change() #消费卡过期
                        set_cache_issucard()#缓存卡表信息
                    if get_option("POS_IC") and FILTER_POS_BREAK_LOG:
                        from mysite.pos.pos_utils import filter_break_log
                        filter_break_log("pos_log_stamp")#筛选IC消费设备的灰色记录
                    
                time.sleep(56)
                if get_option("POS"):
                    stime = appOptions["pos_scanner"]
                else:
                    stime=appOptions["msg_scanner"]
                
                h,m=stime.split(":")
                dt_now=datetime.datetime.now()
                dt=datetime.datetime(year=dt_now.year,month=dt_now.month,day=dt_now.day)#设置时分秒为00:00:00
        except:
            import traceback; traceback.print_exc()
        
        
        
