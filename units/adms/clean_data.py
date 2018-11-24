#!/usr/bin/python
# -*- coding: utf-8 -*- 
#用以删除垃圾文件


import os

from traceback import print_exc

import dict4ini
import datetime
import shutil

CLEAN_DAYS=7

def get_attsite_file():
    current_path = os.getcwd()
    attsite=dict4ini.DictIni(current_path+"/attsite.ini")
    return attsite

def delete_old_list(savdays=0):
    '''
    清除 设备传过来的 文本文件
    '''
    dict = get_attsite_file()
    try:
        CLEAN_DAYS = str(dict["SYS"]["DELETE_DAYS"])
    except:
        pass
    today=datetime.datetime.now()
    if savdays!=0:
        CLEAN_DAYS=savdays
    
    deleteday=today+datetime.timedelta(days=-int(CLEAN_DAYS))
    dayfile=deleteday.strftime("%Y%m%d")
    print "%s %s"%(dayfile,u"前删除".encode('gbk'))#处理乱码
    upload=os.getcwd()+"\\tmp\\upload"
    dev_sn=os.listdir(upload)
    for dev in dev_sn:
        datesfiles=os.listdir(upload+"\\"+dev)
        for d_file in datesfiles:
            try:
                if int(d_file) < int(dayfile):
                    del_list=upload+"\\"+dev+"\\"+d_file
                    print u"delete"+del_list
                    shutil.rmtree(del_list)
            except:
                pass
    print u"delete ok"
    
#删除临时文件
def delete_temp_list():
    '''
    清除 tmp目录下生产的临时文件
    '''
    print "%s"%u"开始删除临时垃圾文件".encode('gbk')#处理乱码
    temp=os.getcwd()+"\\tmp"
    temp_files=os.listdir(temp)
    for temp_file in temp_files:
        if temp_file!="upload":
            try:
                del_list=temp+"\\"+temp_file
                shutil.rmtree(del_list)
            except:
                pass
    print u"delete delete_temp_list ok"


def delete_report_list(savdays=0):
    '''
    删除 tmp目录下生产的报表文件 门禁错误日志不在考虑内
    '''
    dict = get_attsite_file()
    try:
        CLEAN_DAYS = str(dict["SYS"]["DELETE_DAYS"])
    except:
        pass
    today=datetime.datetime.now()
    try:
        CLEAN_DAYS=savdays
        deleteday=today+datetime.timedelta(days=-int(CLEAN_DAYS))
    except:
        CLEAN_DAYS=0
        deleteday=today
        
    dayfile=deleteday.strftime("%Y%m%d")
    print "%s %s"%(dayfile,u"前删除".encode('gbk'))#处理乱码
    tmp=os.getcwd()+"\\tmp"
    tt=os.listdir(tmp)
    for t in tt:
        if t.find('_')>0:
            pp=t.split("_")[1]
            p=pp.split(".")[0]
            if len(p)==14:
                file_data=p[0:8]
                if int(file_data) < int(dayfile):
                    print "delete "+ os.path.join(tmp,t)
                    os.remove(os.path.join(tmp,t))
    print u"delete report ok"
    
    
#def delete_fqueue_file():
#    '''
#    清除 _fqueue文件下产生的垃圾文件
#    '''
#    fqueue=os.getcwd()+"\\_fqueue"
#    xx=os.listdir(fqueue)
#    for x in xx:
#        if x.find('.')<0:
#            print "delete "+ os.path.join(fqueue,x)
#            os.remove(os.path.join(fqueue,x))
#            
#    print 'delete ok'

def delete_att_photo(savdays=7):
    '''
    删除考勤照片
    '''
    dict = get_attsite_file()
    try:
        CLEAN_DAYS = str(dict["SYS"]["DELETE_DAYS"])
    except:
        pass
    today = datetime.datetime.now()
    try:
        CLEAN_DAYS = savdays
        deleteday = today+datetime.timedelta(days = -int(CLEAN_DAYS))
    except:
        CLEAN_DAYS = 0
        deleteday = today
    day_year=deleteday.strftime("%Y")
    month_day = deleteday.strftime("%m%d")
    tmp = os.getcwd()+"\\files\\model\\iclock.Transaction\\picture"
    tt = os.listdir(tmp)
    tt=os.listdir(tmp)
    for t in tt:
        zz = tt+"\\"+t
        pp = os.listdir(zz)
        for p in pp:
            if int(pp) < int(day_year):
                print 'delete ',zz+pp
                shutil.rmtree(zz+pp)
            elif int(pp) == int(day_year):
                hh = zz+"\\"+"pp"
                f_lists = os.listdir(hh)
                for f_list in f_lists:
                    if int(f_lists) < int(month_day) :
                        print 'delete',hh+pp
                        shutil.rmtree(hh+pp)
            
            
        
        
                    
    print u"delete report ok"
    
    


    
    
    
#delete_old_list(7)
#delete_temp_list()
#delete_report_list