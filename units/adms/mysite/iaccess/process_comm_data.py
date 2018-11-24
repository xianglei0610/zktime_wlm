# -*- coding: utf-8 -*-
#! /usr/bin/env python
#
#门禁后台数据中心数据处理方法
#
# Changelog :
#
from django.db import models, connection
from base.middleware import threadlocals
from mysite.personnel.models.model_emp import format_pin, Employee
from mysite.iaccess.devcomm import ERROR_COMM_OK, ERROR_COMM_PARAM
import datetime
from mysite.utils import printf, delete_log, write_log
from traceback import print_exc
import time
g_cursor = connection.cursor()

from models.accmonitorlog import EVENT_LINKCONTROL, CANCEL_ALARM, OPEN_AUXOUT, CLOSE_AUXOUT, EVENT_UNREGISTERCARD, INOUT_SEVER, INOUT_SHORT 

def FmtTTime(ttime):
    try:
        t=int(ttime)
    except:
        t=0
    sec=t % 60
    t/=60
    min=t % 60
    t/=60
    hour=t % 24
    t/=24
    mday=t % 31+1
    t/=31
    mon=t % 12
    t/=12
    year=t+2000
    try:
        tt=datetime.datetime(year, mon+1, mday, hour, min, sec)
        return tt
    except:
        return None

#从跟门相关的事件记录中获取门对象
def obtain_doorobj_from_log(str, doorobj):
    if strtoint(str[4]) in [INOUT_SEVER, INOUT_SHORT, OPEN_AUXOUT, CLOSE_AUXOUT, CANCEL_ALARM]:  #辅助事件 和取消报警事件
        doorobj = None
        #print str[3]
    elif (strtoint(str[4]) == EVENT_LINKCONTROL) and (strtoint(str[6]) == INOUT_SEVER):  #连动事件
        doorobj = None
        #print str[3]
    elif (strtoint(str[4]) == EVENT_LINKCONTROL) and (strtoint(str[6]) == INOUT_SHORT):  #连动事件
        doorobj = None
        #print str[3]
    return doorobj


#用户解析时间记录时的时间转换
def strtodatetime(timestr): #1111-11-11 11:11:11
    dt=timestr.split(' ')
    if len(dt)>1:
        dtime=dt[0].split('-')+dt[1].split(':')
        try:
            tt=datetime.datetime(int(dtime[0]),int(dtime[1]),int(dtime[2]),int(dtime[3]),int(dtime[4]),int(dtime[5]))
        except:
            tt=datetime.datetime(1900,1,1,0,0,0)
        return tt
    else:
        return None

#数据格式转换
def strtoint(str):
    try:
        ret=int(str)
    except:
        ret=0
    return ret

#将字符串转换成日期格式
def str_to_date(str):
    date = str[0:4] + '-' + str[4:6] + '-' + str[6:8]
    return date


#处理用户信息，插入到数据库中
def process_user_info(qret):
    if qret['result'] == 0:
        return {"ret": qret['result'], "retdata": ""}
    elif qret['result'] > 0:
        try:
            #处理从设备中获取的用户信息
            ret_data = qret['data'].split('\r\n')
            user_info_list = ret_data[1:-1]
            #print '+++++++++user_info_list =',qret['data']
            if user_info_list != []:
                i = 0
                if ret_data[0].split(",")[0] == "UID":  #inbio 比C3多一个字段
                    i = 1
#                print 'come into user_info'
                from mysite.personnel.models.model_morecardempgroup import AccMoreCardEmpGroup
                from mysite.personnel.models.model_issuecard import IssueCard, CARD_VALID, CARD_OVERDUE
                pin_list = []#人员编号列表
                pin_emp_dict = {} #字典，存储人员
                emps = Employee.all_objects.all()
                for emp in emps:
                    pin_list.append(emp.PIN)
                    pin_emp_dict[emp.PIN] = emp
  
                #将设备中的用户存放到一个默认部门
                from mysite.personnel.models.model_dept import Department
                dept = Department.objects.get(id=1)
                
                #发卡表
                issue_card_dict = {}
                issue_card = IssueCard.objects.filter(cardstatus__in=[CARD_OVERDUE, CARD_VALID])
                for issue in issue_card:
                    issue_card_dict[issue.UserID] = issue

                for user_info in user_info_list:  
                    user_info = user_info.split(",")
                    card = int(user_info[0+i])
                    pin = format_pin(user_info[1+i])
                    password = user_info[2+i]  
                    group = int(user_info[3+i]) #人员组
                    start = user_info[4+i] #启用门禁日期
                    end = user_info[5+i] #结束门禁日期
                    
                    start_time = start != '0' and str_to_date(start) or None
                    end_time = end != '0' and str_to_date(end) or None
                    card = card or ""
                    more_card_group = AccMoreCardEmpGroup.objects.filter(id=group)#查询人员组
                    if more_card_group:#人员组存在
                        more_card_group = more_card_group[0]
                    else:
                        more_card_group = None
                        
#                    if pin in pin_list:#如果用户存在，更新数据
#                        emp = pin_emp_dict[pin]
##                        print 'pin in pin_list'
#                        
#                        emp.acc_startdate = start_time
#                        emp.acc_enddate = end_time
#                        emp.morecard_group = more_card_group
#                        emp.Password = password
#                        emp.save(force_update=True)
                    if pin not in pin_list:#不存在, 插入数据库
                        employee = Employee(PIN=pin, DeptID=dept, Password=password, acc_startdate=start_time, acc_enddate=end_time, morecard_group=more_card_group)
                        employee.save(force_insert=True)
                        
                        if issue_card_dict.has_key(employee):
                            iss_card = issue_card_dict[employee]
                            iss_card.cardno = card
                            iss_card.save()
                        else:
                            iss_card = IssueCard()
                            iss_card.UserID = employee
                            iss_card.cardno = card
                            iss_card.cardstatus = CARD_VALID
                            iss_card.save()
        except:
            print_exc()
        return {"ret": qret['result'], "retdata": ""}

    else:
        return {"ret": -1, "retdata": ""}

#处理指纹信息，保存到数据库中        
def process_template_info(qret):
    if qret['result'] == 0:
        return {"ret": qret['result'], "retdata": ""}
    elif qret['result'] > 0:
        try:
            #处理从设备中获取的指纹信息
            template_info_list = qret['data'].split('\r\n')[1:-1]
            #print ' +++++++++++++template_info_list = ',  template_info_list 
            if template_info_list != [] and template_info_list[0].split(',')[1] != "":#设备中有指纹信息
#                print 'comm into template'
                from mysite.iclock.models.model_bio import Template
                for template_info in template_info_list:  
                    template_info = template_info.split(",")
                    user_id = template_info[1]
                    pin = format_pin(template_info[2])
                    finger_id = template_info[3]#手指
                    valid = int(template_info[4])#指纹类别
                    template = template_info[5]
                    if template == 0:#指纹为0，后面的数据都是错误值，跳出
                        break
                    employee = Employee.objects.filter(PIN=pin)
                    #处理手指数据类型

                    if finger_id == '':
                        finger_id = None
                    else:
                        finger_id = int(finger_id)
#                    print 'finger_id = ', finger_id
                     
                    #template_info = Template.objects.filter(UserID=user_id, FingerID=finger_id, Fpversion='10')
                    try:
                        employee = Employee.objects.filter(PIN=pin)
                        template_info = Template(UserID=employee[0], Template=template, FingerID=finger_id, Valid=valid, Fpversion='10')
#                        template_info.save(force_insert=True)    #这里不能保存，保存过后用户的10.0指纹数量会+胁迫指纹个数
                    except:
                        pass

        except:
            print_exc()
        return {"ret": qret['result'], "retdata": ""}

    else:
        return {"ret": -1, "retdata": ""}

#判断通讯错误类型
def is_comm_io_error(errorid):
    return ((errorid < ERROR_COMM_OK) and (errorid > ERROR_COMM_PARAM))

#删除临时命令
def delete_tempcmd(dev, devcmd_list, d_server, acmd=None):#从字典缓存中删除临时命令
    try:
        if devcmd_list:
            if acmd:
                d_server.delete_sub_dict("TEMP_CMD", dev.id, acmd)#执行成功或执行超时的命令，从字典缓存中删除
            else:#进程中取出该设备的命令后或者删除设备时，将该设备的命令缓存清空
                d_server.delete_sub_dict("TEMP_CMD", dev.id)
#        else:
            #write_log('---- delete_tempcmd devcmd_list is None in =%d'%dev.id)
    except Exception, e:
        printf('---except--delete_tempcmd--e=%s'%e, True)
        pass

#设置某个门的状态
def set_doorstr(istr, val, doorid): 
    dest = [0,0,0,0]
    for i in range(0, 4, 1):
        dest[i] = istr>>(i*8)&0xFF
    dest[doorid-1] = val
    return dest[0] | (dest[1]<<8) | (dest[2]<<16) | (dest[3]<<24)

#门禁控制器事件记录写入考勤原始记录表
#def sync_to_att(cursor, devobj, pin, time):
#    from django.db import IntegrityError
#    from mysite.personnel.models.model_emp import format_pin
#    pin = (len(pin)>0) and pin or 0
#    try:
#        #sql = "insert into checkinout(userid,sn_name,checktime) select userid,'%s','%s' from userinfo where badgenumber=%s"%(devobj.sn,strtodatetime(time),pin)
#        sql=sqls.sync_to_att_insert(devobj.sn,strtodatetime(time),pin)
#        cursor.execute(sql)
#        connection._commit()
#    except IntegrityError:
#        connection._commit()
#        pass
#    except Exception, e:
#        connection.close()#必须先断开，才能重新建立，否则无效-darcy20120110
#        print_exc()
#    
#        while(1):#避免扔掉数据，直到数据库重新连接上后再将该条记录插入---darcy20120113
#            try:
#                time.sleep(3)#3秒。避免CPU过于繁忙-darcy20120113
#                #print '----before re get the cursor'
#                global g_cursor
#                g_cursor = connection.cursor()
#                #print '-----cursor=',cursor
#                sync_to_att(cursor,devobj, pin, time)
#                #print '---break'
#                break
#            except Exception, e:
#                #print '---while 1 continue e=', e
#                continue
#    
#            
#        #print '---after save_event_log'
#        printf('--------execute sql e=%s'%e, True)
#        pass
#门禁控制器事件记录写入考勤原始记录表
def sync_to_att(cursor, devobj, pin, time):    
    from mysite.sql_utils import p_execute
    import sqls
    if int(pin):
        sql=sqls.sync_to_att_insert(devobj.sn,strtodatetime(time),format_pin(pin))
        res = p_execute(sql)
        if res is None:
            pass