# -*- coding: utf-8 -*-
import sys
import socket
import time
import threading
from mysite.personnel.models.model_issuecard import IssueCard
from mysite.personnel.models.model_emp import Employee,getuserinfo
import random
from  decimal import Decimal
from mysite.iclock.models.model_device import Device
import threading,time,datetime
from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata
from mysite.pos.pos_ic.ic_sync_store import save_pos_file
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE
import urllib,urllib2
import datetime
import time
def online_getdata(sn,data_url,data_type = None):#在线采集消费数据
    from mysite.iclock.cache_cmds import get_device_raise
    a = time.time()
    device =  get_device_raise(sn)
#    request = 'http://192.168.10.141/data/?Action=Query&Table=PosLog&Fields=*&Filter=RecNo>10000 and RecNo<10010'
    request = 'http://192.168.10.192/data/?Action=Query&Table=PosLog&Fields=*&Filter='
    request_sn = 'http://192.168.10.192/data/?Action=InfoQuery&Items=System.SN'
    print request
    try:
        response_sn = urllib.urlopen(request_sn)
        return_sn = response_sn.readlines()[1:][0].split("=")[1].strip()
        if sn == return_sn: #验证设备序列号是否匹配
            response = urllib.urlopen(request)
        else:
            print u"设备序列号错误"
            return
    except Exception, e:
        print "lin_________________EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
        return
    row_list = response.readlines()[2:]
    field =  row_list[-1:][0].split("\t")
    STAMPID = field[5] #获取当批记录的最大流水号
    head_data=":pos_log_stamp: SN=%s\tIP=192.168.10.141\tTIME=%s\tSTAMP=8888\tSTAMPID=%s\tZ=%s"%(str(device.sn).strip(),
         datetime.datetime.now(),STAMPID,'1')
   
    for index in range(len(row_list)):
#        print "row_list[index]====",row_list[index].replace(row_list[index].split("\t")[2],datetime.datetime.strptime(row_list[index].split("\t")[2],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"))
        list_item = row_list[index].split("\t")[2]
        f_time = "".join([list_item[0:4],"-",list_item[4:6],"-",list_item[6:8]," ",list_item[8:10],":",list_item[10:12],":",list_item[12:14]])
        row_list[index] = row_list[index].replace(row_list[index].split("\t")[2],f_time)
    b = time.time()
    rawData = " ".join(row_list)
    try:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    except:
        s_data="%s\n%s\n\n"%(head_data, rawData)
    
    if POS_IC_ADMS_MODEL:
        obj = save_pos_file(device,s_data)
    else:
        obj=pos_gen_device_cmmdata(device,s_data)
    c = time.time()
    print "format==============",c-a
#    print s_data
