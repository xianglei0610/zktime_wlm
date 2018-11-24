# -*- coding: utf-8 -*- 
#用以删除垃圾文件
import os
from traceback import print_exc
import dict4ini
import shutil
import datetime
import types
from django.db import connection
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.settings import MEDIA_ROOT
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.conf import settings
import time

ADMS_DIR = settings.APP_HOME
    
def delete_upload_dirs(before_days=7):
    '''清除每天设备上传数据生成的文件夹'''
    
    clear_days = before_days
    today=datetime.datetime.now()
    count = 0
    if type(clear_days)!=types.IntType:
        return u"%s"%_(u"时间格式不正确.")
    
    deleteday=today-datetime.timedelta(days=clear_days)
    
    dayfile=deleteday.strftime("%Y%m%d")
    upload=ADMS_DIR+"\\tmp\\upload"
    if os.path.exists(upload):
        dev_sn=os.listdir(upload)
        for dev in dev_sn:
            dev_path = os.path.join(upload,dev)
            datesfiles=os.listdir(dev_path)
            for d_file in datesfiles:
                try:
                    processed_dir=os.path.join(dev_path,d_file)
                    if os.path.isdir(processed_dir) and d_file!="new":
                        if int(d_file) < int(dayfile):
                            shutil.rmtree(processed_dir)
                            count +=1
                except:
                    pass
        
    return count
    
#删除临时文件
def delete_temp_dirs(before_days=7):
    '''
    清除 tmp目录下生产的临时文件夹
    '''
    
    if type(before_days)!= types.IntType:
        return u"%s"%_(u"时间格式不对")
    
    temp=os.path.join(ADMS_DIR,"tmp")
    if os.path.exists(temp):
        temp_files=os.listdir(temp)
        before_date = datetime.datetime.now()-datetime.timedelta(before_days)
        count = 0
        for temp_file in temp_files:
            if temp_file !="upload" and temp_file!="zkpos":
                try:
                    dir_file=os.path.join(temp,temp_file)
                    if os.path.isdir(dir_file):
                        str_day = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(dir_file)))
                        modify_date = datetime.datetime.strptime(str_day,'%Y-%m-%d %H:%M:%S')
                        if modify_date<before_date:
                            shutil.rmtree(dir_file)
                            print dir_file
                            count += 1
                except:
                    pass
    return count

def delete_report_list(before_days=7):
    '''
    删除 tmp目录下生产的报表文件 门禁错误日志不在考虑内
    '''
    clear_days = before_days
    if type(before_days)!= types.IntType:
        return u"%s"%_(u"时间格式不对")
    
    today=datetime.datetime.now()
    count = 0
    before_date=today -datetime.timedelta(days=clear_days) 
           
    dayfile=before_date.strftime("%Y%m%d")
    tmp=os.getcwd()+"\\tmp"
    tt=os.listdir(tmp)
    
    for t in tt:
        if t.find('_')>0:
            pp=t.split("_")[1]
            p=pp.split(".")[0]
            if len(p)==14:
                file_data=p[0:8]
                if int(file_data) < int(dayfile):
                    count +=1
                    os.remove(os.path.join(tmp,t))
    return count
    
    
def delete_fqueue_file(before_days =7):
    '''清除 _fqueue文件下产生的垃圾文件'''
    fqueue=ADMS_DIR+"/_fqueue"
    count =0
    dt_now = datetime.datetime.now()
    if type(before_days)!= types.IntType:
        return u"%s"%_(u"时间格式不对")
    
    before_date = dt_now-datetime.timedelta(days =before_days)
    try:
        if os.path.exists(fqueue):
            xx=os.listdir(fqueue)
            for x in xx:
                if x.find('.')<0:
                    f = os.path.join(fqueue,x)
                    str_day = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(f)))
                    modify_date = datetime.datetime.strptime(str_day,'%Y-%m-%d %H:%M:%S')
                    if modify_date<before_date:
                        os.remove(os.path.join(fqueue,x))
                        count +=1
    except:
        pass
    
    return count

def execute_sql(sql):
    u"执行SQL语句"
    cursor = connection.cursor()
    cursor.execute(sql)
    connection._commit()
    
def delete_devcmd_bak(before_days = 7):
    u"删除失败命令表"
    from mysite.iclock.models.model_devcmdbak import DevCmdBak
    dt_now =  datetime.datetime.now()
    count =0
    sql = u"DELETE FROM devcmds_bak WHERE cmdcommittime<='%s'"
    if before_days and type(before_days) == types.IntType:
        before_date = dt_now-datetime.timedelta(days=before_days)
        qs = DevCmdBak.objects.filter(CmdCommitTime__lte=before_date)
        count = qs.count()
        sql = sql%before_date.strftime("%Y-%m-%d %H:%M:%S")
        execute_sql(sql)
        #qs.delete()
    return count
        
def delete_action_log(before_days = 7):
    u"删除日志表的垃圾数据"
    from base.models_logentry import LogEntry
    sql  = u"DELETE FROM action_log WHERE action_time<='%s'"
    dt_now =  datetime.datetime.now()
    count =0
    if before_days and type(before_days) == types.IntType:
        before_date = dt_now-datetime.timedelta(days=before_days)
        qs = LogEntry.objects.filter(action_time__lte = before_date)
        count= qs.count()
        sql = sql%before_date.strftime("%Y-%m-%d %H:%M:%S")
        execute_sql(sql)
        #qs.delete()
    return count
        
        
def delete_operate_cmds(before_days = 7):
    u"删除operatecmds表中的垃圾数据"
    from mysite.iclock.models.model_devoperate import OperateCmd
    dt_now =  datetime.datetime.now()
    count = 0
    if before_days and type(before_days) == types.IntType:
        before_date = dt_now-datetime.timedelta(days=before_days)
        PROCESSED_FLAG = (1,2)
        qs = OperateCmd.objects.filter(success_flag__in=PROCESSED_FLAG,commit_time__lte=before_date)
        count = qs.count()
        qs.delete()
    
    return count
    
def delete_session_data(before_days = 7):
    u"删除过期的用户会话记录"
    from django.contrib.sessions.models import Session
    dt_now = datetime.datetime.now()
    count =0
    sql = u"DELETE FROM django_session WHERE expire_date <='%s'"
    if before_days and type(before_days) == types.IntType:
        before_date = dt_now-datetime.timedelta(days=before_days)
        qs = Session.objects.filter(expire_date__lte=before_date)
        count =qs.count()
        sql = sql%before_date.strftime("%Y-%m-%d %H:%M:%S")
        execute_sql(sql)
        #qs.delete()
    return count
    
@login_required
def get_html_data(request):
    u"默认删除七天以前的记录，不能删除七天以内的数据"
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    from dbapp.utils import getJSResponse
    
    request.dbapp_url =dbapp_url
    apps=get_all_app_and_models()
    dt_now = datetime.datetime.now()
    default_date =dt_now -datetime.timedelta(days =7)
    
    if request.method == "GET":
        return render_to_response('worktable_DeleteData.html',
           RequestContext(request,{
                   'dbapp_url': dbapp_url,
                   'MEDIA_URL':MEDIA_ROOT,
                   "current_app":'base', 
                   'apps':apps,
                   'before_date':default_date.strftime("%Y-%m-%d"),
                   "help_model_name":"DeleteData",
                   "myapp": [a for a in apps if a[0]=="base"][0][1],
                   'app_label':'worktable',
                   'model_name':'Device',
                   'menu_focus':'DeleteData',
                   'position':_(u'系统设置->临时数据清理'),
                   })
           
           )
    else:
        post_date = request.POST.get("before_date",None)
        before_date = default_date
        info =[]
        if post_date:
            try:
                before_date = datetime.datetime.strptime(post_date,"%Y-%m-%d")
            except:
                info.append(u"%s"%_(u"时间转化错误，清除失败,请确认日期输入正确！"))
                
        if (dt_now-before_date).days<7:
            info.append(u"%s"%_(u"不能删除7天之内的数据"))
        
        if not info:#没有错误
            #print 'post:%s\n'%request.POST
            dict_map_data=[
                ["clear_log",delete_action_log],
                ["clear_upload_dir",delete_upload_dirs],
                ["fqueue_file",delete_fqueue_file],
                ["clear_devcmd_bak",delete_devcmd_bak],
                ["clear_operate_cmds",delete_operate_cmds],
                ["clear_tmp_dir",delete_temp_dirs],
                ["clear_session",delete_session_data],
            ]
            dict_map_verbose={
                "clear_log":u"%s"%_(u"清理日志记录"),
                "clear_upload_dir":u"%s"%_(u"清理机器上传的过期文件夹"),
                "fqueue_file":u"%s"%_(u"清理文件缓存"),
                "clear_devcmd_bak":u"%s"%_(u"清理失败命令"),
                "clear_operate_cmds":u"%s"%_(u"清理通讯命令日志"),
                "clear_tmp_dir":u"%s"%_(u"清理临时文件夹"),
                "clear_session":u"%s"%_(u"清理用户会话记录"),
            }
            for k,process_key in dict_map_data:
                value = request.POST.get(k,None)
                if value:
                    #print 'delete %s\n'%k
                    days =(dt_now- before_date).days
                    ret = dict_map_verbose[k]+":"
                    try:
                        if days>0: 
                            ret += u"%s"%process_key(days)
                    except Exception,e:
                        #import traceback;traceback.print_exc()
                        ret+=u"%s"%e
                    
                    info.append(ret)
                    
        return getJSResponse(json.dumps(info))#返回处理结果

def test():
    u"测试删除七天以前的纪录"
    clear_days = 7
    delete_temp_dirs(clear_days)
    delete_report_list(clear_days)
    delete_fqueue_file(clear_days)
    delete_devcmd_bak(clear_days)
    delete_action_log(clear_days)
    delete_operate_cmds(clear_days)
