# -*- coding: utf-8 -*-
#! /usr/bin/env python
#
#设备通讯进程池
#
# Changelog :
#
# 2010.3.19 Zhang Honggen
#   create at zk park Dongguan

from multiprocessing import Pool, Process#pool tcp/ip---proess 485
import threading
import time
import datetime
from time import sleep, ctime
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.db import models, connection
import os, re
import redis_self
import dict4ini
from redis_self.server import queqe_server, start_dict_server
from mysite.iaccess.devcomm import TDevComm
from mysite.iaccess.devcomm import *
from traceback import print_exc
from mysite.utils import printf, delete_log, write_log
from ctypes import *
from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, COMMU_MODE_PULL_RS485, COMMU_MODE_PULL_TCPIP, ACCDEVICE_DISABLED
from mysite.personnel.models.model_emp import format_pin
from mysite.iaccess.models import AccRTMonitor, AccDoor
from base.middleware import threadlocals
from django.db import IntegrityError
from django.conf import settings
import dict4ini
from process_comm_data import strtodatetime, strtoint, str_to_date, is_comm_io_error, delete_tempcmd, set_doorstr,\
        obtain_doorobj_from_log, sync_to_att, FmtTTime
        
from mysite.iaccess.linux_or_win import run_commend

#from base.options import AppOption,Option
from mysite.iaccess.linux_or_win import run_commend
try:
    import cPickle as pickle
except:
    import pickle

#20121120
import sqls
cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini", values={"iaccess":{"reconnect_time":60}})

MAX_TRY_COMM_TIME   = 20#监控时重连20次后设备断开
MAX_CONNECT_COUNT   = 60*24*30   #重连一个月失败后禁用  每3分钟重连一次
#MAX_INTERVAL_CONNTECT_TIME = 60#暂停一分钟后重连
MAX_INTERVAL_CONNTECT_TIME = cfg.iaccess.reconnect_time and int(cfg.iaccess.reconnect_time) or 60#设备断开重连时间
PAUSE_TIMEOUT   =   60      #485暂停超时60秒

g_devcenter = None
g_cursor = connection.cursor()

G_DEVICE_CONNECT  = "CONNECT"
G_DEVICE_DISCONNECT  = "DISCONNECT"
G_DEVICE_UPDATE_DATA = "DATA UPDATE"
G_DEVICE_QUERY_DATA = "DATA QUERY"
G_DEVICE_DELETE_DATA = "DATA DELETE"
G_DEVICE_GET_DATA="DEVICE GET"
G_DEVICE_SET_DATA="DEVICE SET"
G_DEVICE_CANCEL_ALARM = "CANCEL ALARM"
G_DEVICE_CONTROL_NO = "CONTROL NO"
G_DEVICE_UPGRADE_FIRMWARE = "UPGRADE FIRMWARE"
G_DEVICE_GET_OPTION = "OPTION GET"
G_DEVICE_SET_OPTION = "SET OPTION"
G_REAL_LOG = "REAL_LOG"
G_DOWN_NEWLOG = "DOWN_NEWLOG"
G_QUEUE_ERROR = "QUEUE_ERROR"
G_CHECK_SERVICE = "CHECK_SERVICE"
G_DATA_COUNT="DATA COUNT"

GR_RETURN_OK =  200
from models.accmonitorlog import DOOR_STATE_ID, EVENT_LINKCONTROL,CANCEL_ALARM, OPEN_AUXOUT, CLOSE_AUXOUT, EVENT_DOORSENSOROPEN,EVENT_DOORSENSORCLOSE, INOUT_SEVER, INOUT_SHORT, ALARM_ID_START, ALARM_ID_END

MAX_RTLOG               = 500#10#1000 #实时事件最大缓存 5000

TRY_USE_DISK_FILE_CMD_COUNT = 512    #尝试实际检查硬盘命令文件中是否有命令

DEVOPT="DEV_OPERATE"        #设备操作缓存, 新增、修改、删除设备操作
CENTER_PROCE_HEART="CENTER_HEART_%s"
CENTER_PROCE_LIST = "CENTER_PROCE_LIST"
CENTER_MAIN_PID = "CENTER_MAIN_PID"

OPERAT_ADD  =1
OPERAT_EDIT =2
OPERAT_DEL  =3

PROCESS_NORMAL      = 0
PROCESS_WAIT_PAUSE  = 1
PROCESS_PAUSE       = 2

THREAD_NORMAL      = 0
THREAD_WAIT_PAUSE  = 1
THREAD_PAUSE       = 2


DEVICE_COMMAND_TABLE = [
    _(u'人员信息'),
    _(u'门禁权限信息'),
    _(u'节假日设置'),
    _(u'时间段设置'),
    _(u'首卡常开设置'),
    _(u'多卡开门设置'),
    _(u'事件记录'),
    _(u'联动设置'),
    _(u'指纹数据')
]
DEVICE_MONITOR_CONTENT = [
    _(u'更新数据:'),
    _(u'查询数据:'),
    _(u'删除数据:'),
    _(u'获取设备状态'),
    _(u'设置设备状态'),
    _(u'获取设备参数:'),
    _(u'设置设备参数:'),
    _(u'连接设备'),
    _(u'获取实时事件'),
    _(u'获取新记录'),
    _(u'连接断开'),
    _(u'取消报警'),
    _(u'命令队列检测'),
    _(u'数据中心服务检测'),
    _(u'获取记录数'),
]

#执行失败:
DEVICE_COMMAND_RETURN = {
    '0': _(u'正常'),
    '-1': _(u'命令发送失败'),
    '-2': _(u'命令超时'),
    '-3': _(u'需要的缓存不足'),
    '-4': _(u'解压失败'),
    '-5': _(u'读取数据长度错误'),
    '-6': _(u'通讯错误'), #解压的长度和期望的长度不一致
    '-7': _(u'命令重复'),
    '-8': _(u'连接尚未授权'),
    '-9': _(u'数据错误，CRC校验失败'),
    '-10': _(u'数据错误，SDK无法解析'),#数据错误，PullSDK无法解析
    '-11': _(u'数据参数错误'),
    '-12': _(u'命令执行错误'),
    '-13': _(u'命令错误，没有此命令'),
    '-14': _(u'通讯密码错误'),
    '-15': _(u'写文件失败'),#固件将文件写到本地时失败
    '-16': _(u'读文件失败'),
    '-17': _(u'文件不存在'),#读取时找不到文件
    '-18': _(u'存储空间已满'),
    '-19': _(u'校验和出错'),
    '-20': _(u'数据长度错误'),#接受到的数据长度与给出的数据长度不一致
    '-21': _(u'没有设置平台参数'),
    '-22': _(u'固件平台不一致'),#固件升级，传来的固件的平台与本地的平台不一致
    '-23': _(u'升级的固件版本过旧'),#升级的固件版本比设备中的固件版本老
    '-24': _(u'升级文件标识出错'),#升级的文件标识出错
    '-25': _(u'文件名错误'),#固件升级，传来的文件名不对，即不是emfw.cfg
    '-26': _(u'指纹模板长度不能为0'),#传来的指纹模板长度为0
    '-27': _(u'找不到指纹模板对应用户'),#传来的指纹模板PIN号错误,找不到用户

    '-99': _(u'未知错误'),
    '-100': _(u'表结构不存在'),
    '-101': _(u'表结构中，条件字段不存在'),
    '-102': _(u'字段总数不一致'),
    '-103': _(u'字段排序不一致'),
    '-104': _(u'实时事件数据错误'),
    '-105': _(u'解析数据时，数据错误'),
    '-106': _(u'数据溢出，下发数据超出4M'),
    '-107': _(u'获取表结构失败'),
    '-108': _(u'无效OPTIONS选项'),
    '-126': _(u'库文件不存在或者加载失败'),

    #PC端错误 说明当前通讯异常
    '-201': _(u'库文件不存在'), #LoadLibrary失败
    '-202': _(u'调用接口失败'),
    '-203': _(u'通讯初始化失败'),
    '-206': _(u'串口被占用或串口不存在'),
    '-301': _(u'获取TCP/IP版本失败'),#？？？？？？？？？？？？？？
    '-302': _(u'错误的TCP/IP版本号'),
    '-303': _(u'获取协议类型失败'),
    '-304': _(u'无效SOCKET'),
    '-305': _(u'SOCKET错误'),
    '-306': _(u'HOST错误'),
    '-307': _(u'连接超时'),

    '-1001': _(u'连接断开'),#设备离线。含设备刚被disconnect，hcommpro=0的情况

    '-1002': _(u'禁用'),
    '-1003': _(u'服务未启动'),#数据中心服务未启动
    '-1004': _(u'设备线程暂停'),
    '-1005': _(u'后台处理命令失败'),
    '-1006': _(u'未知命令'),#新增，命令不合法
    '-1007': _(u'获取事件记录失败'),#抛异常，需要查看日志文件-darcy20111222
    '-1100': _(u'队列异常! 请取消队列后重新同步数据'),#

    '1000': _(u'获取新记录'),
    '1001': _(u'正在连接'),
}

#-201 调用库文件失败
#-202 库接口调用失败
#-203 通讯初始化失败
#-204 连接失败，其它错误
#-301-304   底层连接初始化失败

def get_cmd_table(cmd_str):
    retstr=""
    if (cmd_str.startswith('userauthorize')):
        retstr=unicode(DEVICE_COMMAND_TABLE[1])
    elif (cmd_str.startswith('user')):
        retstr=unicode(DEVICE_COMMAND_TABLE[0])
    elif(cmd_str.startswith('holiday')):
        retstr=unicode(DEVICE_COMMAND_TABLE[2])
    elif(cmd_str.startswith('timezone')):
        retstr=unicode(DEVICE_COMMAND_TABLE[3])
    elif(cmd_str.startswith('firstcard')):
        retstr=unicode(DEVICE_COMMAND_TABLE[4])
    elif(cmd_str.startswith('multimcard')):
        retstr=unicode(DEVICE_COMMAND_TABLE[5])
    elif(cmd_str.startswith('transaction')):
        retstr=unicode(DEVICE_COMMAND_TABLE[6])
    elif cmd_str.startswith('inoutfun'):
        retstr = unicode(DEVICE_COMMAND_TABLE[7])
    elif cmd_str.startswith('templatev10'):
        retstr = unicode(DEVICE_COMMAND_TABLE[8])
    return retstr

def get_cmd_content(cmd_str):
    comm_param=cmd_str.strip()
    retstr=""
    if (comm_param.startswith(G_QUEUE_ERROR)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[12])
    if (comm_param.startswith(G_DEVICE_CONNECT)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[7])
    elif (comm_param.startswith(G_REAL_LOG)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[8])
    elif (comm_param.startswith(G_DOWN_NEWLOG)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[9])
    elif (comm_param.startswith(G_DEVICE_DISCONNECT)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[10])
    elif (comm_param.startswith(G_DEVICE_UPDATE_DATA)):
        strs = comm_param.split(" ", 3)
        table = strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[0])+get_cmd_table(table)
    elif (comm_param.startswith(G_DEVICE_QUERY_DATA)):
        strs = comm_param.split(" ", 4)
        table = strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[1])+get_cmd_table(table)
    elif(comm_param.startswith(G_DEVICE_DELETE_DATA)):
        strs = comm_param.split(" ", 3)
        table = strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[2])+get_cmd_table(table)
    elif(comm_param.startswith(G_DATA_COUNT)):
        strs = comm_param.split(" ", 3)
        table = strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[14])+get_cmd_table(table)
    elif(comm_param.startswith(G_DEVICE_GET_DATA)):
        retstr=unicode(DEVICE_MONITOR_CONTENT[3])
    elif(comm_param.startswith(G_DEVICE_SET_DATA)):
        strs = comm_param.split(" ", 5)
        retstr=unicode(DEVICE_MONITOR_CONTENT[4])
    elif(comm_param.startswith(G_DEVICE_GET_OPTION)):
        strs = comm_param.split(" ", 2)
        opt=strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[5])+opt
    elif(comm_param.startswith(G_DEVICE_SET_OPTION)):
        strs = comm_param.split(" ", 3)
        opt=strs[2]
        retstr=unicode(DEVICE_MONITOR_CONTENT[6])+opt
    elif comm_param.startswith(G_DEVICE_CANCEL_ALARM):
        strs = comm_param.split(" ")
        opt = strs[2]
        retstr = unicode(DEVICE_MONITOR_CONTENT[7]) + opt
    elif comm_param.startswith(G_CHECK_SERVICE):
        retstr = unicode(DEVICE_MONITOR_CONTENT[13])
    #print '---retstr=',retstr #只能用于命令行调试，否则unicode错误
    return retstr

#检查服务是否启动 True启动，False未启动
def check_service_commcenter(d_server):
    ret = d_server.get_from_dict("CENTER_RUNING")
    if ret:
        return True
    else:
        return False
#    #return True
#    s = os.popen("sc.exe query ZKECODataCommCenterService").read()
#    if ": 1  STOPPED" in s:
#        return False
#    return True

#将门状态写入缓存中
def set_door_connect(device, vcom, d_server):
    try:
        doorstate = d_server.get_from_dict(device.get_doorstate_cache_key())
    except Exception, e:
        printf("set_door_connect 1 error=%s"%e)

#    print "doorstate=",doorstate
    if doorstate is None:
        doorstate="0,0,0"
    doorstr=doorstate.split(",", 3)
    if vcom > 0:#"DEVICE_DOOR_%s"%self.id
        try:
            d_server.set_to_dict(device.get_doorstate_cache_key(), "%s,%s,%d"%(doorstr[0],doorstr[1], vcom))
        except Exception, e:
            printf("set_door_connect 2 error=%s"%e)
    else:
        try:
            d_server.set_to_dict(device.get_doorstate_cache_key(), "0,0,0")#没连接上  set
        except Exception, e:
            printf("set_door_connect 3 error=%s"%e)
    #print '---getdoorstate=',d_server.get_from_dict(device.get_doorstate_cache_key())

def checkdevice_and_savecache(d_server, devobj, cursor):
    from mysite.iclock.models import Device
    last_activity_time = d_server.get_from_dict(devobj.get_last_activity())
    
    #修改最后连接时间
    if last_activity_time:
        now_t = time.mktime(datetime.datetime.now().timetuple())
        if float(last_activity_time) > now_t:
            d_server.set_to_dict(devobj.get_last_activity(), "1")
        elif now_t - float(last_activity_time) > 120:
            #print '---120-checkdevice_and_savecache'
            from django.db import IntegrityError#, InterfaceError
            try:
                #print '----all devices=', Device.objects.all()
#                dev = Device.objects.get(id = devobj.id)
#                dev.last_activity = datetime.datetime.now()
                last_activity = datetime.datetime.now().strftime("%Y-%m-%d %X")
                #cursor = connection.cursor()
                sql=sqls.checkdevice_and_savecache_update(last_activity,devobj.id)
                #sql = "update iclock set last_activity = '%s' where id = %s"%(last_activity,devobj.id)
                cursor.execute(sql)
                connection._commit() 
                #print '--------------------------------last activity00000001111'
                #connection.close()不能关闭，其他地方还要调用-darcy20120105             
#                dev.save(force_update=True, log_msg=False)
                d_server.set_to_dict(devobj.get_last_activity(), str(now_t))
            except IntegrityError:
                connection._commit()
                pass
                #checkdevice_and_savecache(d_server, devobj, g_cursor)
#            except InterfaceError:
#                connection._commit()
#                pass
            except Exception, e:
                connection.close()
                global g_cursor
                #print '-----------re get g_cursor'
                g_cursor = connection.cursor()
                #print '--checkdevice_and_savecache--e=',e
                #print '--------------------------------last activity00000002222'
                connection._commit()
                print_exc()
                pass
    else:
        d_server.set_to_dict(devobj.get_last_activity(), "1")

def appendrtlog(d_server, cursor, devobj, rtlog):
    from mysite.iaccess.models import AccRTMonitor
    from base.middleware import threadlocals
    try:
        rtlogs = rtlog.split("\r\n")
        operator = threadlocals.get_current_user()
        if not cursor:
            cursor = connection.cursor()
        try:
            dev_door_list = AccDoor.objects.filter(device=devobj)  #读设备门列表到缓存
            dev_door_dict = {}#使用字典，减少循环次数
            for obj in dev_door_list:
                dev_door_dict[obj.door_no] = obj
                
            for rtlog in rtlogs:#修改支持一次获取多条事件记录
                if not rtlog:#非记录
                    continue
                #print '---rtlog=',rtlog
                str = rtlog.split(",",7)
                #print '---appendrtlog---str=',str
                #doorstr=""
                if len(str) < 7:      #不合规范数据
                    return 0
                if strtoint(str[4]) == DOOR_STATE_ID:#0时间+1门开关状态+2报警或门开超时+3没用+4（255标明该事件为门状态，否则为事件）+5 没用+6验证方式（200其他）
#                    d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%s,%s,1"%(str[1],str[2]))
#                    if d_server.get_from_dict("NEXT_STATE_BREAK"):   #全局变量进行判断
#                        d_server.set_to_dict("GET_DOORSTATE_AGAIN", 1)
#                        d_server.set_to_dict("NEXT_STATE_BREAK", 0)
#                        return
#                if ((strtoint(str[4]) >= ALARM_ID_START) and (strtoint(str[4]) < ALARM_ID_END)) or (strtoint(str[4]) in [CANCEL_ALARM, EVENT_DOORSENSOROPEN, EVENT_DOORSENSORCLOSE]):
#                    d_server.set_to_dict("NEXT_STATE_BREAK", 1)  #立即返回
                    door_state = d_server.get_from_dict(devobj.get_doorstate_cache_key())#从缓存中获取设备门上次的状态  --by huangjs20120310
                    if door_state:
                        val = door_state.split(",", 3)
                        if str[1] != val[0] or str[2] != val[1]:#如果门状态或者报警状态改变，告诉后台立即返回门状态给前端
                            #print '----change---'
                            now_t = time.mktime(datetime.datetime.now().timetuple())#取得当前门状态改变的时间
                            d_server.set_to_dict("GET_DOORSTATE_AGAIN", now_t)#以类似时间戳的方式判断门状态
                    d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%s,%s,1"%(str[1],str[2]))#将设备门状态和报警状态放到缓存
                    return
                           
                doorobj = None
                try:
                    if int(str[3]) in dev_door_dict:
                        doorobj = dev_door_dict[int(str[3])]
                    doorobj = obtain_doorobj_from_log(str, doorobj)
                    if doorobj is not None:
                        str[3] = doorobj and doorobj.id or 0
                except:
                    print_exc()

                #if d_server.llen("MONITOR_RT")<MAX_RTLOG:
                try:
                    log = "%s,%s,%s,%s,%s,%s,%s,%d"%(str[0],str[1],str[3],str[4],str[5], str[6], str[2], devobj and devobj.id or 0)
                    #write_log("---log=%s"%log)
                    d_server.rpush_to_dict("MONITOR_RT", log)#{"MONITOR_RT':['log1','log2']}
                    #print '-----get====monitor_rt=',d_server.get_from_dict("MONITOR_RT")
                except:
                    print_exc()

                if (strtoint(str[4]) >= ALARM_ID_START) and (strtoint(str[4]) < ALARM_ID_END):
                    d_server.rpush_to_dict("ALARM_RT", log)
                #time, Pin, cardno, doorID, even_type, reserved, verified
                save_event_log(str, cursor, operator, doorobj, devobj, d_server)
                if doorobj and doorobj.is_att:
                    from  models.accmonitorlog import EVENT_LOG_AS_ATT
                    #if ((strtoint(str[4]) >= 0) and (strtoint(str[4]) <=2)) or ((strtoint(str[4]) >= 21) and (strtoint(str[4]) <=23)) or (strtoint(str[4]) == 5):
                    if strtoint(str[4]) in EVENT_LOG_AS_ATT:
                        try:
                            sync_to_att(cursor, devobj, str[1], str[0])
                        except:
                            #print_exc()
                            pass#写入考勤原始记录表时，避免抛出异常时终止插入。darcy20111205
        finally:
            pass
    except:
        print_exc()

#传入的split_log为原始记录分解之后的。分别为time, Pin, cardno, doorID, even_type, reserved, verified
def save_event_log(split_log, cursor, operator, doorobj, devobj=None, d_server=None):
    try:
        event_sql = parse_event_to_sql(split_log, operator, doorobj, devobj, d_server)
        sql = event_sql and event_sql[0]
        params = event_sql and event_sql[1]
#        print 'sql=',sql
#        print 'params=',params
        cursor.execute(sql, params)
        #print '------before commit'
        connection._commit()
        #print '------after commit'
    except IntegrityError:
        #print_exc()
        connection._commit()
        #printf('------save_event_log IntegrityError', True)
        pass
#    except InterfaceError:
#        print_exc()
#        connection._commit()
#        pass
    except Exception, e:
        connection.close()#必须先断开，才能重新建立，否则无效-darcy20120110
        #d_server.set_to_dict("DATABASE_ERROR", 1)
        #print_exc()

        while(1):#避免扔掉数据，直到数据库重新连接上后再将该条记录插入---darcy20120113
            try:
                time.sleep(3)#3秒。避免CPU过于繁忙-darcy20120113
                #print '----before re get the cursor'
                global g_cursor
                g_cursor = connection.cursor()
                #print '-----cursor=',cursor
                save_event_log(split_log, g_cursor, operator, doorobj, devobj, d_server)
                #print '---break'
                break
            except Exception, e:
                #print '---while 1 continue e=', e
                continue
            
        #print '---after save_event_log'
        printf('--------execute sql e=%s'%e, True)
        pass

#处理获取到的事件记录，含 定时获取新纪录，手动获取所有记录、新记录，实时监控时获取实时记录。--jianght20110328
def process_event_log(dev, qret, cursor=None, d_server=None):
    if qret['result'] >= 0:
        from  models.accmonitorlog import EVENT_LOG_AS_ATT
        cursor = connection.cursor()
        try:
            operator = threadlocals.get_current_user()
            dev_door_list = AccDoor.objects.filter(device=dev)  #读设备门列表到缓存
            dev_door_dict = {}#使用字典，减少循环次数
            for obj in dev_door_list:
                dev_door_dict[obj.door_no] = obj
            
            event_sql_list = []#存储sql语句
            event_params_list = []#存储sql语句参数
            params = []#要执行的批量sql语句的参数
            device_event_dict = {}#存放设备在数据库中的事件记录
            att_event_dict = {}#考勤原始记录表
            emp_dict = {}#所有人员的编号，id
            att_event_has_search = False#标志是否已经查询了考勤数据
            att_event_sql_list = []
            sn_name = dev.sn
            dev_id = dev.id
            min_time = ""
            
            printf('--------begin-time=%s'%dev, True)
            #首次循环，取出全部事件中最小的时间
            for i in range(1, qret['result']+1, 1):
                log = qret['data'][i]
#                print '%s====%s'%(i,log) 
                str = log.split(",",7)
                tmp_time = FmtTTime(str[6])
                if not min_time or min_time > tmp_time:#取得最小时间
                    min_time = tmp_time
            #print '-----------min_time===', min_time    
            for i in range(1, qret['result']+1, 1):
                log = qret['data'][i]
                str = log.split(",",7)
                doorobj = None
                try:
                    if int(str[3]) in dev_door_dict:
                        doorobj = dev_door_dict[int(str[3])]
                    doorobj = obtain_doorobj_from_log(str,doorobj)
                    if doorobj:
                        str[3] = doorobj and doorobj.id or 0
                except Exception, e:
                    print_exc()
                    
                try:
                    #print '---str=',str
                    restr = "%s,%s,%s,%s,%s,%s,%s"%(FmtTTime(str[6]),str[1],str[0],str[3],str[4],str[5],str[2])
                    restr = restr.split(',', 7)#????
                 
                    #save_event_log(restr, cursor, operator, doorobj, dev, d_server)    #保存数据至数据库
                except:
                    print_exc()
                    continue
                
                if i == 1:#获取记录，第一条为最旧的数据，查询时间比它大的记录， 以唯一约束建为字典的键值，放到缓存中---huangjs20120611
                    #device_event_sql = "select time,pin,card_no,device_id,door_id,in_address,verified,state,event_type,trigger_opt from acc_monitor_log where device_id=%s and time>'%s'"%(dev_id, restr and restr[0])
                    device_event_sql=sqls.process_event_log_select1(dev_id, restr)
                    printf('----device_event_sql----process_event_log=%s'%device_event_sql, True)
                    try:
                        cursor.execute(device_event_sql)
                        rets = cursor.fetchall()
#                        print '=rets=',rets
                        for ret in rets:
                            key = "%s_%s_%s_%s_%s_%s_%s_%s_%s_%s"%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7], ret[8], ret[9])
                            device_event_dict[key] = 1#只需要键来判断获取到的数据是否已在数据库中，值可以任意取---huangjs20120612
#                        print '----device_event_dict=', device_event_dict
                    except Exception, e:
                        #printf('--------device_event_sql-----e=%s'%e, True)
                        pass
                
                sql_and_param = parse_event_to_sql(restr, operator, doorobj, dev, d_server)#解析事件记录，获取sql语句
                param = sql_and_param and sql_and_param[1] or []
                sql = sql_and_param and sql_and_param[0] or []
                
                #当前记录的键
                cur_key = "%s_%s_%s_%s_%s_%s_%s_%s_%s_%s"%(param and param[2], param and param[3], param and param[4], param and param[5],
                        param and param[8],param and param[10],param and param[11], param and param[12], param and param[13], param and param[14],
                )
#                print '----cur_key==', cur_key   
                if param and sql and cur_key not in device_event_dict:
                    event_sql_list.append(sql)
                    event_params_list.append(param)#用于失败时，保存参数的分隔---huangjs
                    params += param
                if len(event_sql_list) == 130:#采用双参数，避免出现国际编码出现乱码问题，sqlserver数据库参数长度有限定，现只能每次130条，再多会报出错
                    execute_batch_sql(event_sql_list, params, event_params_list, cursor)
                    event_sql_list = []
                    event_params_list = []
                    params = []

                if doorobj and doorobj.is_att and strtoint(restr[4]) in EVENT_LOG_AS_ATT:#门禁带考勤，cursor全局，只能抽取出来放在同一个文件下
                    if not att_event_has_search:
                        #查询大于这个时间的考勤原始记录信息
                        #att_sql = "select badgenumber, checktime from checkinout c, userinfo u where c.userid=u.userid and checktime>'%s'"%strtodatetime(restr[0])
                        att_sql=sqls.process_event_log_select2(restr[0])
                        cursor.execute(att_sql)
                        att_rets = cursor.fetchall()
                        for ret in att_rets:
                            key = "%s_%s"%(ret[0], ret[1])
                            att_event_dict[key] = 1
                        #print '---------------att_event_dict===', att_event_dict
                        
                        #查询全部人员的编号，id   
                        #emp_sql = "select badgenumber, userid from userinfo"
#                        emp_sql=sqls.process_event_log_select3()
#                        cursor.execute(emp_sql)
#                        emp_rets = cursor.fetchall()
#                        for ret in emp_rets:
#                            emp_dict[ret[0]] = ret[1]
                        #print '-----------------emp_dict====', emp_dict
                        att_event_has_search = True#标志已经获取过考勤原始记录---huangjs
                        
                    restr[1] = format_pin(restr[1])
                    cur_att_event_key = "%s_%s"%(restr[1], restr[0])#当前的记录键值
                    
                    if cur_att_event_key not in att_event_dict:
#                        if restr[1] in emp_dict:
                            #sql = "insert into checkinout(sn_name, userid, checktime) values('%s', %s, '%s');"%(sn_name, emp_dict[restr[1]],strtodatetime(restr[0]))
#                            sql=sqls.process_event_log_insert(sn_name, emp_dict[restr[1]],strtodatetime(restr[0]))
#                            att_event_sql_list.append(sql)
                        sql=sqls.process_event_log_insert(sn_name, restr[1],strtodatetime(restr[0]))
                        att_event_sql_list.append(sql)
                    if len(att_event_sql_list) == 1000:#考勤直接执行，每次1000条
                        execute_batch_sql(att_event_sql_list, None, None, cursor)
                        att_event_sql_list = []
                
        
            #不到130条的门禁记录，批量插入
            if event_sql_list:
                execute_batch_sql(event_sql_list, params, event_params_list, cursor)
            
            if att_event_sql_list:
                execute_batch_sql(att_event_sql_list, None, None, cursor)
        except Exception, e:
            #print '--------123----eee==', e
            printf('---2-----process_event_log e=%s'%e, True)
        finally:
            event_sql_list = None
            event_params_list = None
            params = None
            device_event_dict = None
            att_event_dict = None
            emp_dict = None
            att_event_sql_list = None
        printf('-------finish-time=%s'%dev, True)
        return {"ret": qret['result'], "retdata": ""}
    else:
        return {"ret": -1, "retdata": ""}
  

#将传入的事件记录解析，返回sql语句， 传入的split_log为原始记录分解之后的。分别为time, Pin, cardno, doorID, even_type, reserved, verified-----huangjs20120607
def parse_event_to_sql(split_log, operator, doorobj, devobj=None, d_server=None):
    dev_id = 0
    dev_name = ""
    dev_sn = ""
    door_id = 0
    door_name = ""

    if devobj:
        try:
            dev_id = devobj.id
            dev_name = unicode(devobj.alias)
            dev_sn = devobj.sn
        except:
            print_exc()

    if doorobj:
        try:
            door_id = doorobj.id
            door_name = unicode(doorobj.door_name)
        except:
            print_exc()

    device_name_field = AccRTMonitor._meta.get_field("device_name")
    door_name_field = AccRTMonitor._meta.get_field("door_name")
    dev_name = device_name_field.get_db_prep_save(dev_name, connection=connection)
    door_name = door_name_field.get_db_prep_save(door_name, connection=connection)
    
    #单条事件结构信息 先初始化，后面再根据实际情况更改
    transaction_struct = {}
    transaction_struct['change_time'] = None
    transaction_struct['create_operator'] = None             #问题：后台进程无法获取操作用户
    transaction_struct['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    transaction_struct['delete_operator'] = None
    transaction_struct['delete_time'] = None
    transaction_struct['time'] = strtodatetime(split_log[0])
    transaction_struct['card_no'] = split_log[2] and int(split_log[2]) or "--"
    transaction_struct['pin'] =  int(split_log[1]) and format_pin(split_log[1]) or "--"
    transaction_struct['state'] =(len(split_log[5])>0) and split_log[5] or 0
    transaction_struct['event_type'] = (len(split_log[4])>0) and split_log[4] or 0
    transaction_struct['status'] = 0
    transaction_struct['verified'] = 200
    transaction_struct['in_address'] = -1
    transaction_struct['out_address'] = -1
    transaction_struct['trigger_opt'] = -1
    transaction_struct['device_id'] = dev_id
    transaction_struct['device_name'] = dev_name#设备是一定有的
    transaction_struct['device_sn'] = dev_sn
    transaction_struct['door_id'] = 0#不能为None，否则None转换成int时会失败
    transaction_struct['door_name'] = None

    if strtoint(split_log[4]) in [INOUT_SEVER, INOUT_SHORT]:                 #辅助输入
        transaction_struct['in_address'] = (len(split_log[3])>0) and split_log[3] or 0

    elif strtoint(split_log[4]) in [OPEN_AUXOUT, CLOSE_AUXOUT]:              #辅助输出
        transaction_struct['out_address'] = (len(split_log[3])>0) and split_log[3] or 0

    elif strtoint(split_log[4]) == EVENT_LINKCONTROL:                        #联动
        if strtoint(split_log[6]) in [INOUT_SEVER, INOUT_SHORT]:
            transaction_struct['in_address'] = (len(split_log[3])>0) and split_log[3] or 0
            transaction_struct['trigger_opt'] = (len(split_log[6])>0) and split_log[6] or 0
            transaction_struct['card_no'] = "--"                        #联动记录中卡号字段的位置被联动id复用
        else:
            transaction_struct['door_id'] = door_id
            transaction_struct['door_name'] = door_name
            transaction_struct['card_no'] = "--"
            transaction_struct['trigger_opt'] = (len(split_log[6]) > 0) and split_log[6] or 0
    else:
        transaction_struct['verified'] = (len(split_log[6])>0) and split_log[6] or 0
        #transaction_struct['device_id'] = dev_id
        #transaction_struct['device_name'] = dev_name
        transaction_struct['door_id'] = door_id
        transaction_struct['door_name'] = door_name

    #sql = "INSERT INTO acc_monitor_log(change_operator,change_time,create_operator,create_time,delete_operator,delete_time,status,time,pin,card_no,device_id,device_sn,device_name,door_id,door_name,in_address,verified,state,event_type,trigger_opt,out_address) values(NULL,NULL,%s,%s,NULL,NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#    sql = "INSERT INTO acc_monitor_log(change_operator,change_time,create_operator,create_time,delete_operator,delete_time,status,time,\
#            pin,card_no,device_id,device_sn,device_name,door_id,door_name,in_address,verified,state,event_type,trigger_opt,out_address) \
#            values(NULL,NULL,NULL,%s,NULL,NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
#    print '============'
    sql=sqls.parse_event_to_sql_insert()
    params = [
            transaction_struct['create_time'],
            transaction_struct['status'],
            transaction_struct['time'],
            transaction_struct['pin'],
            transaction_struct['card_no'],
            transaction_struct['device_id'],
            transaction_struct['device_sn'],
            transaction_struct['device_name'],
            transaction_struct['door_id'],
            transaction_struct['door_name'],
            transaction_struct['in_address'],
            transaction_struct['verified'],
            transaction_struct['state'],
            transaction_struct['event_type'],
            transaction_struct['trigger_opt'],
            transaction_struct['out_address']
    ]
    return [sql, params]

#批量执行插入，batch_sql:批量sql语句，params批量sql语句的参数值， params_list:每条sql语句的参数值，列表，约束冲突时使用----huangjs20120626
def execute_batch_sql(batch_sql, params=None, params_list=None, cursor=None):
    from django.db import IntegrityError
#    print 'batch_sql=',batch_sql
#    print 'batch-params=',params
    if not cursor:
        cursor = connection.cursor()
    try:
        batch_sql = ''.join(batch_sql)
        if params:
            params = tuple(params)
            cursor.execute(batch_sql, params)
        else:
            cursor.execute(batch_sql)
    except IntegrityError:
        sql_list = batch_sql.split(';')
        for i, sql in enumerate(sql_list):
            try:
                if params_list and params_list[i]:
                    cursor.execute(sql, params_list[i])
                else:
                    cursor.execute(sql)#sql语句参数值不带中文值
            except:
                pass
    except Exception, e:
        #print '----------execute_batch_sql----eee==', e
        pass
    finally:
        connection._commit()
        time.sleep(1)
        

#获取新记录，用于第一次连接成功或者重连成功。
def get_new_log(dev_comm, dev_obj, d_server):
    try:
        ret = dev_comm.get_transaction(newlog=True)
#        print '---ret=',ret['result']
    except Exception, e:
        print_exc()
        printf("%s *****reconnect****get_transaction error: %s"%(dev_obj.alias.encode("gb18030"), e), True)
    try:
#        print 'again'
        process_event_log(dev_obj, ret, cursor=None, d_server=d_server)
    except Exception, e:
        print_exc()
        printf("reconnect %s after check_and_down_log e: %s"%(dev_obj.alias.encode("gb18030"), e), True)

#Cardno,Pin,Verified,DoorID,EventType,InOutState,Time_second  记录
#time, Pin, cardno, doorID, even_type, reserved, verified   事件
def process_comm_task(devs, comm_param, cursor, d_server):#dev指DevComm的实例，而非Device的实例--comment by darcy
    from mysite.iclock.models import Transaction
    try:
        ret = 0
        devcomm = devs.comm
        #printf("________process_comm_task comm_param=%s pid=%d"%(comm_param, os.getpid()))
        if (comm_param.startswith(G_DEVICE_CONNECT)):
            #write_log("________process_comm_task before connect pid=%d"%(os.getpid()))
            qret = devcomm.connect()
            #write_log("________process_comm_task after connect pid=%d"%(os.getpid()))
            return {"ret": qret["result"], "retdata": qret["data"]}

        elif (comm_param.startswith(G_DEVICE_DISCONNECT)):
            #write_log("________process_comm_task before disconnect pid=%d"%(os.getpid()))
            return devcomm.disconnect()
            #write_log("________process_comm_task after disconnect pid=%d"%(os.getpid()))

        elif (comm_param.startswith(G_DEVICE_UPDATE_DATA)):
            strs = comm_param.split(" ",3)
            table = strs[2]
            if len(table) > 0:
                data = comm_param[comm_param.find(table)+len(table)+1:]
                data = re.sub(ur'\\', '\r', data)
                #write_log("________process_comm_task before update_data pid=%d"%(os.getpid()))
                qret = devcomm.update_data(table.strip(),data.strip(),"")
                #write_log("________process_comm_task after update_data pid=%d"%(os.getpid()))
            else:
                pass
                #print "command error"
            return {"ret":qret["result"], "retdata":qret["data"]}

        elif (comm_param.startswith(G_DEVICE_QUERY_DATA)):
            if comm_param.find("transaction") > 0:#下载全部刷卡事件
                from mysite.iaccess.models import AccRTMonitor
                #write_log("________process_comm_task before get_transaction pid=%d"%(os.getpid()))
                if comm_param.find("NewRecord")>0:
                    qret = devcomm.get_transaction(True)
                else:
                    qret = devcomm.get_transaction(False)
                #write_log("________process_comm_task after get_transaction pid=%d"%(os.getpid()))
                #write_log("24. user down all transaction rec=%d"%qret['result'])
                return process_event_log(devs.devobj, qret, cursor, d_server)
            else:
                str = ""
                strs = comm_param.split(" ",4)
                table = strs[2]
                field_names = strs[3]

                if len(table) > 0 :
                    filter = comm_param[comm_param.find(field_names)+len(field_names)+1:]
                    #write_log("________process_comm_task before query_data pid=%d"%(os.getpid()))
                    qret = devcomm.query_data(table.strip(),field_names.strip(),filter.strip(), "")
                    #write_log("________process_comm_task after query_data pid=%d"%(os.getpid()))
                else:
                    pass
                
                if comm_param.find("user") > 0:#下载user表内容并与数据库中数据做比较
                    from process_comm_data import process_user_info
                    return process_user_info(qret)
                elif comm_param.find("templatev10") > 0:#下载templatev10表内容并与数据库中数据做比较
                    from process_comm_data import process_template_info
                    return process_template_info(qret)
                else:
                    return {"ret": qret["result"],"retdata": qret["data"]}

        elif(comm_param.startswith(G_DEVICE_DELETE_DATA)):
            strs = comm_param.split(" ", 3)
            table = strs[2]
            if len(table) > 0:
                #write_log("________process_comm_task before delete_data pid=%d"%(os.getpid()))
                qret = devcomm.delete_data(table,comm_param[comm_param.find(table)+len(table)+1:],)
                #write_log("________process_comm_task after delete_data pid=%d"%(os.getpid()))
            else:
                pass
                #print "command error"
            return {"ret": qret["result"],"retdata": qret["data"]}

        elif(comm_param.startswith(G_DEVICE_GET_DATA)):
            return
        elif(comm_param.startswith(G_DATA_COUNT)):
            strs = comm_param.split(" ",3)
            table = strs[2]
            qret=devcomm.Get_Data_Count(table)
            return {"ret":qret["result"],"retdata":qret["data"]}
        elif(comm_param.startswith(G_DEVICE_SET_DATA)):
            try:
                comm_param = comm_param.strip()
                strs = comm_param.split(" ", 5)
                door = int(strs[2])
                index = int(strs[3])
                state = int(strs[4])
                #write_log("________process_comm_task before controldevice pid=%d"%(os.getpid()))
                qret = devcomm.controldevice(door, index, state)
                #write_log("________process_comm_task after controldevice pid=%d"%(os.getpid()))
                return {"ret":qret["result"],"retdata":qret["data"]}
            except:
                print_exc()
                printf("-------process_comm_task G_DEVICE_SET_DATA error return devs.devobj=%s"%devs.devobj, True)
                return

        elif(comm_param.startswith(G_DEVICE_CONTROL_NO)):#
            try:
                comm_param = comm_param.strip()
                strs = comm_param.split(" ", 5)
                door = int(strs[2])#门编号
                state = int(strs[3])#启用（1）或禁用（0）
                #write_log("________process_comm_task before control_normal_open pid=%d"%(os.getpid()))
                qret = devcomm.control_normal_open(door, state)#控制常开
                #write_log("________process_comm_task after control_normal_open pid=%d"%(os.getpid()))
                #print '---qret=',qret,'-----',door,'---',state
                return {"ret": qret["result"], "retdata": qret["data"]}
            except:
                print_exc()
                printf("-------process_comm_task G_DEVICE_CONTROL_NO error return devs.devobj=%s"%devs.devobj, True)
                return

        elif(comm_param.startswith(G_DEVICE_CANCEL_ALARM)):
            try:
                #write_log("________process_comm_task before cancel_alarm pid=%d"%(os.getpid()))
                qret = devcomm.cancel_alarm()#取消报警
                #write_log("________process_comm_task after cancel_alarm pid=%d"%(os.getpid()))
                return {"ret": qret["result"], "retdata": qret["data"]}
            except:
                print_exc()
                printf("-------process_comm_task G_DEVICE_CANCEL_ALARM error return devs.devobj=%s"%devs.devobj, True)
                return

        elif(comm_param.startswith(G_DEVICE_GET_OPTION)):
            strs = comm_param.split(" ", 2)
            opt = strs[2]
            if len(opt) > 0:
                optitem = re.sub(ur'\t', ',', opt)
                #write_log("________process_comm_task before get_options pid=%d"%(os.getpid()))
                qret = devcomm.get_options(optitem.strip())
                #write_log("________process_comm_task after get_options pid=%d"%(os.getpid()))
            return {"ret":qret["result"],"retdata":qret["data"]}

        elif(comm_param.startswith(G_DEVICE_SET_OPTION)):
            strs = comm_param.split(" ",3)
            opt = strs[2]
            if len(opt) > 0:
                optitem = re.sub(ur'\t', ',', opt)
                #write_log("________process_comm_task before set_options pid=%d"%(os.getpid()))
                qret = devcomm.set_options(optitem.strip())
                #write_log("________process_comm_task after set_options pid=%d"%(os.getpid()))
            return {"ret": qret["result"], "retdata": qret["data"]}
        else:
            return {"ret": 0, "retdata": "unknown command"}
    except:
        print_exc()


class DeviceMonitor(object):
    def __init__(self):
        self.id = 0
        self.comm_tmp = ""
        self.new_cln = ""
        self.devobj = None
        self.comm = None
        self.try_failed_time = 0#尝试获取实时记录失败的次数
        self.try_connect_count = 0#尝试连接次数 每分钟一次 try_connect_count即分钟数
        self.try_connect_delay = 0#上次尝试连接时间？
        self.no_command_count = 0   #累计无命令的次数，如果达到 TRY_USE_DISK_FILE_CMD_COUNT,则去实际检查磁盘一次

#命令处理
def process_general_cmd(dev, d_server, q_server, acmd=None, cursor=None, push_on=None):
    #print '-----!!!!!!process_general_cmd'
    if not cursor:
        cursor = connection.cursor()
    cmd_ret = False
    cnt = int(d_server.get_from_dict(dev.cnk) or 0)
    #write_log('process cmd----cnt=%s'%cnt)
    #write_log('process cmd----222acmd=%s dev=%s'%(acmd, dev.devobj.alias.encode("gb18030")))
    if not acmd and cnt == 0:
        #write_log('process cmd----3333--cnd<0 return dev=%s cnt=%s'%(dev.devobj.alias.encode("gb18030"),cnt))
        dev.no_command_count += 1
        if dev.no_command_count < TRY_USE_DISK_FILE_CMD_COUNT:
            return
        else:
            dev.no_command_count = 0
            pass    #继续往下走，实际检查磁盘文件
    #acmd = None
    try:
        #acmd=d_server.getrpop(dev.cln)  #防意外掉电，命令丢失, 先取出执行，成功再删除
        #print '-----process_general_cmd len=',d_server.llen_file(dev.new_cln)
        #if len > 0:#dict中有再到文件缓存中取
        if not acmd:
            acmd = q_server.getrpop_from_file(dev.new_cln)#防意外掉电，命令丢失, 先取出执行，成功再删除
        #printf("---new command list= %s"%acmd, True)
        #print '-!!!!!!!!!--acmd=',acmd
        if (type(acmd) == type('str')) and (acmd.startswith(G_QUEUE_ERROR)):#文件队列错误
            cmd_ret = True
            #write_log("---new command list not None QUEUE_ERROR dev=%s"%dev)
            #acmd = None
            try:
                d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': G_QUEUE_ERROR, 'CmdReturn': -1100})#tmp
                print "add queue error"
            except:
                print_exc()
        #print '-------process_general_cmd  '
    except Exception, e:
        #print '--------process_general_cmd error'
        printf("process_general_cmd error=%s"%e, True)
        print_exc()

    try:
        if acmd and type(acmd)==type('str'):
            acmd = pickle.loads(acmd)
    except:
        printf("---pickle loads acmd error dev=%s"%dev, True)
        acmd = None

    if acmd is not None:
        #write_log("acmd is not None dev=%s"%dev)
        try:
            from mysite.iclock.models.model_device import MAX_COMMAND_TIMEOUT_SECOND
            try:
                cmdline = str(acmd.CmdContent)
            except:
                cmdline = str(acmd.CmdContent.encode('gbk'))

            is_immed = False #记录是否是紧急命令
            if acmd.CmdImmediately:#紧急命令 判断时间
                is_immed = True
                #write_log("immediately commands dev=%s"%dev)
                now_t = datetime.datetime.now()
                if (now_t - acmd.CmdCommitTime).seconds > MAX_COMMAND_TIMEOUT_SECOND:
                    #q_server.rpop_from_file(dev.new_cln)#已判断过dict，直接从文件缓存中pop
                    #write_log('--- delcmd1--in process_general_cmd function')
                    #delete_tempcmd(dev, d_server, acmd)#超时的命令，从字典缓存中删除
                    return False
            #print "general====", cmdline,"==="
        except Exception, e:
            printf("check cmd error = %s" % e, True)
            print_exc()
        #print '---cmdline !=None   =',cmdline!=None
        if cmdline != None:
            try:
                cmd_ret = True
                ret = {"ret": -1005}
                #print '---before acmd.CmdContent=',acmd.CmdContent
                try:
                    #write_log('------before process_comm_task dev=%s'%dev)
                    d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': acmd.CmdContent, 'CmdReturn': 0})#命令未处理前先显示正常
#                    print '=cmdline-------cmdline=',cmdline
                    ret = process_comm_task(dev, cmdline, cursor, d_server)
                    #print cmdline,'*****************ret=====',ret
                    #write_log('------after process_comm_task dev=%s  ret=%s'%(dev, ret))
                except Exception, e:
                    printf("%s *********process_comm_task error =%s"%(dev.devobj.alias.encode("gb18030"), e), True)
                    print_exc()
                #printf("8.%s -- process_general_cmd cmd=%s, ret=%d"%(dev.devobj.alias.encode("gb18030"), cmdline, ret["ret"]))
                #ret["ret"] = -18
                if ret["ret"] >= 0: #执行成功, 写入数据库
                    #write_log("cmds excute succeed --before rpop_from_file")
                    if not is_immed:#非紧急命令时
                        q_server.rpop_from_file(dev.new_cln)#命令执行成功后从文件缓存中清除
                        cmdCount = int(q_server.llen_file(dev.new_cln))
                        if cmdCount<0:    #读出的条数不对，重新再读一次
                            cmdCount = int(q_server.llen_file(dev.new_cln))
                        d_server.set_to_dict(dev.cnk, "%d"%(cmdCount))
                    #write_log("cmds excute succeed --after rpop_from_file")
                    acmd.CmdReturn = ret["ret"]
                    acmd.CmdReturnContent = ret["retdata"]
                    acmd.CmdTransTime = datetime.datetime.now()
                    acmd.save()
                    checkdevice_and_savecache(d_server, dev.devobj, cursor)
                    dev.try_failed_time =0
                else:
                    #write_log("cmds excute failed --before rpop_from_file")
                    if acmd.CmdImmediately == 1:    #立即执行的命令，只执行一次，包括失败
                        #q_server.rpop_from_file(dev.new_cln)
                        printf('--- delcmd3--in process_general_cmd function', True)
                        #delete_tempcmd(dev, d_server, acmd)
                        acmd.CmdReturn = ret["ret"]
                        acmd.CmdReturnContent = ret["retdata"]
                        acmd.CmdTransTime = datetime.datetime.now()
                        acmd.save()

                    #write_log("cmds excute failed --after rpop_from_file")
                    if ret["ret"] == -18:
                        printf("----ret=-18,delete all new commands--dev=%s"%dev.devobj.alias.encode("gb18030"), True)
                        #q_server.deletemore_file(dev.new_cln)    #存贮空间不足
                        d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': acmd.CmdContent, 'CmdReturn': -18})
                        return -18
                    
                    
                    #acmd.CmdReturn=ret["ret"]
                    cmd_ret = False
                    #如果命令处理失败，设备监控需要显示原因。
                    d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': acmd.CmdContent, 'CmdReturn': ret["ret"]})
                    time.sleep(3)#避免设备监控一闪而过
                    
                    #多次失败后要自动断开，之后会自动重新连接并下数据
                    if ret["ret"] == -1 or ret["ret"] == -2:    #仅在发送失败和超时情况断开，其他情况不处理
                        dev.try_failed_time += 1
                        if(dev.try_failed_time > MAX_TRY_COMM_TIME):#尝试获取实时记录五次后，仍然失败，将设备状态改为离线
                            try:
                                #write_log('---try_failed_time > 5--')
                                dev.comm.disconnect()
                                dev.try_connect_delay = time.mktime(datetime.datetime.now().timetuple())
                                set_door_connect(dev.devobj, 0, d_server)#将设备状态改为离线 实时监控显示门断开
                                dev.try_failed_time = 0
                                d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})#
                            except:
                                print_exc()
                    
                #print '---after acmd.CmdContent=',acmd.CmdContent
            except Exception, e:
                printf("process_comm_task failed.....dev=%s,e=%s"%(dev.devobj.alias.encode("gb18030"), e), True)
                print_exc()
                cmd_ret=False
    #print '-------process_general_cmd  cmd_ret=',cmd_ret
    #write_log('-------process_general_cmd  cmd_ret=%s dev=%s'%(cmd_ret, dev))
    return cmd_ret

#devs_dict为进程中的设备信息dict，与Manager管理的dict不同
def add_devs_dict(devs_dict, devobj, d_server):
    try:
        devs_dict[devobj.id] = DeviceMonitor()
        devs_dict[devobj.id].id = devobj.id
        devs_dict[devobj.id].sn = devobj.sn
        devs_dict[devobj.id].new_cln = devobj.new_command_list_name()
        devs_dict[devobj.id].comm_tmp = devobj.command_temp_list_name()#TMP
        devs_dict[devobj.id].cnk = devobj.command_count_key()#命令统计
        devs_dict[devobj.id].devobj = devobj
        devs_dict[devobj.id].comm = TDevComm(devobj.getcomminfo())
        devs_dict[devobj.id].try_connect_count = 0
        devs_dict[devobj.id].enabled = devobj.enabled#是否启用
        devs_dict[devobj.id].comminfo = devobj.getdevinfo()#设备通讯信息------设备信息&通讯信息
        if devs_dict[devobj.id].enabled:
            devs_dict[devobj.id].comm.connect()
            if devs_dict[devobj.id].comm.hcommpro > 0:
                devs_dict[devobj.id].try_connect_delay = time.mktime(datetime.datetime.now().timetuple())
                set_door_connect(devs_dict[devobj.id].devobj, 1, d_server)#在线
                if devs_dict[devobj.id].devobj.sync_time:
                    devs_dict[devobj.id].devobj.set_time(False)
                try:
                    get_new_log(devs_dict[devobj.id].comm, devs_dict[devobj.id].devobj, d_server)#第一次连接成功后首先获取新记录，设备多时可能导致初始化时间较长。-darcy20111207                
                except:
                    pass
                    #print_exc()
            else:
                set_door_connect(devs_dict[devobj.id].devobj, 0, d_server)#离线
                devs_dict[devobj.id].try_connect_delay=0
        else:#禁用的设备不connect
            set_door_connect(devs_dict[devobj.id].devobj, 0, d_server)#离线
            devs_dict[devobj.id].try_connect_delay=0
            devs_dict[devobj.id].comm.hcommpro = -1002

    except Exception, e:
        printf("15. add_devs_dict id=%d error =%s"%(devobj.id, e))


def check_and_down_log(dev, d_server, cursor, down_log_time):    #下载新记录
    from mysite.iaccess.models import AccRTMonitor
    try:
        #cfg = AppOption.objects.filter(optname='download_time')
        #download_time = cfg and int(cfg[0].value) or 0
        now_hour = datetime.datetime.now().hour
        num = smart_str(down_log_time).split(',')
        #print '---------num==', num
        if str(now_hour) not in num:
            return
    
        last_time = d_server.get_from_dict("DOWN_LOG_TIME_%s"%dev.id)
        if last_time == None:
            d_server.set_to_dict("DOWN_LOG_TIME_%s"%dev.id, str(now_hour))
        elif str(last_time) == str(now_hour):
            return
        d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DOWN_NEWLOG", 'CmdReturn': 1000})#正在执行下载新记录
    except Exception, e:
        printf("22-1. %s check_and_down_log e: %s"%(dev.devobj.alias.encode("gb18030"), e), True)
        print_exc()

    #下载记录前先删除之前的日志
    try:
        delete_log()
    except Exception, e:
        write_log("22-1-add. check_and_down_log delete_log e: %s"%e)

    #write_log("22-2. %s check_and_down_log "%dev.devobj.alias.encode("gb18030"))
    try:
        #write_log("22-2. before check_and_down_log")
        ret = dev.comm.get_transaction(newlog=True)
        d_server.set_to_dict("DOWN_LOG_TIME_%s"%dev.id, str(now_hour))
        #write_log("22-2. after check_and_down_log")
    except Exception, e:
        printf("%s *********get_transaction error: %s"%(dev.devobj.alias.encode("gb18030"), e), True)
    #write_log("23-1. %s ---check_and_down_log rec=%d"%(dev.devobj.alias.encode("gb18030"), ret['result']))
    try:
        process_event_log(dev.devobj, ret, cursor, d_server);
    except Exception, e:
        printf("23-2. %s after check_and_down_log e: %s"%(dev.devobj.alias.encode("gb18030"), e), True)
    #write_log("23-3. %s check_and_down_log return: %d"%(dev.devobj.alias.encode("gb18030"), ret['result']))
    return ret['result']


def check_server_stop(procename, pid, devs, d_server):
    #检测到服务停止进程退出
    try:
        ret = False
        proce_server_key = "%s_SERVER"%procename
        #print '---proce_server_key=',proce_server_key
        proce_stop = d_server.get_from_dict(proce_server_key)
        #print '---proce_stop=',proce_stop
        if proce_stop == "STOP":
            d_server.lpop_from_dict(proce_server_key)
            #d_server.delete(proce_server_key)
            #d_server.deletemore_dict("CENTER_HEART_*")
            printf("%s servers return "%procename, True)
            for devsn in devs:
                dev = devs[devsn]
                try:
                    d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})
                except:
                    print_exc()
            ret = True
    except Exception, e:
        print_exc()
        printf("stop server error=%s"%e)
    return ret

#添加设备时让后台进程暂停，以释放串口。否则可能无法添加485设备---darcy20110215
def wait_com_pause(d_server, com_port, timeout):     #COM_1_CHANNELS    PROCESS_WAIT_PAUSE
    channel_key = "COM_%d_CHANNELS"%com_port   #COM_1_CHANNELS
    #print '---channel_key=',channel_key
    com_key = "COM_%d_PID"%com_port
    #print '---com_key=',com_key
    com_pid = d_server.get_from_dict(com_key)
    #print '---com_key=',com_key,'  com_pid=',com_pid
    if com_pid is None:     #串口不存在
        return True
    #print '---PROCESS_WAIT_PAUSE=',PROCESS_WAIT_PAUSE
    d_server.set_to_dict(channel_key, "%d"%PROCESS_WAIT_PAUSE)#写入字典后进程获取该值并处理1
    for i in range(0, timeout, 1):
        #print '-----i=',i
        com_status = d_server.get_from_dict(channel_key)
        #print '---channel_key com_status=',com_status
        if com_status is None:
            #print '----com_status is None'
            time.sleep(1)
            #print '----continue'
            continue
        #print '----after com_status=',com_status
        try:
            ret = int(com_status)
        except:
            ret = 0
        #print '----ret=',ret
        if int(ret) > PROCESS_WAIT_PAUSE:#如果ret =2 说明停止成功，返回True
            #print '---wait_com_pause----return True'
            channel_timeout_key = "COM_%d_CHANNELS_TIMEOUT" % com_port
            d_server.delete_dict(channel_timeout_key)#通知后台进程进程（线程）不再需要等超时
            return True
        time.sleep(1)
    return False

#添加设备时让后台进程暂停，以释放串口。否则可能无法添加485设备---darcy20110215
#停止以太网线程
def wait_thread_pause(d_server, thread, timeout):     #COM_1_CHANNELS    PROCESS_WAIT_PAUSE
    channel_key = "DEVICE_%d_CHANNELS" % thread   #THREAD_DEVICE_1
    #print '---thread_key=',thread_key

    #print '---PROCESS_WAIT_PAUSE=',PROCESS_WAIT_PAUSE
    d_server.set_to_dict(channel_key, "%d"%THREAD_WAIT_PAUSE)#写入字典后进程获取该值并处理1
    for i in range(0, timeout):
        #print '-----i=',i
        thread_status = d_server.get_from_dict(channel_key)#后台停止成功后会将该值改为2
        #print '---channel_key com_status=',com_status
        if thread_status is None:
            #print '----com_status is None'
            time.sleep(1)
            #print '----continue'
            continue
        #print '----after com_status=',com_status
        try:
            ret = int(thread_status)
        except:
            ret = 0
        #print '----ret=',ret
        if int(ret) > THREAD_WAIT_PAUSE:#如果ret =2 说明停止成功，返回True PROCESS_WAIT_PAUSE=1
            #print '---wait_com_pause----return True'
            channel_timeout_key = "DEVICE_%d_CHANNELS_TIMEOUT" % thread
            d_server.delete_dict(channel_timeout_key)#通知后台进程进程（线程）不再需要等超时
            return True
        time.sleep(1)
    return False


#删除暂停通道，后台进程继续---darcy20110215主要用于485，停止的是线程，但实际上每个线程都会停止。防止串口占用问题
def set_comm_run(d_server, com_port):
    #print '---in_set_comm_run'
    channel_key = "COM_%d_CHANNELS" % com_port   #COM_1_CHANNELS
    channel_timeout_key = "COM_%d_CHANNELS_TIMEOUT" % com_port
    d_server.delete_dict(channel_key)
    d_server.delete_dict(channel_timeout_key)

#用户以太网设备升级时停止某个线程
def set_thread_run(d_server, thread):
    #print '---in_set_comm_run'
    thread_key = "DEVICE_%d_CHANNELS" % thread   #THREAD_DEVICE_1
    thread_timeout_key = "DEVICE_%d_CHANNELS_TIMEOUT" % thread
    d_server.delete_dict(thread_key)
    d_server.delete_dict(thread_timeout_key)

#实时任务处理函数，用于进程调用
def net_task_process(devobjs, devcount, procename=""):
    from mysite.iclock.models.model_device import Device, COMMU_MODE_PULL_RS485
    from mysite.iaccess.view import check_acpanel_args
    #raw_input("net_task_process any key to start server".center(50, "-"))
    d_server = start_dict_server()
    q_server = queqe_server()
    tt = d_server.get_from_dict("CENTER_RUNING")    #主服务ID

    pid = os.getpid()#子进程pid
    q_server.set_to_file("PROCESS_%s_PID"%procename, str(pid))#防止python进程意外退出（退出时强制杀python进程）

    d_server.rpush_to_dict(CENTER_PROCE_LIST, "%s"%procename)#
    devs_dict = {}
    path = "%s/_fqueue/"%settings.APP_HOME
    for devobj in devobjs:
        try:
            #print '----devobj=',devobj
            add_devs_dict(devs_dict, devobj, d_server)#devs_dict返回当前进程初始化时进程中的全部设备信息-darcy20110227
            #print '-----devs_dict=',devs_dict
            #devs_dict_all =  d_server.get_from_dict("DEVS_ALL")
            #if devs_dict_all:
            #    for key in devs_dict:
            #        if not devs_dict_all.haskey(key):
            #            devs_dict_all.setdefault(key, devs_dict[key])
            #            d_server.set_to_dict("DEVS_ALL", devs_dict_all)
            #else:
            #    d_server.set_to_dict("DEVS_ALL", devs_dict)
            d_server.delete_dict(devs_dict[devobj.id].comm_tmp)#清除原有设备通讯状态
            #write_log("commstatus 1 CONNECT--CmdReturn=%d"%devs_dict[devobj.id].comm.hcommpro)
            d_server.set_to_dict(devs_dict[devobj.id].comm_tmp, {'SN': devobj, 'CmdContent': "CONNECT", 'CmdReturn': devs_dict[devobj.id].comm.hcommpro})#TMP下载新命令
            d_server.set_to_dict(ACCDEVICE_DISABLED%devobj.id, (not devobj.enabled))#初始化字典中的设备状态
        except Exception, e:
            printf("add_devs_dict %d error=%s"%(devobj.id, e), True)
            #print "add_devs_dict %d error"%devobj.id
        if check_server_stop(procename, pid, devs_dict, d_server):  #启动时检测停止服务
            return 0
    printf("%s :current process: %d"%(procename, os.getpid()))
    #print '---before while(1) of ',procename
    #print '---before while(1) of ',devs_dict
    
    cfg_delay = dict4ini.DictIni(os.getcwd()+"/appconfig.ini",values={"iaccess":{"realtime_delay":1000.0}})        
    realtime_delay = cfg_delay.iaccess.realtime_delay/1000.0
    
    cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini",values={"iaccess":{"down_newlog":0, "realtime_forever":0}})        
    realtime_forever = int(cfg.iaccess.realtime_forever)
    down_log_time = cfg.iaccess.down_newlog
    global g_cursor
    while(1):
        #服务停止进程退出
        cursor = g_cursor
        change_iaccess_argument = d_server.get_from_dict("CHANGE_IACCESS_ARGUMENT")
        if change_iaccess_argument:
            cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini",values={"iaccess":{"down_newlog":0, "realtime_forever":0}})
            realtime_forever = int(cfg.iaccess.realtime_forever)
            down_log_time = cfg.iaccess.down_newlog
            d_server.set_to_dict("CHANGE_IACCESS_ARGUMENT",0)
        #print '--------------11111-----down_log_time===', down_log_time
        try:
            #write_log("!!!!!* child process while(1) process: %s, %s" % (procename, datetime.datetime.now()))
            #print '------@@@@@@@@--while(1)   procename=',procename, '---pid=',os.getpid()
            proce_server_key = "%s_SERVER"%procename #Net0_SERVER
            proce_stop = d_server.get_from_dict(proce_server_key)
            if proce_stop == "STOP":#检测到服务已经停止，显示设备断开
                try:
                    d_server.delete_dict(proce_server_key)
                    #d_server.deletemore_dict("CENTER_HEART_*")
                    printf("%s servers return "%procename, True)
                    #print "%s servers return "%procename
                    for devsn in devs_dict:
                        dev = devs_dict[devsn]
                        try:
                            d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})
                        except:
                            print_exc()
                    d_server.close()
                    q_server.connection.disconnect()
                except Exception, e:
                    print_exc()
                    printf("stop server error=%s"%e, True)
                return 0

            pid_t = time.mktime(datetime.datetime.now().timetuple())
            d_server.set_to_dict(CENTER_PROCE_HEART%procename, str(pid_t))
            #主服务ID不一致退出(同时启动多个服务时)
            if tt != d_server.get_from_dict("CENTER_RUNING"):
                #print '----------servers id error return'
                try:
                    printf("%s servers id error return "%procename, True)
                    for devsn in devs_dict:
                        dev = devs_dict[devsn]
                        try:
                            d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})
                        except:
                            print_exc()
                    d_server.close()
                    q_server.connection.disconnect()
                except Exception, e:
                    print_exc()
                    printf("stop server error=%s"%e, True)
                return 0

            #线程与缓存中的设备同步

            #获取到当前进程中的“目标”设备列表，设备添加、编辑、删除后，该list将实时变化，并通知进程作出改变-darcy20110227
            process_realtime_devinfo = d_server.get_from_dict(procename) or []
            process_current_devinfo = []  #当前线程中的实际设备列表
            del_dev = {}#运行时需要删除的设备。（如设备已从数据库中删除）---darcy20110227
            #print '-----devs=',devs
            thread_dev = {}#当前设备线程
            for devsn in devs_dict:
                try:
                    thread_dev = devs_dict[devsn].comminfo#获取线程中的设备的基本信息，如通讯参数等。
                    #print thread_dev,'--------thread_dev'
                    #print '-##########--thread_dev=',thread_dev
                    process_current_devinfo.append(thread_dev)
                except Exception, e:
                    printf("process_current_devinfo append device error=%s"%e, True)
                #删除设备
                #print '---thread_dev=',thread_dev
                #print '--proce_thread_devset=',proce_thread_devset
                if not thread_dev:#except的情况
                    continue
                
                if thread_dev not in process_realtime_devinfo:#当前进程中的该设备可能已经被用户从数据库中删除-darcy20110227
                    try:
                        #print '---delete thread_dev=',thread_dev
                        devs_dict[devsn].comm.disconnect()
                        #devs.__delitem__(devsn)
                        del_dev[devsn] = devs_dict[devsn]
                        #print "1. %s delete device %d"%(procename, thread_dev["id"])
                        #write_log("1. %s delete device %d"%(procename, thread_dev["id"]))
                    except Exception, e:
                        print_exc()
                        printf("16. %s delete device error id=%d error=%s"%(procename, thread_dev["id"], e), True)
            try:
                for del_d in del_dev:   #解决运行期
                    #print '---del_d =',del_d
                    del devs_dict[del_d]
            except:
                printf("procecache delete device error", True)

            #print procename, "process_current_devinfo=" , process_current_devinfo
            #增加设备(用户新增了设备，需要再进程中添加)
            for process_dev in process_realtime_devinfo:
                if process_dev not in process_current_devinfo:
                    #print '-----add dev   process_dev=',process_dev
                    try:
                        cdev = Device.objects.filter(id=process_dev["id"])
                        if cdev:
                            #print '---before devs_dict=',devs_dict
                            add_devs_dict(devs_dict, cdev[0], d_server)#获取到了新的devs_dict
                            #print '---after devs_dict=',devs_dict
                            d_server.delete_dict(devs_dict[cdev[0].id].comm_tmp)
                            #write_log("commstatus 2 CONNECT--CmdReturn=%d"%devs_dict[cdev[0].id].comm.hcommpro)
                            d_server.set_to_dict(devs_dict[cdev[0].id].comm_tmp, {'SN': cdev[0], 'CmdContent': "CONNECT", 'CmdReturn': devs_dict[cdev[0].id].comm.hcommpro})
                            d_server.set_to_dict(ACCDEVICE_DISABLED%cdev[0].id, (not cdev[0].enabled))#初始化字典中的设备状态(是否被禁用)
                            #write_log("22. %s add device %s"%(procename, process_dev["id"]))
                    except Exception, e:
                        print_exc()
                        printf("add device error e=" % e, True)
                        continue

            #write_log("3. %s process_current_devinfo=%s, process_realtime_devinfo=%s"%(procename, process_current_devinfo, process_realtime_devinfo))
            #进程级---串口进程中设备为空时自动中止进程
            if procename.find("COM") >= 0:
                try:
                    if devs_dict.__len__() == 0:
                        #用于新增485设备, 线程暂停
                        channel_key = "%s_CHANNELS" % procename   #COM_1_CHANNELS
                        channel_timeout_key = "%s_CHANNELS_TIMEOUT" % procename

                        channel_now = time.mktime(datetime.datetime.now().timetuple())#当前时间
                        channel_timeout = d_server.get_from_dict(channel_timeout_key)
                        #write_log('----channel_timeout=%s' % channel_timeout)
                        if channel_timeout: #如果需要等待超时的话（前端收到后台停止线程的通知后会将该超时标记设置为空）
                            try:
                                channel_timeout = int(channel_timeout)
                            except:
                                channel_timeout = 0
                            if channel_now - int(channel_timeout) > PAUSE_TIMEOUT:#暂停超时，取消暂停
                                #print '-------pause_timeout=',PAUSE_TIMEOUT
                                d_server.delete_dict(channel_key)
                                d_server.delete_dict(channel_timeout_key)
                        channel_status = d_server.get_from_dict(channel_key)
                        #write_log('----original--channel_status=%s' % channel_status)
                        if channel_status is None:
                            channel_status = 0
                        try:
                            channel_status = int(channel_status)
                        except:
                            channel_status = 0
                        #write_log('-----channel_status=%s' % channel_status)
                        if channel_status == PROCESS_WAIT_PAUSE:#检测到让串口进程暂停的请求
                            #write_log('----@@@@@after stop hcommpro=%s' % dev.comm.hcommpro)
                            d_server.set_to_dict(channel_key, "%d"%PROCESS_PAUSE)#进程暂停，写入2
                            d_server.set_to_dict(channel_timeout_key, "%d"%(int(channel_now)))
                        if channel_status > PROCESS_NORMAL:#0
                            #print '------com process continue'
                            #write_log('------com process continue')
                            #进程暂停
                            d_server.set_to_dict(CENTER_PROCE_HEART%procename, time.mktime(datetime.datetime.now().timetuple()))#COM进程暂停时，修改子进程心跳
                            continue#485后台线程暂停，不再向下执行-darcy20110215
                except Exception, e:
                    printf("proccache device empty return error=%s"%e, True)
                    pass
            #print "----------before process general cmd    devs_dict=%s"%devs_dict
            ##write_log("----------before process general cmd    devs=%s"%devs_dict)
            #设备通讯
            for devsn in devs_dict:
                #服务停止进程退出
                proce_server_key = "%s_SERVER"%procename
                proce_stop = d_server.get_from_dict(proce_server_key)
                if proce_stop == "STOP":
                    try:
                        d_server.lpop_from_dict(proce_server_key)
                        #d_server.delete(proce_server_key, file=True, dict=True)
                        #d_server.deletemore_dict("CENTER_HEART_*")
                        printf("%s servers return "%procename, True)
                        for devsn in devs_dict:
                            dev = devs_dict[devsn]
                            try:
                                d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})
                            except:
                                print_exc()
                        d_server.close()
                        q_server.connection.disconnect()
                    except Exception, e:
                        print_exc()
                        printf("stop server error=%s"%e, True)
                    return 0

                #主服务ID不一致退出
                if tt != d_server.get_from_dict("CENTER_RUNING"):
                    try:
                        printf("%s servers id error return "%procename, True)
                        for devsn in devs_dict:
                            dev = devs_dict[devsn]
                            try:
                                d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})#设备监控显示设备断开
                            except:
                                print_exc()
                        d_server.close()
                        q_server.connection.disconnect()
                    except Exception, e:
                        print_exc()
                        printf("stop server error=%s"%e, True)
                    return 0
                dev = devs_dict[devsn]
                cnt  = d_server.get_from_dict(dev.cnk)
                if cnt is None:
                    cmdcount = q_server.llen_file(dev.devobj.new_command_list_name())
                    d_server.set_to_dict(dev.cnk, "%d"%(int(cmdcount)))
                try:
                    #用于新增485设备（COM进程中已有其他设备的情况） 以及升级固件, 线程暂停---线程级
                    if procename.find("COM") >= 0:
                        channel_key = "%s_CHANNELS"%procename   #COM_1_CHANNELS
                        channel_timeout_key = "%s_CHANNELS_TIMEOUT"%procename
                    else:#Net 以太网
                        channel_key = "DEVICE_%s_CHANNELS" % dev.id   #COM_1_CHANNELS
                        channel_timeout_key = "DEVICE_%d_CHANNELS_TIMEOUT" % dev.id

                    #pause_current_channel(d_server, channel_key, channel_timeout_key, dev)#暂停当前进程或线程 dev可能为None，当新增485设备时
                    channel_now = time.mktime(datetime.datetime.now().timetuple())#当前时间
                    channel_timeout = d_server.get_from_dict(channel_timeout_key)
                    if channel_timeout: #如果需要等待超时的话（前端收到后台停止线程的通知后会将该超时标记设置为空）
                        try:
                            channel_timeout = int(channel_timeout)
                        except:
                            channel_timeout = 0
                        if channel_now - int(channel_timeout) > PAUSE_TIMEOUT:#暂停超时，取消暂停
                            #write_log('-------pause_timeout=%s' % PAUSE_TIMEOUT)
                            d_server.delete_dict(channel_key)
                            d_server.delete_dict(channel_timeout_key)
                    channel_status = d_server.get_from_dict(channel_key)
                    #write_log('----original--channel_status=%s' % channel_status)
                    if channel_status is None:
                        channel_status = 0
                    try:
                        channel_status = int(channel_status)
                    except:
                        channel_status = 0
                    #print '-----channel_status=',channel_status
                    if channel_status == PROCESS_WAIT_PAUSE:#检测到让串口进程暂停的请求
                        if dev.comm.hcommpro > 0:
                            dev.comm.disconnect()
                        #write_log('----@@@@@after stop hcommpro=%s' % dev.comm.hcommpro)
                        d_server.set_to_dict(channel_key, "%d"%PROCESS_PAUSE)#进程暂停，写入2
                        d_server.set_to_dict(channel_timeout_key, "%d"%(int(channel_now)))
                    if int(channel_status) > PROCESS_NORMAL:#0
                        #write_log('-----com or net process continue')
                        #线程暂停
                        d_server.set_to_dict(CENTER_PROCE_HEART%procename, time.mktime(datetime.datetime.now().timetuple()))#当前设备线程暂停时，修改子进程心跳
                        d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "CONNECT", 'CmdReturn': -1004})    #设备线程暂停，实际上也已经断开连接
                        #write_log("---------com or net continue")
                        set_door_connect(dev.devobj, 0, d_server)#将设备状态改为离线 实时监控显示门断开
                        continue#485后台线程暂停，不再向下执行-darcy20110215
                except Exception, e:
                    print_exc()
                    printf("thread pause error=%s"%e, True)
                    
                #设备被禁用  dev.devobj.id
                try:
                    try:
                        check_disabled = d_server.get_from_dict(ACCDEVICE_DISABLED%dev.devobj.id)#禁用该设备。获取到False或者返回None均为未禁用（启用）:
                    except Exception, e:
                        printf("check_disabled error=%s"%e, True)
                    #print '----check_disabled=',check_disabled
                    if check_disabled:#为True
                        try:
                            dev.enabled = 0
                            d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISABLED", 'CmdReturn': -1002})    #设备监控显示设备被禁用
                        except Exception, e:
                            printf("check_disabled 2 error=%s"%e, True)
                        if dev.comm.hcommpro > 0:
                            dev.comm.disconnect()
                        try:
                            set_door_connect(dev.devobj, 0, d_server)#实时监控显示灰色（离线）
                        except Exception, e:
                            printf("check_disabled 3 error=%s"%e, True)
                        now_t = time.mktime(datetime.datetime.now().timetuple())
                        #print '----now_t=',now_t
                        #print '--dev.try_connect_delay=',dev.try_connect_delay
                        if now_t - dev.try_connect_delay < MAX_INTERVAL_CONNTECT_TIME:
                            dev.try_connect_delay = now_t - MAX_INTERVAL_CONNTECT_TIME #60s     #启用设备立即重连
                        #print '----dev.try_connect_delay=',dev.try_connect_delay
                        try:
                            d_server.set_to_dict(CENTER_PROCE_HEART%procename, time.mktime(datetime.datetime.now().timetuple()))#当前线程暂停时，修改子进程心跳
                        except Exception, e:
                            printf("check_disabled 4 error=%s"%e, True)
                        continue
                    else:
                        dev.enabled = 1#代表前端设备是启用的
                    
                except Exception, e:
                    print_exc()
                    printf("4. check_dev_enabled error=%s"%e, True)

                #print "5. %s -- dev.comm.hcommpro=%d"%(dev.devobj.alias.encode("gb18030"), dev.comm.hcommpro)
                #write_log("5. %s -- dev.comm.hcommpro=%d"%(dev.devobj.alias.encode("gb18030"), dev.comm.hcommpro))
                #print '----dev.enabled=',dev.enabled,'---dev.devobj.alias=',dev.devobj.alias
                #已禁用的设备不会执行此处（上面已经continue）

                try:
                    immed_cmd_dict = d_server.get_from_dict("TEMP_CMD")#获取紧急命令
                    ret = False
                    #write_log('in-----------1 %s %s'%(immed_cmd_dict,procename))
                    #紧急命令由process_general_cmd直接处理
                    if immed_cmd_dict:
                        for dev_id in devs_dict.keys():#当当前设备在当前进程中时才处理该设备的命令
                            #print dev_id,'=========ininin========',immed_cmd_dict.keys()
                            if dev_id in immed_cmd_dict.keys():
                                #for dev_id in immed_cmd_dict.keys():
                                #    print devs_dict,'-------devs_dict',dev_id
                                #    dev = devs_dict[dev_id]
                                dev_obj = devs_dict[dev_id]#当前需要处理紧急命令的设备，与下面获取事件记录的设备不同
                                #write_log('--darcy111---dev=%s, temp_cmd=%s'%(dev_obj.devobj, d_server.get_from_dict("TEMP_CMD")))
                                devcmd_list = immed_cmd_dict.get(dev_obj.id)
                                timeout = 0
                                while True:
                                    temp_cmd_lock = d_server.get_from_dict("TEMP_CMD_LOCK")
                                    if temp_cmd_lock:
                                        #write_log('-----lock--dev=%s temp_cmd_lock=%s timeout=%s'%(dev_obj.devobj, temp_cmd_lock, timeout))
                                        timeout += 1
                                        if timeout > 300:
                                            break#超时后不放入缓存
                                        time.sleep(1)
                                        continue
                                    else:
                                        d_server.set_to_dict("TEMP_CMD_LOCK", 1)
                                        delete_tempcmd(dev_obj, devcmd_list, d_server)#如果设备当前连接是断开的，则删除此设备的临时命令，继续执行其他命令
                                        d_server.set_to_dict("TEMP_CMD_LOCK", 0)
                                        break
                                if dev_obj.comm.hcommpro <= 0 or not dev_obj.enabled:#设备断线或者被禁用
                                    #write_log('-------offline or disabled------delete cmd----------')
                                    #print '--!!!!!------in--',dev_obj.comm.hcommpro
                                    temp_hcommpro = dev_obj.comm.hcommpro
                                    if not dev_obj.enabled:#不会到此
                                        temp_hcommpro = -1002#设备被禁用-darcy201101012
                                    elif temp_hcommpro == 0:#避免调用设备的disconnect事连接句柄变为0产生的操作假成功--darcy20111010
                                        temp_hcommpro = -1001
                                        
                                    #print '---temp_hcommpro=',temp_hcommpro
                                    if devcmd_list:
                                        #immed_cmd_dict.pop(dev_obj.id)
                                        for acmd in devcmd_list:
                                            #print '---dev_obj.comm.hcommpro=',dev_obj.comm.hcommpro
                                            acmd.CmdReturn = temp_hcommpro
                                            acmd.CmdTransTime = datetime.datetime.now()
                                            acmd.save()
                                
                                else:#当前设备时连接的，可用的
                                    if devcmd_list:
                                        for acmd in devcmd_list:
                                            #write_log('in-------------2  %s'%devcmd_list)
                                            #if dev.comm.hcommpro > 0:
                                            #write_log('in----------3 %s %s %s'%(acmd.CmdContent, dev_obj, procename))
                                            #以下代码直接处理紧急命令
                                            ret = process_general_cmd(dev_obj, d_server, q_server, acmd, cursor=cursor, push_on=False)#先处理紧急命令 此处是否需要修改子进程心跳???
                                                #if ret == None:
                                                #    break
                                            #else:
                                            #    delete_tempcmd(dev, d_server, acmd)#如果设备当前连接是断开的，则删除此命令，继续执行其他命令
                                        #temp_cmd_dict.pop(dev.id)
                                        #d_server.set_to_dict("TEMP_CMD", temp_cmd_dict)
                                    #    d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "REAL_LOG", 'CmdReturn':1})
                                continue
                        #else:
                            #prinft()
                except Exception, e:
                    printf("-!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-process temp_cmd e=%s"%e, True)
                    pass
                    

                if dev.comm.hcommpro <= 0:#已启用的设备 如果当前未连接
                    now_t=time.mktime(datetime.datetime.now().timetuple())
                    if now_t - dev.try_connect_delay > MAX_INTERVAL_CONNTECT_TIME:  #未连接设备, 60秒重连一次  启用设备立即重连
                        try:
                            dev.try_connect_count += 1
                            dev.try_connect_delay = time.mktime(datetime.datetime.now().timetuple())
                            #write_log("5.1 %s -- try connect device"%dev.devobj.alias.encode("gb18030"))
                            dev.comm.disconnect()
                            #write_log("5.2 %s -- disconnect device succeed"%dev.devobj.alias.encode("gb18030"))
                            dev.comm.connect()
                            #write_log("5.3 %s --  after connect device "%dev.devobj.alias.encode("gb18030"))
                            #write_log("commstatus 3 CONNECT--CmdReturn=%d  dev=%s"%(dev.comm.hcommpro, dev.devobj.alias.encode("gb18030")))
                            d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "CONNECT", 'CmdReturn': dev.comm.hcommpro})
                        except Exception, e:
                            printf("5.0 %s -- try connect device error=%s"%(dev.devobj.alias.encode("gb18030"), e))
                            print_exc()
                        #print '----re connect the device dev=',dev.devobj
                        #write_log('----re connect the device dev=%s'%dev.devobj)
                        if dev.comm.hcommpro > 0: #重试连接成功
                            #print '---- success re connect the device dev=',dev.devobj
                            try:
                                dev.try_connect_count = 0
                                set_door_connect(dev.devobj, 1, d_server)
                                if dev.devobj.sync_time:
                                    dev.devobj.set_time(False)
                                check_acpanel_args(dev, dev.comm)#关于门禁控制器设备参数的回调函数
                                get_new_log(dev.comm, dev.devobj, d_server)#重试连接成功后重新获取新记录。-darcy20111207
                            except:
                                print_exc()
                        else:#重试连接失败，需要修改设备监控通讯状态以及实时监控状态
                            #print '---- failed to re connect the device dev=',dev.devobj
                            #write_log('---- failed to re connect the device dev=%s'%dev.devobj)
                            try:
                                set_door_connect(dev.devobj, 0, d_server)
                                if dev.try_connect_count > MAX_CONNECT_COUNT:   #禁用设备  一个月
                                    printf("6. %s -- set dev disabled"%(dev.devobj.alias.encode("gb18030")), True)
                                    dev.try_connect_count = 0
                                    dev.devobj.set_dev_disabled(d_server)
                            except:
                                print_exc()
                    continue
                #write_log("----------before process general cmd process=%s pid=%d"%(procename, os.getpid()))
                #print "----------before process general cmd"
                try:
                    #else:
                    ret = process_general_cmd(dev, d_server, q_server, acmd=None, cursor=cursor, push_on=False)#处理非紧急命令
                    d_server.set_to_dict(CENTER_PROCE_HEART%procename, time.mktime(datetime.datetime.now().timetuple()))#每条命令执行完，均修改子进程心跳时间
                    #print '---ret=',ret
                    #write_log("---------process general cmd ret=%s process=%s"%(ret, procename))
                    if ret == True:#下载命令
                        #print '---continue'
                        #write_log('---continue')
                        continue#命令下载完前不会进入到下面的获取实时事件以及门状态。
                    elif dev.comm.hcommpro <= 0:
                        continue    #设备因失败已断开连接
                        
                    #没有命令需要下载时，继续
                    elif ret == -18:
                        continue
                except Exception, e:
                    #print '---process_general_cmd error'
                    print_exc()
                    printf("process_general_cmd error=%s"%e, True)
                #write_log("----------after process general cmd process=%s"%procename)
                #print "----------after process general cmd"

                currunt_time = datetime.datetime.now()
                rtmonitor_stamp = d_server.get_from_dict("RTMONITOR_STAMP")  
                try:                  
                    if realtime_forever or (rtmonitor_stamp and (currunt_time-rtmonitor_stamp).seconds <= 60):#前断需要后台开启监控时，后台开启。当最后一次请求距离当前时间超过60s后，自动终止后台监控，其它继续。
                        rtlog = dev.comm.get_rtlog()
                        #print dev.devobj.alias," rtlog result:",rtlog["data"]#实时事件
                        ##write_log("7.%s -- rtlog result:%s"%(dev.devobj.alias.encode("gb18030"), rtlog["data"]))#固件最原始数据
                        if(is_comm_io_error(rtlog["result"])):
                            printf("7. %s -- get rtlog return failed result=%d"%(dev.devobj.alias.encode("gb18030"), rtlog["result"]), True)
                            printf("commstatus 4 REAL_LOG--CmdReturn=%d"%rtlog["result"], True)
                            d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "REAL_LOG", 'CmdReturn': rtlog["result"]})
                            dev.try_failed_time += 1
                            if(dev.try_failed_time > MAX_TRY_COMM_TIME):#尝试获取实时记录五次后，仍然失败，将设备状态改为离线
                                try:
                                    #write_log('---try_failed_time > 5--')
                                    dev.comm.disconnect()
                                    dev.try_connect_delay = time.mktime(datetime.datetime.now().timetuple())
                                    set_door_connect(dev.devobj, 0, d_server)#将设备状态改为离线 实时监控显示门断开
                                    dev.try_failed_time = 0
                                    set_door_connect(dev.devobj, 0, d_server)#将设备状态改为离线 实时监控显示门断开
                                    d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "DISCONNECT", 'CmdReturn': -1001})#
                                except:
                                    print_exc()
                            continue
                        else:
                            try:
                                d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "REAL_LOG", 'CmdReturn': 1})
                                checkdevice_and_savecache(d_server, dev.devobj, cursor)
                            except:
                                print_exc()
                            if rtlog["result"] > 0:#获取到实时事件记录
                                appendrtlog(d_server, cursor, dev.devobj, rtlog["data"])
                            dev.try_failed_time = 0
                    else:
                        d_server.set_to_dict(dev.comm_tmp, {'SN': dev.devobj, 'CmdContent': "", 'CmdReturn':0})
                except Exception, e:
                        print_exc()
                        printf("control realtime monitoring error=%s"%e, True)  

                try:
                    #print '--------------222222-----down_log_time===', down_log_time
                    ret_log = check_and_down_log(dev, d_server, cursor, down_log_time)    #检查定时下载记录
                    if ret_log > 0:
                        printf("check_and_down_log end .... ret_log=%d"%ret_log, True)
                        #print "check_and_down_log end .... ret_log=%d"%ret_log
                        pid_t = time.mktime(datetime.datetime.now().timetuple())
                        #print '---pid_t2=',pid_t
                        #process_heart[procename] = pid_t
                        #g_devcenter.process_heart[procename] = pid_t
                        d_server.set_to_dict(CENTER_PROCE_HEART%procename, str(pid_t))
                    else:
                        #write_log("no new log end or not the time process=%s"%procename)
                        pass
                except Exception, e:
                    print_exc()
                    printf("check_and_down_log error=%s"%e, True)

            time.sleep(realtime_delay)

            #print '------@@@@@@@@-end-while(1)   procename=',procename
            #write_log('------@@@@@@@@-end-while(1) procename=%s'%procename)
        except Exception, e:
            #write_log("try exception e=%s"%e)
            print_exc()
            pass
    d_server.close()
    q_server.connection.disconnect()
    #write_log("process return ")
    return 0

class TThreadMonitor(object):
    def __init__(self,func,args):
        self.func = func
        self.args = args

    def __call__(self):
        apply(self.func, self.args)

class TDevDataCommCenter(object):
    def __init__(self, d_server, q_server):
        cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini",values={"iaccess":{"max_thread":5}})
        self.max_thread = cfg.iaccess.max_thread
        self.d_server = d_server
        self.q_server = q_server
        self.pool = Pool(processes = self.max_thread)#进程池
        self.comport_set={}
        self.NetDev=Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).filter(comm_type=COMMU_MODE_PULL_TCPIP)
        self.ComDev=Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).filter(comm_type=COMMU_MODE_PULL_RS485)
        ##write_log("self.NetDev=%s"%self.NetDev)
        self.net_dev_set = self.set_thread_dev(self.NetDev)   #将设备平均分配 生成设备列表
        #print '---self.net_dev_set=',self.net_dev_set
        printf("self.net_dev_set=%s"%self.net_dev_set, True)
        self.killRsagent()
        self.pid=os.getpid()
        #print '----self.pid=',self.pid#主进程pid
        printf("CommCenter main pid=%d" % self.pid, True)
        self.q_server.set_to_file(CENTER_MAIN_PID, "%d"%(self.pid))#主进程--darcy
#        print "net_dev_set=", self.net_dev_set
        for i in range(0, self.max_thread):
            devs = self.net_dev_set[i]
            tName = "Net%d" % i
            self.d_server.set_to_dict(CENTER_PROCE_HEART%tName, time.mktime(datetime.datetime.now().timetuple()))#子进程心跳#self.pid
            self.d_server.delete_dict(tName)
            #printf("----class init devs= %s"%devs)
            for dev in devs:
                dev_info = dev.getdevinfo()
                try:
                    #printf("--before rpush_to_dict--")
                    self.d_server.rpush_to_dict(tName, dev_info)#写入缓存时值已list写入，如{"Net0":['abd','23dd'}
                    #printf("--after rpush_to_dict--")
                except:
                    print_exc()
            #printf("------tName=%s %s"%(tName, d_server.get_from_dict(tName)))
            #printf("----class init get_items %s"%d_server.sync_dict.get_dict()._getvalue())
            self.pool.apply_async(net_task_process, [devs, len(devs), tName])#net_task_process进程调用--tcp/ip

        self.comports = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485).values('com_port').distinct()
        for comport in self.comports:
            comdevs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485,com_port=comport['com_port'])
            tName = "COM_%d" % comport["com_port"]
            devs = []
            self.d_server.delete_dict(tName)
            for comdev in comdevs:
                devs.append(comdev)
                comdev_info = comdev.getdevinfo()
                self.d_server.rpush_to_dict(tName, comdev_info)

            p = Process(target=net_task_process, args=(devs, len(devs), tName))#net_task_process进程调用--485
            self.d_server.set_to_dict("%s_PID"%tName, "%d"%(p._parent_pid))
            p.start()
            #t = threading.Thread(target = TThreadMonitor(net_task_process,(devs, len(devs), tName)))

    def killRsagent(self):
        return os.system(run_commend(4))

    def set_thread_dev(self, devset):
        devs=[]
        for i in range(0, self.max_thread):
            devs.append([])#
        for i in range(0, len(devset)):
            devs[i%self.max_thread].append(devset[i])
        return devs

    def refushcomport(self):
        from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, COMMU_MODE_PULL_RS485, COMMU_MODE_PULL_TCPIP
        self.comports = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485).values('com_port').distinct()
        self.NetDev = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).filter(comm_type=COMMU_MODE_PULL_TCPIP)

    #同步前台后台设备
    def delete_device(self, devinfo):
        from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, COMMU_MODE_PULL_RS485, COMMU_MODE_PULL_TCPIP
        if devinfo["comm_type"] == COMMU_MODE_PULL_TCPIP:
            for i in range(0, len(self.net_dev_set)):
                for net_dev in self.net_dev_set[i]:
                    if net_dev.id == devinfo["id"]:
                        self.net_dev_set[i].remove(net_dev)#先删除进程中设备
                        tName="Net%d"%i
                        self.d_server.delete_dict(tName)#字典缓存中中设备
                        for dev in self.net_dev_set[i]:#然后将剩余的设备重新循环添加到字典缓存中
                            self.d_server.rpush_to_dict(tName, dev.getdevinfo())
        elif devinfo["comm_type"] == COMMU_MODE_PULL_RS485:
            comdevs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485,com_port=devinfo["com_port"])
            tName = "COM_%d"%devinfo["com_port"]
            self.d_server.delete_dict(tName)
            for dev in comdevs:
                self.d_server.rpush_to_dict(tName, dev.getdevinfo())
        self.d_server.save()

    def edit_device(self, dev):
        from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, COMMU_MODE_PULL_RS485, COMMU_MODE_PULL_TCPIP
        if dev.comm_type == COMMU_MODE_PULL_TCPIP:
            for i in range(0, len(self.net_dev_set)):
                for net_dev in net_dev_set[i]:
                    if net_dev.id == dev.id:
                        ii = net_dev_set[i].index(net_dev)
                        net_dev_set[i][ii] = dev
                        #修改缓存设备信息
                        tName = "Net%d"%i
                        self.d_server.delete_dict(tName)
                        dev = []
                        for dev0 in self.net_dev_set[i]:
                            try:
                                dev = Devivce.objects.filter(id=dev0.id)
                                self.d_server.rpush_to_dict(tName, dev[0].getdevinfo())
                            except:
                                printf("edit_device error")
        elif dev.comm_type == COMMU_MODE_PULL_RS485:
            comdevs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485,com_port=dev.com_port)
            tName = "COM_%d"%dev.com_port
            devs = []
            self.d_server.delete_dict(tName)
            for comdev in comdevs:
                devs.append(comdev)
                self.d_server.rpush_to_dict(tName, comdev.getdevinfo())
        self.d_server.save()

    def adddevice(self,dev):
        from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, COMMU_MODE_PULL_RS485, COMMU_MODE_PULL_TCPIP
        self.NetDev = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).filter(comm_type=COMMU_MODE_PULL_TCPIP)
        if dev.comm_type == COMMU_MODE_PULL_TCPIP:
            new_dev = True
            for dev_set in self.net_dev_set:
                if dev in dev_set:
                    new_dev = False
            #print '------new_dev=',new_dev
            if new_dev:     #设备不在线程中
                #print '---self.net_dev_set=',self.net_dev_set
                for i in range(0, self.max_thread):
                    if len(self.net_dev_set[i]) <= len(self.NetDev)/self.max_thread:    #分配至后台进程
                        self.net_dev_set[i].append(dev)
                        #print '-----self.net_dev_set=',self.net_dev_set
                        tName="Net%d"%i
                        #print "---before---%s %s"%(tName, d_server.get_from_dict(tName))
                        self.d_server.rpush_to_dict(tName, dev.getdevinfo())
                        #print "---after---%s %s"%(tName, d_server.get_from_dict(tName))
                        break

        elif dev.comm_type == COMMU_MODE_PULL_RS485:
            comdevs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485,com_port=dev.com_port)
            tName = "COM_%d"%dev.com_port
            devs = []
            self.d_server.delete_dict(tName)
            for comdev in comdevs:
                devs.append(comdev)
                self.d_server.rpush_to_dict(tName, comdev.getdevinfo())
            com_list = []
            for v in self.comports:
                com_list.append(v.values()[0])
            if dev.com_port not in com_list:
                #t = threading.Thread(target = TThreadMonitor(net_task_process,(devs, len(devs), tName)))
                self.comports =Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,comm_type=COMMU_MODE_PULL_RS485).values('com_port').distinct()
                p = Process(target=net_task_process, args=(devs, len(devs), tName))
                self.d_server.set_to_dict("%s_PID"%tName, "%d"%(p._parent_pid))
                p.start()
        self.d_server.save()

#某个进程异常，所有进程，然后重启所有进程
def killall_pid(q_server):
    try:
        main_pid = q_server.get_from_file(CENTER_MAIN_PID)
        process_info = os.popen(run_commend(1) % main_pid).read()
        #print '---process_info=',process_info
        if run_commend(3) in process_info.lower():
            os.system(run_commend(2) % main_pid)
        #q_server.get_from_file("PROCESS_%s_PID"%procename, pid)
        #raw_input("Press any key to start server".center(50, "-"))
    except:
        print_exc()

def rundatacommcenter():
    try:
        from mysite.iclock.models.model_device import Device, COMMU_MODE_PULL_RS485
        from process_mails import SendEmail
        
        global g_devcenter
        printf("1.--rundatacenter--sevice pid=%d" % os.getpid(), True)
        #process_heart = manager.dict()#子进程心跳
    #    check_sync_db_cachel()  #同步数据库与缓存数据
        SendEmail().start()
        try:
            delete_log()
        except:
            pass
        q_server = queqe_server()
        d_server = start_dict_server()
        #需要考虑server没启动的情况(比如webservice没启动)
        killall_pid(q_server)#缓存中记录了之前的主进程pid，杀掉
        #print '---current_pid=',os.getpid()

        #服务启动时，清空文件缓存。dict在server没启动时也需要初始化
        try:
            path = "%s/_fqueue/"%settings.APP_HOME
            #raw_input("Press any key to start server".center(50, "-"))
            #print '---start=',d_server.sync_dict.get_items()
            d_server.clear_dict()#初始化共享数据的字典

            tt = "{0:%Y-%m-%d %X}".format(datetime.datetime.now())
            d_server.set_to_dict("CENTER_RUNING", tt)
            #print '-----have cleared all the files'
            g_devcenter = TDevDataCommCenter(d_server, q_server)
        except Exception, e:
            print_exc()

        while True:
            #print '---while true-----'
            #printf("while true get_items %s"%d_server.sync_dict.get_dict()._getvalue(), True)
            #printf("while true devopt %s"%d_server.get_from_dict(DEVOPT), True)
            try:
                #print '--before--get devopt=',d_server.get_from_dict(DEVOPT)
                len = d_server.llen_dict(DEVOPT)
                #print '--len=',len
                if len > 0:#意味着有新增、编辑或者删除操作的（任意一个）
                    try:
                        acmd = d_server.lpop_from_dict(DEVOPT)#从dict中判断有数据,一个个取操作
                    except Exception, e:
                        print_exc()
                        printf('------datacommcenter main process new-edit-del device error=%s'%e, True)
                    #print '----len2 of devopt=',d_server.llen_dict(DEVOPT)
                    #print '----get devopt=',d_server.get_from_dict(DEVOPT)
                    #print '--devopt--acmd=',acmd
                    if acmd is None:
                        continue
                    try:
                        devinfo = pickle.loads(acmd)
                        #print '---devinfo=',devinfo
                    except:
                        devinfo = None
                    if devinfo is not None:
                        try:
                            #print "2. add com device %s operate=%s"%(devinfo["id"], devinfo["operatstate"])
                            #write_log("2. add com device %s operate=%s"%(devinfo["id"], devinfo["operatstate"]))
                            #print '---devinfo["operatstate"]=',devinfo["operatstate"]
                            op_type = int(devinfo["operatstate"])
                            if op_type == OPERAT_ADD:   #新增设备
                                dev = Device.objects.filter(id = devinfo["id"])
                                #write_log('--add dev--')
                                if dev:##设备已在数据库中
                                    #print '---device has in the database'
                                    g_devcenter.adddevice(dev[0])
                                else:
                                    d_server.rpush_to_dict(DEVOPT, devinfo)   #设备还未save进数据库
                                    time.sleep(10)
                            elif op_type == OPERAT_EDIT:  #修改设备时，先删除后增加设备
                                g_devcenter.delete_device(devinfo)
                                dev = Device.objects.filter(id = devinfo["id"])
                                #write_log('--edit dev--')
                                if dev:
                                    g_devcenter.adddevice(dev[0])
                                else:
                                    d_server.rpush_to_dict(DEVOPT, devinfo)   #设备还未save进数据库
                                    time.sleep(10)
                            elif op_type == OPERAT_DEL:
                                #write_log('--del dev--')
                                g_devcenter.delete_device(devinfo)
                        except Exception, e:
                            printf("device opreater error=%s"%e, True)
                    continue
                else:
                    time.sleep(5)
                if d_server.llen_dict("MONITOR_RT") > MAX_RTLOG:#d_server.llen("MONITOR_RT")
                    d_server.set_to_dict("MONITOR_RT_DEL", True)#该值默认F（或者返回None），如果为T,实时监控需要重新取
                    d_server.delete_dict("MONITOR_RT")
                    d_server.delete_dict("ALARM_RT")
                #僵尸进程检测
                pid_set = d_server.get_from_dict(CENTER_PROCE_LIST) or []
                #print '---jiangshi--pid_set=',pid_set
                #write_log("---jiangshi--pid_set=%s" % pid_set)
                for p in pid_set:
                    #write_log("---jiangshi--process=%s" % p)
                    pid_time = d_server.get_from_dict(CENTER_PROCE_HEART%p)
                    #print '----p: %s, pid_time: pid_time : %s' % (p, pid_time)
                    #print "*****main service while true: process: %s, pid_time: %s" % (p, pid_time)
                    #write_log("*****main service while true: process: %s, pid_time: %s" % (p, pid_time))
                    if pid_time:#type:str
                        now_t = time.mktime(datetime.datetime.now().timetuple())
                        #print '-----now_t-float(pid_time)=',now_t - float(pid_time)
                        #printf("*****main service while true: process: %s, now_t: %s, delta: %d" % (p, datetime.datetime.now(), now_t - pid_time), True)

                        if now_t - float(pid_time) > 60*60*2:#     #now_t - float(pid_time)#1小时没心跳, 杀掉所有进程，重新启动
                            printf("PID die**********", True)
                            #print '---PID die--'
                            try:
                                d_server.close()
                                q_server.connection.disconnect()
                                killall_pid(q_server)#杀掉后服务会自动重启
                                #write_log('****kill pid finished')
                                printf("****kill pid finished", True)
                                #time.sleep(60*5)#60*5
                            except:
                                #write_log('-----killall pid error')
                                printf("-----killall pid error", True)
                            break;

            except Exception, e:
                print_exc()
                printf("datacommcenter while True error=%s"%e, True)
                continue
            time.sleep(1)
        d_server.close()
        q_server.connection.disconnect()
    except Exception, e:
        print_exc()
        printf("-----while true error=%s"%e, True)
    
if __name__ == '__main__':
    print 'start at:', ctime()

    rundatacommcenter()
    print 'finish'
