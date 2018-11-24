#! /usr/bin/env python
#coding=utf-8

#
#设备通讯单元
#
# Changelog :
#
# 2010.2.3 Zhang Honggen
#   commit first version

import threading
from time import sleep, ctime
from ctypes import *
from mysite.utils import printf, write_log
import os
m_rtlog_buffer = None#获取实时监控事件时的buffer。默认16K

"""communication with device"""

#通讯错误定义

ERROR_COMM_OK                  =  0
ERROR_COMM_AUTH                =  -1
ERROR_COMM_REALM                =  -2
ERROR_COMM_URL                =  -3
ERROR_COMM_SOCKET            =  -4
ERROR_COMM_QUERY_EMPTY        =  -5
ERROR_COMM_HANDLE            =  -6
ERROR_COMM_TIMEOUT_D            =  -7
ERROR_COMM_SOCKET_SEND        =  -8
ERROR_COMM_SOCKET_RECV        =  -9

ERROR_COMM_PARAM                =  -100 
ERROR_COMM_QUERY                =  -101 
ERROR_COMM_TABLE                =  -102 
ERROR_COMM_FIELDS            =  -103 
ERROR_COMM_OPTIONS            =  -104 
ERROR_COMM_IO                =  -105 
ERROR_COMM_NO_MEM            =  -106 
ERROR_COMM_UPDATE_DATA        =  -107 
ERROR_COMM_UPDATE_PK            =  -108 
ERROR_COMM_FILTER_FIELD        =  -109 
ERROR_COMM_FILTER_OP            =  -110 
ERROR_COMM_FILTER_VAL_TIME    =  -111 
ERROR_COMM_UPDATE_OLDDATA    =  -112 
ERROR_COMM_UPDATE_SIZE        =  -113 
ERROR_COMM_UPDATE_ERROR        =  -114 
ERROR_COMM_UPDATE_NO_PK        =  -115
ERROR_COMM_UPDATE_NOUSER        =  -116
ERROR_COMM_UPDATE_FIELD        =  -117
ERROR_COMM_NO_SPACE            =  -118
ERROE_COMM_DELETE_SAVE        =  -119

g_rtlog_buf =""#实时事件buf，用于存放最近得到的实时事件
g_runing=1
g_teststop=1
g_reallog = []


"""
  设备通讯类，设备数据通讯接口
    
  数据命令通讯返回结果为 以下格式的字典：
  {"result":ret,"data":""}
  其中： 
  result表示命令是否成功，>=0表示成功,其值为返回数据的长度，<0表示失败，其值为错误ID
  data 表示返回的数据
"""

class TDevComm(object):        
    def __init__(self, comminfo):
        self.comminfo = comminfo
        self.commpro = windll.LoadLibrary("plcommpro.dll")
        self.connected = False
        self.hcommpro=0
        #self.str_buf_len = 8*1024*1024
        #self.str_buf = create_string_buffer(self.str_buf_len)

    def connect(self):
        params=""
        if (self.hcommpro>0):
            return {"result":self.hcommpro,"data":str(self.hcommpro)}
        if (self.comminfo["comm_type"] == 1):
            params=u"protocol=TCP,ipaddress=%s,port=%d,timeout=3000,passwd=%s"%(self.comminfo["ipaddress"], self.comminfo["ip_port"], self.comminfo["password"])
        elif (self.comminfo["comm_type"] == 2):
            params=u"protocol=RS485,port=%s,baudrate=%sbps,deviceid=%d,timeout=4000,passwd=%s"%(self.comminfo["com_port"], self.comminfo["baudrate"], self.comminfo["com_address"], self.comminfo["password"])        
        constr = create_string_buffer(params)
        #print params
        write_log("-----devcomm before connect the device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        self.hcommpro = self.commpro.Connect(constr)
        write_log("-----devcomm after connect the device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
       # printf("13. dev=%s, ret=%d"%(params, self.hcommpro))
        #print "Connect....",self.hcommpro
        if(self.hcommpro>0):
            self.connected = True
        else:
            error=self.get_last_error()
            if error > 0:
                error = 0 - error
            self.hcommpro = error
            self.connected = False
        return {"result": self.hcommpro, "data": str(self.hcommpro)}

    def disconnect(self):
        if self.hcommpro>0:
            write_log("-----devcomm before disconnect the device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
            self.commpro.Disconnect(self.hcommpro)
            write_log("-----devcomm before disconnect the device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        self.connected = False
        self.hcommpro = 0

    #更新设备数据，注意个参数前不要带空格
    def update_data(self,table,data,options):
        ptable = create_string_buffer(table)
        str_buf = create_string_buffer(data)
        write_log("-----devcomm before SetDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.SetDeviceData(self.hcommpro, ptable, str_buf, options)
        write_log("-----devcomm after SetDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return { "result": ret, "data": ""}

    #查询设备数据，注意个参数前不要带空格--非事件记录
    def query_data(self, table, fieldname, filter, option):
        ptable = create_string_buffer(table)
        pfieldname = create_string_buffer(fieldname)
        pfilter = create_string_buffer(filter)
        poption= create_string_buffer(option)
        str_buf_len = 6*1024*1024
        str_buf = create_string_buffer(str_buf_len)
        
        write_log("-----devcomm before GetDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.GetDeviceData(self.hcommpro, str_buf, str_buf_len, ptable, pfieldname, pfilter, poption)
        write_log("-----devcomm after GetDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        
        if(ret>=0):
            result = str_buf.raw
            result = result.split('\0')[0]
            return {"result":ret,"data":result}
        else:
            return {"result":ret,"data":""}
        
    #删除数据
    def delete_data(self,table,filter):
        ptable = create_string_buffer(table)
        pfilter = create_string_buffer(filter)
        write_log("-----devcomm before DeleteDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.DeleteDeviceData(self.hcommpro,ptable,pfilter,"")
        write_log("-----devcomm after DeleteDeviceData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result":ret,"data":""}
    
    #获取设备参数
    def get_options(self, items):
        op_buf = create_string_buffer(2048)
        pitems=create_string_buffer(items)
        write_log("-----devcomm before GetDeviceParam device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret=self.commpro.GetDeviceParam(self.hcommpro, op_buf, 2048, pitems)
        write_log("-----devcomm after GetDeviceParam device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        if (ret>=0):
            result = op_buf.raw
            result = result.split('\0')[0]
            return {"result":ret, "data":result}
        else:
            return {"result":ret, "data":""}

    #设置设备参数
    def set_options(self, items):
        pitems=create_string_buffer(items)
        write_log("-----devcomm before SetDeviceParam device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret=self.commpro.SetDeviceParam(self.hcommpro, pitems)
        write_log("-----devcomm after SetDeviceParam device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        #print "result=",ret,"  set_options:",items
        return {"result":ret, "data":""}

    #设备输出状态---远程开关门   index代表门或者辅助输出 1门 2辅助输出 state 开关状态
    def controldevice(self, doorid, index, state):      #输出状态, state由软件控制  
        write_log("-----devcomm before ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret=self.commpro.ControlDevice(self.hcommpro, 1, doorid, index, state, 0 , "")
        write_log("-----devcomm after ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result":ret,"data":""}

    #获取实时事件
    def get_rtlog(self):
        if self.hcommpro <= 0:
            return {'result':ERROR_COMM_HANDLE,'data':''}   #communication error
        global m_rtlog_buffer
        if not m_rtlog_buffer:
            m_rtlog_buffer = create_string_buffer(16*1024)#2048)#256

        write_log("-----devcomm before GetRTLog device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.GetRTLog(self.hcommpro, m_rtlog_buffer, 16*1024)
        write_log("-----devcomm after GetRTLog device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        if ret >= 0:
            rtlog = m_rtlog_buffer.raw
            rtlog = rtlog.split('\0')[0]
            return {"result": ret,"data": rtlog}
        else:
            return {"result": ret,"data": ""}

    def get_transaction(self, newlog=True, file_buffer=None, file_len=None):
        if (self.hcommpro <= 0) and newlog != "SD":#通过SD卡获取记录时不需要连接设备
            return {'result':ERROR_COMM_HANDLE,'data':''}   #communication error
        log=""
        ret = -1007
        str_buf_len = 8*1024*1024
        str_buf = create_string_buffer(str_buf_len)
        
        try:
            if newlog:
                if newlog == "SD":
                    ret = self.commpro.ProcessBackupData(file_buffer, file_len, str_buf, str_buf_len)
                else:
                    write_log("-----devcomm before GetDeviceData newlog device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
                    ret = self.commpro.GetDeviceData(self.hcommpro, str_buf, str_buf_len, "transaction", "*", "", "NewRecord");
                    write_log("-----devcomm after GetDeviceData newlog device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
                
            else:
                write_log("-----devcomm before GetDeviceData all logs device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
                ret = self.commpro.GetDeviceData(self.hcommpro, str_buf, str_buf_len, "transaction", "*", "", "");
                write_log("-----devcomm after GetDeviceData all logs device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        except Exception,e:
            printf("-----devcomm before GetDeviceData newlog device:%s e:%s"%(self.comminfo["ipaddress"], e), True)
            return {"result":ret, "data":""}            
        if ret >= 0:
            try:
                log = str_buf.raw
                str_buf = ""
                log = log.split('\r\n')
                return {"result":ret,"data":log}
            except:
                return {"result":ret,"data":""}
        else:
            return {"result":ret,"data":""}
        
    
    #只有该操作不需要先connect所以self.comminfo为None-darcy20110303
    def SearchDevice(self):
        dev_buf = create_string_buffer("", 64*1024)
        ret=self.commpro.SearchDevice("UDP", "255.255.255.255", dev_buf)
        if (ret>=0):
            result = dev_buf.raw
            result = result.split('\0')[0]
            return {"result":ret, "data":result}
        else:
            return {"result":ret, "data":""}
        
    def ModifyIPAddress(self, buffer):
        pbuffer = create_string_buffer(buffer)
        ret = self.commpro.ModifyIPAddress("UDP", "255.255.255.255", pbuffer)
        return {"result":ret, "data":""}
    
    def Get_Data_Count(self, table):
        ret = self.commpro.GetDeviceDataCount(self.hcommpro, table, "", "")
        return {"result":ret, "data":""}
    
    def get_last_error(self):
        return self.commpro.PullLastError()
    
    def cancel_alarm(self):
        write_log("-----devcomm before ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.ControlDevice(self.hcommpro, 2, 0, 0, 0, 0 , "")
        write_log("-----devcomm after ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result": ret, "data": ""}
    
    def reboot(self):
        write_log("-----devcomm before ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.ControlDevice(self.hcommpro, 3, 0, 0, 0, 0 , "")
        write_log("-----devcomm after ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result": ret, "data": ""}

    #控制常开时间段的启用和禁用
    def control_normal_open(self, doorid, state):
        write_log("-----devcomm before ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.ControlDevice(self.hcommpro, 4, doorid, state, 0, 0 , "")
        write_log("-----devcomm after ControlDevice device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result": ret, "data": ""}
    
    def upgrade_firmware(self, file_name, buffer, buff_len):
        pfile_name = create_string_buffer(file_name)
        pbuffer = create_string_buffer(buffer)
        write_log("-----devcomm before SetDeviceFileData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        ret = self.commpro.SetDeviceFileData(self.hcommpro, pfile_name, pbuffer, buff_len, "")
        write_log("-----devcomm after SetDeviceFileData device:%s pid=%d"%(self.comminfo["ipaddress"], os.getpid()))
        return {"result": ret, "data": ""}

#监控线程
class TThreadMonitor(object):
    def __init__(self,func,args):
        self.func = func
        self.args = args
                        
    def __call__(self):
        apply(self.func,self.args)

#实时监控函数，用于线程调用
def rt_monitor(devcomm, hcommpro):
    test_count = 0
    str_buf = create_string_buffer(10*1024)
    while(g_runing > 0):
        retlen = devcomm.GetRTLog(hcommpro,str_buf,100)
        if(retlen>0):
            rtlog_buf = str_buf.raw
            global g_rtlog_buf
            global g_reallog
            g_rtlog_buf = rtlog_buf.split('\0')[0]
#                        for rtlog in g_rtlog_buf:
#                                str="%d,%s"%(devcomm.devid, rtlog)
            g_reallog.append(g_rtlog_buf)
        sleep(0.5)

#取已得到的实时事件函数
def GetRTLogBuf(request):
    global g_rtlog_buf
    if len(g_rtlog_buf)<=0:
        html = "<TR>"+ "No data"  + "</TR>"
    else:
        html = "<TR>"+ g_rtlog_buf  + "</TR>"
    return HttpResponse(html)
   
#测试程序        
if __name__ == '__main__':
    print 'start at:', ctime()
    comminfo={
        'sn': 1,
        'comm_type':1,
        'ipaddress':'192.168.12.252',
        'ip_port':4370,
        'com_port':'COM1',
        'com_address':1,
        'password': 252,
        }
    dev = TDevComm(comminfo)
    hCommpro = dev.connect()
    if(hCommpro>0):
        str_buf = create_string_buffer(100)
        connect_info = 'connect success' #,IPAddress is %s' % ipaddr.raw
        rtlog = dev.get_rtlog()
        if(rtlog['len'] >0):
            print 'got rtlog :', rtlog['content']
    else:
        connect_info = 'connect failed'

    dev.disconnect()
    i = 0
    while True:
        i += 1
        dev.disconnect()
        hCommpro = dev.connect()
        print '---i=',i,'    --hCommpro=',hCommpro
        
        
        
    #print 'disconnect'
    #print 'all DONE at:', ctime()
    html="<TR>"+ connect_info +"</tr>"
    
    #print html
    #return HttpResponse(html)
    

