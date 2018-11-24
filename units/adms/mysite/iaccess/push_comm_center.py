#! /usr/bin/env python
#coding=utf-8

#门禁控制器pushsdk通讯处理视图
# 2011.4.27 Darcy
# commit first version

"""该视图只要处理pushsdk协议下的数据通讯的业务逻辑处理"""

import threading
from time import sleep, ctime
from ctypes import *
from mysite.utils import printf, write_log
import os
import dict4ini
from django.utils.encoding import smart_str
m_rtlog_buffer = None#获取实时监控事件时的buffer。默认16K
from traceback import print_exc
from django.db import connection
from mysite.iaccess.models import AccDoor
from mysite.personnel.models.model_emp import format_pin, Employee
from django.core.cache import cache
import datetime

CMD_RETURN_TIMEOUT = 30

EVENT_GAPB_SUCCEED = 222
EVENT_ANTIPASSBACK = 41             #41反潜验证，后台验证
EVENT_ANTIPASSBACK_FAILED = 42      #42反潜验证失败，后台验证
EVENT_GAPB_RESET = 224	        #224反潜验证重置

#from dev_comm_center import set_door_state, strtoint, sync_to_att, obtain_doorobj_from_log, get_door_state #该方式需要抽象出来
from process_comm_data import strtoint, sync_to_att, obtain_doorobj_from_log, strtodatetime, set_doorstr, FmtTTime #该方式需要抽象出来
from process_comm_data import EVENT_LINKCONTROL, CLOSE_AUXOUT, OPEN_AUXOUT,  ALAEM_ID_START, ALAEM_ID_END, DOOR_STATE_ID, INOUT_SEVER, INOUT_SHORT

from rtmonitor import get_door_state

g_monitor_server = None
#处理控制器通过push传输过来的事件记录以及门状态
#原始记录格式为：0：卡号，1：PIN号，2：验证方式，3：门编号，4：事件类型，5：出入状态，6：时间
#记录格式：0：时间， 1：PIN号 ， 2：卡号， 3：门编号， 4：事件类型， 5：出入状态， 6：验证方式  7:门状态  8:报警状态----zhangy
#time, Pin, cardno, doorID, even_type, reserved, verified
def cdata_post_acc_trans_state(device, raw_data, d_server):
#    print '---push comm center raw_data=',raw_data
#    print '----device = ',device, type(device)
    append_rtlog_status_push(device, raw_data, d_server)
    return (1, 1, "")#需要修改调试

def append_rtlog_status_push(devobj, rtlog, d_server):#append_rtlog_push(d_server, devobj, rtlog):#push ----cccc20110726
    from mysite.iaccess.models import AccRTMonitor
    from base.middleware import threadlocals
    from mysite.iaccess.models.accdoor import AccDoor
    try:
        rtlogs = rtlog.split("\t")
        operator = threadlocals.get_current_user()
        cursor = connection.cursor()
        dev_door_list = AccDoor.objects.filter(device=devobj)  #读设备门列表到缓存
        for rtlog in rtlogs:#修改支持一次获取多条事件记录
            #print '---rtlog=',rtlog
#            if not rtlog:#非记录
#                continue
#            str = rtlog.split("\t")#pull为','
            str = rtlog.split(",")  #----cccc
            doorstr=""
            if len(str) < 7:      #不合规范数据
                return 0
            d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%s,%s,1"%(str[7],str[8]))
            print 'door_state---status====',d_server.get_from_dict(devobj.get_doorstate_cache_key())
#            if strtoint(str[4]) == DOOR_STATE_ID:#0时间+1门开关状态+2报警或门开超时+3没用+4（255标明该事件为门状态，否则为事件）+5 没用+6验证方式（200其他）
#                d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%s,%s,1"%(str[1],str[2]))
#                write_log("rtlog ---- %s %s"%(str[1],str[2]))
#                return
##            print '---str=',str
#            if strtoint(str[4]) == EVENT_DOORSENSOROPEN:
#                doorstate = d_server.get_from_dict(devobj.get_doorstate_cache_key())#dict中读取
#    #            print "doorstate=",doorstate
#                if doorstate is None:
#                    doorstate = "0,0,0"
#                doorstr = doorstate.split(",", 3)
#                try:
#                    val = set_doorstr(int(doorstr[0]), 0x02, int(str[3]))
#                except:
#                    val = 0
#                d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%d,%s,1"%(val,doorstr[1]))
#
#            if strtoint(str[4]) == EVENT_DOORSENSORCLOSE:
#                doorstate = d_server.get_from_dict(devobj.get_doorstate_cache_key())
#                #print "doorstate=",doorstate
#                if doorstate is None:
#                    doorstate = "0,0,0"
#                doorstr = doorstate.split(",", 3)
#                try:
#                    val = set_doorstr(int(doorstr[0]), 0x01, int(str[3]))
#                except:
#                    val = 0
#                d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%d,%s,1"%(val,doorstr[1]))
#
#            if (strtoint(str[4]) >= ALAEM_ID_START) and (strtoint(str[4]) < ALAEM_ID_END):
#                doorstate = d_server.get_from_dict(devobj.get_doorstate_cache_key())
#                #print "doorstate=",doorstate
#                if doorstate is None:
#                    doorstate = "0,0,0"
#                doorstr = doorstate.split(",", 3)
#                try:
#                    val = set_doorstr(int(doorstr[1]), int(str[4]), int(str[3]))
#                except:
#                    val = 0
#                d_server.set_to_dict(devobj.get_doorstate_cache_key(), "%s,%d,1"%(doorstr[0], val))

            doorobj = None
            try:
                for obj in dev_door_list:
                    if obj.door_no == int(str[3]): #查找相应的门对像,避免重复查询数据库
                        doorobj = obj
                        break
                doorobj = obtain_doorobj_from_log(str, doorobj)
                if doorobj is not None:
                    str[3] = doorobj and doorobj.id or 0
#                     str[3] = str[3] or 0  #----cccc20110726
                    area_id = doorobj.device.area.id
            except:
                print_exc()
            #print '--!!!!!!!--str=',str
             #if d_server.llen("MONITOR_RT")<MAX_RTLOG:
            #暂不考虑，设备人员不在数据库中的情况。固件已判断，只有验证通过的人才会上来41事件。darcy20110803锦湖轮胎
            try:
                #新记录格式：0：时间， 1：PIN号 ， 2：卡号， 3：门编号， 4：事件类型， 5：出入状态， 6：验证方式  ----cccc
                #time, Pin, cardno, doorID, even_type, reserved, verified
                #push方式给设备发命令 ----chenwj20110726

                if int(str[4]) == EVENT_GAPB_SUCCEED or int(str[4]) == EVENT_GAPB_RESET: #反潜验证开门成功或者初始化反潜规则---222
                    #d_server.set_to_dict("APB_STATE_EMP_"+str[1], str[5])
                    if doorobj:
                        if doorobj.global_apb:
                            d_server.set_to_dict("GLOBAL_APB_AREA_%s_EMP_%s"%(area_id, str[1]), str[5])

                #由于devview中已经做了设备所属区域内是否都在线的判断，所以程序执行至此时，说明区域内所有设备都在线
                if int(str[4]) == EVENT_ANTIPASSBACK: #反潜验证41
                    if doorobj:
                        global_apb_cmd = ""#返回空，表示后台验证失败--darcy20110803锦湖轮胎
                        #查看区域反潜范围内的设备的当前状态（不需要检查当前设备）-darcy20110803锦湖轮胎
                        if not check_apb_device_state(devobj, d_server):
                        #if area_apb_offline:#如果区域反潜上一个状态是离线的，那么整个区域内的所有设备上来的之后的第一条记录都按照固件权限组逻辑判断。
                            #d_server.delete_dict("GLOBAL_APB_AREA_"+area_id)#清空
                            global_apb_cmd = "NA"
                            print '------NA'
                            keys = d_server.get_keys_from_dict()#效率不高。。。
                            #print '-@@@@@@--keys=',keys
                            for key in keys:
                                if key.startswith("GLOBAL_APB_AREA_%s"%area_id):
                                    #print '--------delete the emp key=',key
                                    d_server.delete_dict(key)
                                    #print '--get key=',key,'---',d_server.get_from_dict(key)
                        else:
                            lock_delay = doorobj.lock_delay#获取锁驱动时长
                            print '----GLOBAL_APB_AREA=',"GLOBAL_APB_AREA_%s_EMP_%s"%(area_id, str[1])
                            apb_state = d_server.get_from_dict("GLOBAL_APB_AREA_%s_EMP_%s"%(area_id, str[1]))
                            #print '---apb_state=',apb_state
                            #DEVICE SET %d %d %d %d   #1继电器,门id，1继电器类型为门，时长
                            if apb_state:#缓存中存在此人员
                                if apb_state != str[5]:#出入状态匹配成功，可以开门--darcy20110803锦湖轮胎
                                    #print '-----can open the door'
                                    global_apb_cmd = "DEVICE SET 1 %d 1 %s"%(int(str[3]), lock_delay)
                            elif apb_state is None:#第一次，里面还没有内容，即初始化反潜规则，要求固件发送224事件-darcy20110803
                                #print '--apb_state is None---can open the door'
                                global_apb_cmd = "RESET_GAPB DEVICE SET 1 %d 1 %s"%(int(str[3]), lock_delay)
                            else:
                                pass
                                #print '------cannot open the door'
                        d_server.set_to_dict("GLOBAL_APB_CMD_%s"%devobj.sn, global_apb_cmd + '\n' + rtlog.strip())#生成开门命令

                #else:#其它情况，如：卡未注册
                if doorobj is not None:
                    str[3] = doorobj and doorobj.id or 0
                log = "%s,%s,%s,%s,%s,%s,%s,%d"%(FmtTTime(str[0]).strftime('%Y-%m-%d %H:%M:%S'),str[1],str[3],str[4],str[5], str[6].strip(), str[2], devobj and devobj.id or 0)
                write_log("---log=%s"%log)
                save_event_log(str, cursor, operator, doorobj, devobj)#写入报表
                d_server.rpush_to_dict("MONITOR_RT", log)#{"MONITOR_RT':['log1','log2']}#push实时监控

                if (strtoint(str[4]) >= ALAEM_ID_START) and (strtoint(str[4]) < ALAEM_ID_END):
                    d_server.rpush_to_dict("ALARM_RT", log)

            except Exception, e:
                print '--e2=',e
                print_exc()

        connection.close()
    except Exception, e:
        connection.close()
        print '-----e3=',e
        print_exc()

#查看区域反潜范围内的设备的当前状态（不需要检查当前设备）-darcy20110803锦湖轮胎
def check_apb_device_state(device, d_server):
    #{"PUSH_DEVICE_INFO", {"1234",:{"dev_obj":<>,"push_status":1, "pull_status":0},{"23455":{}}}
    #{"PUSH_DEV_INFO", {"1234",:"dev_obj":<>}, "PUSH_STATE_12345":1,"PULL_STATE_12345":0}
    #先取出要检测的设备。
    devs_sn = device.area.device_set.exclude(sn=device.sn).filter(accdoor__global_apb=1).distinct().values("sn")
    #只要有一个离线就要返回NA.push和pull至少有一个在线（即两个都断线才是断线），就认定为在线，验证时先验证push。-darcy20110803锦湖轮胎
    #由于开门也通过push返回命令，所以pull主要用来判断当前的区域反潜设备状态。
    #print '---devs_sn=',devs_sn
    for dev in devs_sn:
        #print '----sn=',dev["sn"]
        #print '----key2=',"PUSH_STATE_%s"%dev["sn"]
        push_state = d_server.get_from_dict("PUSH_STATE_%s"%dev["sn"])
        #print '---push_state=',push_state
        if push_state <= 0:#大于0 在线 小余等于0不在线
            pull_state = d_server.get_from_dict("PULL_STATE_%s"%dev["sn"])
            #print '---pull_state=',pull_state
            if pull_state <= 0:#确实不在线。
                return False
    return True#含只有一个设备的时候直接返回True（即当前是在线的）

#根据不同的数据库生成相应的----cccc 20110802
def sql_state(pin_str):
    sql = ""
    try:
        if 'oracle' in str(type(connection)).lower():
            sql = "SELECT STATE FROM ACC_MONITOR_LOG WHERE ROWNUM = 1 AND PIN = '%s' AND EVENT_TYPE in (0, 222) ORDER BY TIME DESC"%pin_str
        elif 'mysql' in str(type(connection)).lower():
            sql = "SELECT STATE FROM ACC_MONITOR_LOG WHERE PIN = '%s' AND EVENT_TYPE in (0, 222) ORDER BY TIME DESC LIMIT 1"%pin_str
        elif 'sqlserver_ado' in str(type(connection)).lower():
            sql = "SELECT TOP 1 STATE FROM ACC_MONITOR_LOG WHERE PIN = '%S' AND EVENT_TYPE in (0, 222) ORDER BY TIME DESC"%pin_str
    except:
        print_exc()
        pass
    return sql


#该方法需要提取为push和pull两种模式，实现一个方法兼容两种事件记录的格式
#传入的split_log为原始记录分解之后的。分别为time, Pin, cardno, doorID, even_type, reserved, verified
def save_event_log(split_log, cursor, operator, doorobj, devobj=None):
    from mysite.iclock.models import Device
    print split_log,'&&&&&&&&&&777vvsplit_log'
    dev_id = 0
    dev_name = ""
    door_id = 0
    door_name = ""
    sql = ""
    if devobj:
        try:
            dev_id = devobj.id
            dev_name = devobj.alias
        except:
            print_exc()

    if doorobj:
        try:
            door_id = doorobj.id
            door_name = doorobj.door_name
        except:
            print_exc()
    #记录格式：0：时间， 1：PIN号 ， 2：卡号， 3：门编号， 4：事件类型， 5：出入状态， 6：验证方式  ----cccc
    #time, Pin, cardno, doorID, even_type, reserved, verified

    import time
    #单条事件结构信息 先初始化，后面再根据实际情况更改
    transaction_struct = {}
    transaction_struct['change_operator'] = None
    transaction_struct['change_time'] = None
    transaction_struct['create_operator'] = None             #问题：后台进程无法获取操作用户
    transaction_struct['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    transaction_struct['delete_operator'] = None
    transaction_struct['delete_time'] = None
    transaction_struct['time'] = FmtTTime(split_log[0]).strftime('%Y-%m-%d %H:%M:%S')
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
    transaction_struct['device_sn'] = devobj.sn
    transaction_struct['device_name'] = dev_name#设备是一定有的
    transaction_struct['door_id'] = 0#不能为None，否则None转换成int时会失败
    transaction_struct['door_name'] = None
#    print split_log[4],'---------------'
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

#    if transaction_struct['event_type'] == '0':#只保存时间正常刷卡的事件
    if 'oracle' in str(type(connection)).lower():
#        print 'oracle---------------------'
        #使用直接的SQL插入保存  问题：后台进程无法获取操作用户(create_operator字段)
        sql = "INSERT INTO acc_monitor_log(change_operator,change_time,create_operator,create_time,delete_operator,delete_time,status,time,pin,card_no,device_id \
               ,device_sn,device_name,door_id,door_name,in_address,verified,state,event_type \
               ,trigger_opt,out_address) \
               values(NULL,NULL,'%s',to_date('%s','YYYY-mm-dd HH24-MI-SS'),NULL,NULL,'%s',to_date('%s','YYYY-mm-dd HH24-MI-SS'),'%s',%s,%s,%s,'%s',%s,'%s',%s,%s,%s,%s,%s,%s)" % (
                    transaction_struct['create_operator'],
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
                )
    else:
#        print '-----------------other_sql'
        sql = "INSERT INTO acc_monitor_log(change_operator,change_time,create_operator,create_time \
               ,delete_operator,delete_time,status,time,pin,card_no,device_id \
               ,device_sn,device_name,door_id,door_name,in_address,verified,state,event_type \
               ,trigger_opt,out_address) \
               values(NULL,NULL,'%s','%s',NULL,NULL,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                    transaction_struct['create_operator'],
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
                )
    try:
        cursor.execute(sql)
        connection._commit()
    except:
#        print sql,'-----------------errorsql'
        print_exc()
        pass


#push反潜 命令生成
#def open_or_colse_comm(str):
#    ret = ''
#    APB_STATE_EMP_ = d_server.get_from_dict("APB_STATE_EMP_"+str[1])
#    #DEVICE SET %d %d %d %d   #1继电器,门id，1继电器类型为门，时长
#    if APB_STATE_EMP_:#缓存中存在此人员
#        if APB_STATE_EMP_ != str[5]:
#            print '11111111'
#            ret = "1 %d 1 15"%int(str[3])
#            d_server.set_to_dict("APB_STATE_EMP_"+str[1],str[5])
#        else:
#            print '55555555'
#    else:#不存在在报表中查询----cccc
#        sql ="SELECT STATE FROM ACC_MONITOR_LOG WHERE ROWNUM = 1 AND PIN = '%s'  ORDER BY TIME DESC"%pin_str
#        cursor.execute(sql)
#        state = cursor.fetchall()
#        if state:
#            if int(str[5]) not in state[0]:
#                print '2222222'
#                ret = "1 %d 1 15"%int(str[3])
#                d_server.set_to_dict("APB_STATE_EMP_"+str[1],str[5])
#            else:
#                print '333333333'
#                d_server.set_to_dict("APB_STATE_EMP_"+str[1],str[5])
#                str['24']
#        else:
#            print '44444444'
#            ret = "1 %d 1 15"%int(str[3])
#            d_server.set_to_dict("APB_STATE_EMP_"+str[1],str[5])
#        return ret



#    cursor = conn.cursor()
#    okc = 0;
#    errorLines = [] #发生保存错误的记录
#    cacheLines = [] #本次提交的行
#    errorLogs = []  #解析出错、不正确数据的行
#    sqls = []
#    commitLineCount = 700 #达到700行就提交一次
#    if settings.DATABASE_ENGINE == "ado_mssql": commitLineCount = 50
#    alog = None
#    for line in raw_data.splitlines():
#        if line:
#            eMsg = ""
#            try:
#                log = line_to_log(device, line)
#            except Exception, e:  #行数据解析错误
#                eMsg = u"%s" % e.message
#                print eMsg
#                log = None
#            print log
#            if log:
#                sqls.append(log)
#                cacheLines.append(line) #先记住还没有提交数据，commit不成功的话可以知道哪些数据没有提交成功
#                if len(cacheLines) >= commitLineCount: #达到一定的行就提交一次
#                    try:
#                        commit_log(cursor, sqls, conn)
#                        okc += len(cacheLines)
#                        if not alog:
#                            alog = cacheLines[0]
#                    except IntegrityError:
#                        errorLines += cacheLines
#                    except Exception, e:
#                        print_exc()
#                        print "try again"
#
#                        conn.close()
#                        cursor = conn.cursor()
#                        errorLines += cacheLines
#                    cacheLines = []
#                    sqls = []
#            else:
#                errorLogs.append("%s\t--%s" % (line, eMsg and eMsg or "Invalid Data"))
#    if cacheLines: #有还没有提交的数据
#        try:
#            commit_log(cursor, sqls, conn)
#            okc += len(cacheLines)
#            if not alog:
#                alog = cacheLines[0]
#        except IntegrityError:
#            errorLines += cacheLines
#        except Exception, e:
#            print_exc()
#            print "try again"
#            conn.close()
#            cursor = conn.cursor()
#            errorLines += cacheLines
#
#    if errorLines: #重新保存上面提交失败的数据，每条记录提交一次，最小化失败记录数
#        cacheLines = errorLines
#        errorLines = []
#        for line in cacheLines:
#            if line not in errorLogs:
#                try:
#                    log = line_to_log(device, line, False)
#                    commit_log(cursor, log, conn)
#                    if not alog: alog = cacheLines[0]
#                    okc += 1
#                except Exception, e:
#                    estr = u"%s" % e
#                    if "database is locked" in estr:
#                        try:
#                            conn.close()
#                            cursor = conn.cursor()
#                            log = line_to_log(device, line, False)
#                            commit_log(cursor, log, conn)
#                            if not alog: alog = cacheLines[0]
#                            okc += 1
#                            estr = ""
#                        except Exception, ee:
#                            estr = u"%s" % ee
#                    elif ("UNIQUE KEY" in estr) or ("are not unique" in estr) or (
#                        "Duplicate entry" in estr):
#                        estr = "Duplicated"
#                    errorLines.append("%s\t--%s" % (line, estr))
#    errorLines += errorLogs
#    dlogObj = ""
#    try:
#        if okc == 1:
#            dlogObj = alog
#        elif okc > 1:
#            dlogObj = alog + ", ..."
#    except:pass
#    if errorLines:
#        #ErrNo:22 (invalid argument)的错误处理。
#        #出错的非重复记录，重新进入到后台处理队列
#        elinedata=[]
#        for el in errorLines:
#            if "Duplicated" not in el:
#                elinedata.append(el.split("\t--")[0])
#        if elinedata:
#            from mysite.iclock.models.model_cmmdata import gen_device_cmmdata
#            obj=gen_device_cmmdata(device,old_head+"\n"+"\n".join(elinedata),"error")
#
#        tmpFile("transaction_%s_%s.txt" % (device.sn, datetime.datetime.now().strftime("%Y%m%d%H%M%S")), "\n".join(errorLines))
#    print okc, len(raw_data.splitlines())
#    return (okc, len(errorLines), dlogObj)


# state（0无门磁，1门关,2门开） alarm（1报警 2门开超时）connect(0不在线，1在线)
def door_state_monitor_push(dev_list, d_server):#dev_list为QuerySet---devids需为list
    #service_enable = check_service_commcenter(d_server)
    cdatas = []
    for dev in dev_list:
        key = dev.get_door_state_cache_key()
        doorstate = d_server.get_from_dict(key)
#        print '----doorstate=',doorstate
        #print 'doorstate=',doorstate
        if not dev.enabled:#设备被禁用
            vdoor = 0
            valarm = 0
            vcon = 0
            enabled = 0
        elif doorstate:#and service_enable:#服务没有启动（含手动），前端门显示不在线
            val = doorstate.split(",", 3)
            enabled = 1
            try:
                vdoor = int(val[0])#设备中所有门的开关状态
            except:
                #print_exc()
                vdoor = 0
            try:
                valarm = int(val[1])#设备中所有门的 报警 门开超时
            except:
                #print_exc()
                valarm = 0
            try:
                vcon = int(val[2])#是否在线
            except:
                #print_exc()
                vcon = 0
        else:
            vdoor = 0
            valarm = 0
            vcon = 0
            enabled = 1

        door = dev.accdoor_set.all()
        for d in door:
            state = get_door_state(vdoor, d.door_no)
            alarm = get_door_state(valarm, d.door_no)
            cdata = {
                'id': int(d.id),
                'state': int(state),
                'alarm': int(alarm),
                'connect': int(vcon),
                'enabled': enabled,
            }
            cdatas.append(cdata)
    cc={
        'data':cdatas,
    }
    #print cc
    #rtdata=simplejson.dumps(cc)
    return cc

def acc_cdata(request, response):
    from redis_self.server import start_dict_server
    from mysite.iclock.devview import cdata_get_options
#    print '====innini=--acc_cdata'
    resp = ''
    try:
        global g_monitor_server
        if not g_monitor_server:
           #print '--rtlog--first time=',g_monitor_server
           g_monitor_server = start_dict_server()


        #检测设备是否存在，存在的话，检测设备的在线和离线状态。
        device = check_acc_device(request, g_monitor_server, True)

        print '----device=',device
        if device is None: 
            return "UNKNOWN DEVICE"
#        print '---request.method=',request.method
        g_monitor_server.set_to_dict(device.get_last_activity(), datetime.datetime.now())
        if request.REQUEST.has_key('action'):
            resp += "OK\n"
        elif request.method == 'GET':
            #if request.REQUEST.has_key('PIN'):
            #    resp+=cdata_get_pin(request, device)
            # else:
            print '----request---get'
            alg_ver = "1.0"
            if request.REQUEST.has_key('pushver'):
              alg_ver = request.REQUEST.get('pushver')    #2010-8-25  device字段alg_ver用来区分新老固件  >=2.0为新固件，默认为旧固件
            device.alg_ver = alg_ver
            device.save()
            resp += cdata_get_options(device)
            
        elif request.method == 'POST':#处理设备上传上来的数据，如实时监控记录等。-darcy0803锦湖轮胎
#            print '---cdata post'
            try:
                resp += acc_cdata_post(request, device, g_monitor_server)
#                print '---!!!!!---resp=',resp
            except Exception, e:
                resp = u"ERROR: %s" % e
                print e
                #errorLog(request)
        else:
            resp += "UNKNOWN DATA\n"
            resp += "POST from: " + device.sn + "\n"
    except:
        resp += "error\n"
        from traceback import print_exc
        print_exc()
    print resp, '=========resp'
    return resp
    
#根据设备http请求找对应的设备对象--门禁控制器
def check_acc_device(request, d_server, allow_create=False):
    from mysite.iclock.models import Device
    from base.cached_model import STATUS_PAUSED, STATUS_STOP
    from mysite.iaccess.dev_comm_center  import DEVOPT
    import time
    import datetime
    from mysite.iclock.models.model_device import DEVICE_ACCESS_CONTROL_PANEL
    from redis_self.server import start_dict_server
    from mysite.iclock.cache_cmds import check_and_init_cmds_cache
    #print '---request=',request
    device = None
    global g_monitor_server
    if not g_monitor_server:
       #print '--rtlog--first time=',g_monitor_server
       g_monitor_server = start_dict_server()
    if not d_server:
        d_server = g_monitor_server
    try:
        sn = request.GET["SN"]
        #print '---sn=',sn
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
        
    dev_info = d_server.get_from_dict("PUSH_DEV_INFO")#暂没有加设备的同步.....darcy20110803锦湖轮胎
    len = d_server.llen_dict(DEVOPT)
    #print '--len=',len
   # print '-----!!dev_info=',dev_info
    if not dev_info or len > 0:#设备信息初始化   len > 0意味着有新增、编辑或者删除操作的（任意一个）
        #{"PUSH_DEVICE_INFO", {"1234",:{"dev_obj":<>,"push_status":1, "pull_status":0},{"23455":{}}}
        devs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL)
        dev_dict = {}
        for dev in devs:
            dev_dict[dev.sn] = dev
        d_server.set_to_dict("PUSH_DEV_INFO", dev_dict)
        dev_info = dev_dict
    #print '----dev_info=',dev_info
    #print sn, dev_info.keys()
    if sn in dev_info.keys():#设备存在
        device = dev_info[sn]
        #print '--sn==',sn
        if device.status in (STATUS_STOP, STATUS_PAUSED):
            return None
        #初始化设备的在线状态（此处仅更新push的在线状态）--darcy20110803锦湖轮胎
        #push_state = d_server.get_from_dict("PUSH_STATE_" + sn)
        #if push_state <= 0:#等于0的话为在线--darcy20110803锦湖轮胎
        d_server.set_to_dict("PUSH_STATE_%s"%sn, time.mktime(datetime.datetime.now().timetuple()))
        #print '-key=',"PUSH_STATE_%s"%sn
        #print '--get_push_state=',d_server.get_from_dict("PUSH_STATE_%s"%sn), "PUSH_STATE_%s"%sn
            
    #device.last_activity = datetime.datetime.now()?????
    check_and_init_cmds_cache(device)
    return device

def acc_cdata_post(request, device, d_server=None):
    from mysite import settings
    from mysite.iclock.devview import STAMPS
    raw_Data = request.raw_post_data
    #print "raw_Data:%s"%raw_Data
    #print request.META.items()
    if not raw_Data:
        raw_Data = request.META['raw_post_data']
    #print settings.ENCRYPT
    #logger.error(raw_Data)
    if settings.ENCRYPT:
        import lzo
        rawData = lzo.bufferDecrypt(raw_Data, device.sn)
    else:
        rawData = raw_Data
    
    #print '---raw_Data=',raw_Data
    stamp=None
    for s in STAMPS:
        stamp=request.REQUEST.get(s, None)
        if not (stamp is None):
            stamp_name=STAMPS[s]
            break
#    print stamp_name,'======stamp_name'
    if stamp is None:
        return "UNKNOWN"

    msg=None
    if stamp_name == 'log_stamp':
        c, ec, msg = cdata_post_acc_trans_state(device, rawData, d_server)
    else:
        c = 0

    #push下发开关门命令---darcy20110803       
    try:
        c = d_server.pop_from_dict("GLOBAL_APB_CMD_%s"%device.sn) or ""
        
    except Exception, e:
        from traceback import print_exc
        print_exc()
        printf('------send push e=%d'%e, True)
    if c.startswith("NA"):
        return c
    else:
        return "OK %s"%c

#一体机接受设备请求命令，返回命令给设备
def acd_getreq(request, resp, device):
    from mysite.iclock.models.model_device import MAX_COMMAND_TIMEOUT_SECOND
    from mysite.iclock.cache_cmds import get_request_cmds, check_pre_request, get_pre_request_cmds, TEMP_CMD_KEY
    from redis_self.server import start_dict_server
    print '=======acd_getreq=='
    global g_monitor_server
    if not g_monitor_server:
       #print '--rtlog--first time=',g_monitor_server
       g_monitor_server = start_dict_server()
    g_monitor_server.set_to_dict(device.get_last_activity(), datetime.datetime.now())
    try:
        sn = request.GET["SN"]
    except:
        sn = request.raw_post_data.split("SN=")[1].split("&")[0]
#    temp_cmd_list = cache.get(TEMP_CMD_KEY%device.pk)
#    print temp_cmd_list,'======temp_cmd_list==key=',TEMP_CMD_KEY%device.pk
#    if temp_cmd_list:
#        temp_cmd_obj = temp_cmd_list.pop()
#        cache.set(TEMP_CMD_KEY%device.pk, temp_cmd_list)
#        return process_next_cmd(request, resp, device, temp_cmd_obj, sn, False)#处理紧急命令，不需要更新cache中的命令index，紧急命令单独存储、优先处理
    pre_cmd_obj = cache.get("PROCESSING_CMD_OBJ_%s"%sn)
#    timeout = CMD_RETURN_TIMEOUT
    if pre_cmd_obj and not pre_cmd_obj.CmdImmediately:
        check_ret = check_pre_request(device)#确认上次下发命令，机器是否成功接收到
        if not check_ret:
            devcmd = get_pre_request_cmds(device) #返回上一次下发的命令
            print devcmd,'----precmdcmdmdm'
            return process_next_cmd(request, resp, device, devcmd, sn, False)
        else:
            devcmd = get_request_cmds(device)
            print devcmd, '========nextdevcmdddd'
            return process_next_cmd(request, resp, device, devcmd, sn, True)
    else:
        devcmd = get_request_cmds(device)
        print '---------devcmd=',devcmd
        ret = process_next_cmd(request, resp, device, devcmd, sn, True)
        return ret

#一体机给设备返回命令
def process_next_cmd(request, resp, device, devcmd, sn, flag_new=False):
    from mysite.iclock.devview import update_cached_cmd
    from mysite.iclock.cache_cmds import update_start_end_index
    from mysite.iclock.cmdconvert import std_cmd_convert
    if devcmd:
        obj_cmd = cache.get(devcmd)
        if not obj_cmd:
            obj_cmd = devcmd #当为紧急命令时，传人的为命令对象
        obj_cmd.CmdTransTime = datetime.datetime.now()
        update_cached_cmd(obj_cmd)
        CmdContent = obj_cmd.CmdContent
        if CmdContent.find("DATA UPDATE user")==0 or CmdContent.find("SMS ")==0: #传送用户命令,需要解码成GB2312
            cc = CmdContent
            try:
                cc = cc.encode("gb18030")
            except:
                try:
                    cc = cc.decode("utf-8").encode("gb18030")
                except:
                    import traceback;traceback.print_exc()
                    pass
                    #errorLog(request)
        else:
            cc = str(CmdContent)

        nowcmd = str(cc)
        cc = std_cmd_convert(cc, device)
        if cc:
            resp += "C:%d:%s\n"%(obj_cmd.id, cc)
        if flag_new:
            update_start_end_index(device, 1)#一次下发一条命令
        cache.set("PROCESSING_CMD_OBJ_%s"%sn, obj_cmd)
    else:
        resp += "OK"
    print resp,'---------return resp'
    return resp

#处理紧急命令
import threading
import time
import httplib, urllib
class ProcessTempCmd(threading.Thread):
    def __init__(self):
        super(ProcessTempCmd, self).__init__()
    def run(self):
        from mysite.iclock.cache_cmds import TEMP_CMD_KEY
        print '----run push process temp cmd===='
        while True:
            timeout = 0
            temp_cmd_obj =  None
            while True:
                temp_cmd_lock = cache.get("TEMP_CMD_LOCK_PUSH")
                if temp_cmd_lock:
                    timeout = timeout+1
                    if timeout > 300:
                        printf("-process_temp_cmd---push---timeout***break-", True)
                        break
                    time.sleep(0.5)
                    continue
                else:
                    cache.set("TEMP_CMD_LOCK_PUSH", 1)
                    temp_cmd_list = cache.get(TEMP_CMD_KEY)
                    #print temp_cmd_list,'======temp_cmd_list==key=',cache.get(TEMP_CMD_KEY)
                    if temp_cmd_list:
                        temp_cmd_obj = temp_cmd_list.pop()
                        cache.set(TEMP_CMD_KEY, temp_cmd_list)
                    cache.set("TEMP_CMD_LOCK_PUSH", 0)
                    break
            if temp_cmd_obj:
                device = temp_cmd_obj.SN
                ipaddress = device.ipaddress
                params = ""
                device_server_info = "%s:8370"%ipaddress
                #device_server_info = "192.168.8.41:80"
                conn = httplib.HTTPConnection(device_server_info)
                headers = {"Content-type": "application/x-www-form-urlencoded;charset=gb2312","Accept": "application/json, text/javascript, */*"} 
                try:
                    conn.timeout = 50  
                    conn.request('GET', "?urgCmd=%s"%temp_cmd_obj.CmdContent, params, headers)    
                    #conn.request('GET', "?urgCmd=GET OPTION NetMask,GATEIPAddress", params, headers)
                    #conn.request('GET', "/accounts/login/", params, headers)
                    print '--------conn send request--dir==%s'%dir(conn)
                except Exception, e:
                    print '---conn.request-error=%s'%e
                    temp_cmd_obj.CmdReturn = -10060#发送请求失败
                    temp_cmd_obj.save()
                    conn.close()
                    write_log('---conn.request-error=%s'%e)
                    time.sleep(1.5)
                    continue
                print '========before get response=='
                ret = None
                try:
                    ret = conn.getresponse()
                except Exception, e:
                    print '============get response error=%s'%e
                    pass
                print '========after get response==%s'%ret
                ret_read = ret.read()
                print ret.status,'============ret.status'
                print ret_read, '-------ret_read'
                ret_dict = {}
                if ret.status == 200:
                    rets = ret_read.split('&')
                    print '========rets==',rets
                    ret_return = rets[0]
                    ret_dict[ret_return.split('=')[0]] = ret_return.split('=')[1]
                    if ret_dict["Return"] >= 0:
                        from mysite.iaccess.dev_comm_center import G_DEVICE_GET_OPTION
                        if temp_cmd_obj.CmdContent.startswith("DATA QUERY transaction") > 0:
                            from dev_comm_center import process_event_log
                            try:
                                process_event_log(device, ret_dict["Result"])
                            except Exception, e:
                                printf("PUSH****process_event_log-=-=%s"%e, True)
                                pass
                        elif temp_cmd_obj.CmdContent.startswith(G_DEVICE_GET_OPTION) > 0:
                            ret_result = rets[1].split('Result=')
                            if len(ret_result) > 0:
                                ret_result = ret_result[1].split('=')
                                print '=====ret_result=!!!',ret_result
                                for r in ret_result:
                                    rets = r.split('=')
                                    ret_dict[rets[0]] = rets[1]#待处理
                            print '&&&&&&&&ret_dict===', ret_dict
                    temp_cmd_obj.CmdReturn = ret_dict["Return"]
                else:
                    temp_cmd_obj.CmdReturn = 0 - int(ret.status)#请求响应失败
                temp_cmd_obj.CmdTransTime = datetime.datetime.now()
                temp_cmd_obj.save()
            time.sleep(1.5)
            continue
                
                
                
        
