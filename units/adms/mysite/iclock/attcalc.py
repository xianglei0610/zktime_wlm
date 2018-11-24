#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################
## 模块功能: 计算考勤/计考勤
## 模块入口: 考勤计算与报表
## 编写日期: 2010-05-13
## 作者:     刘新喜
################################################################
#from mysite.att.models import *
#from mysite.iclock.models import *
from mysite.iclock.tools import *
#from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.utils.encoding import  force_unicode
from django.utils.translation import ugettext as _
from django.db.models.fields import AutoField, FieldDoesNotExist
from mysite.iclock.datasproc import *
from mysite.iclock.iutils import *
from django.conf import settings
from django.db import  connection
from django.core.paginator import Paginator, InvalidPage
from mysite.att.models.modelproc import customSql,customSqlEx
from mysite.iclock.models.model_trans import Transaction
from random import random
import datetime
from mysite.att.models.num_run_deil import NUM_RUN_DEIL
from mysite.att.models.model_empspecday import EmpSpecDay
from django.db.models import Q
from mysite.att.models.attshifts import attShifts
from dbapp.utils import getJSResponse
from decimal import Decimal
from mysite.att.models.model_setuseratt import SetUserAtt
try:
    from django.db.models import Sum
except:
    pass


import datetime
import copy


                                              
isCalcing=-1
AttRule={}
AttRuleStrKeys=('CompanyLogo','CompanyName')


def auto_calculate(calculate_all):
    from mysite.att.models import WaitForProcessData
    import time
    from django.contrib.auth.models import User, Permission, Group
    from base.middleware import threadlocals

    #objs=WaitForProcessData.all_objects.filter(flag=1).order_by("id")
    objs=WaitForProcessData.objects.filter(flag=1).order_by("id")
    #last_customer=None
    for obj in objs:
        try:
            
#            if last_customer!=obj.customer:                    
#                threadlocals._thread_locals.user=None
#                u=User.objects.filter(customeradmin__customer=obj.customer).order_by("id")[0]            
#                threadlocals._thread_locals.user=u   
#                last_customer=obj.customer   
                  
            print "process id '%(pk)s'    %(user)s"%{'pk':obj.pk,'user':obj.UserID} 
            endtime=obj.endtime
            if obj.endtime>datetime.datetime.now():
                endtime=datetime.datetime.now()
            MainCalc_new([obj.UserID.pk],None,obj.starttime,endtime)
            obj.flag=2
        except:
            obj.flag=3
            import traceback;traceback.print_exc()    
        try:
            obj.save()
        except:
            pass
        time.sleep(0.1)
    if calculate_all:  #每日进行一次前一天的考勤计算
        from mysite.personnel.models import Department
        depts=Department.objects.all()
        print len(depts)
        yesterday=datetime.datetime.now().date()+datetime.timedelta(days=-1)
        pks=[d.pk for d in depts]
        MainCalc_new(None,pks,yesterday,yesterday)


def MainCalc_new(UserIDList,DeptIDList,d1,d2,isForce=0):
    """
        @UserIDList 用户ID 例如[1,2,3,4] 
        @DeptIDList 部门ID 例如[1,2,3,4]
        @d1 开始时间  datetime类型
        @d2  结束时间 datetime类型
    """
    from mysite.att.models import attShifts,attRecAbnormite,AttException,attCalcLog
    from mysite.att.models import NUM_RUN  ,SchClass ,AttException #考勤班次,考勤时段,刘新喜加入
    from mysite.personnel.models import Employee
    global isCalcing
    d1=trunc(d1)
    d2=trunc(d2)#datetime.datetime(d2.year,d2.month,d2.day,23,59,59,0)
    if d1>d2:
        return -1
    if d2>trunc(datetime.datetime.now()):
        return -3
    if not allowAction(d1,1,d2):
        return -4
    if isCalcing==1: #是否正在统计
        return -5
    isCalcing=1
    
    global LeaveClasses,AttRule
    global AttAbnomiteRptItems
    global StartDate,EndDate
    global UserSchPlan
    global AttRule
    global schclass #时段
    global NUM_RUN #班次
    global schclass_all
    global empleavedata
    global calcitem 
    global leavetype   
    empleavedata = None
    schclass_all = list(SchClass.objects.all().order_by('StartTime'))    #刘新喜加入
    num_run_all = list(NUM_RUN.objects.all())      #刘新喜加入    
    
    userids=[]
    StartDate=d1
    EndDate=d2
    if DeptIDList:#有传部门进来就按照部门中的人统计
        calcDepts=[]
        for t in DeptIDList:
            StartDate=d1
            EndDate=d2
            calcDepts.append(t)
            if len(calcDepts)>300: #300个部门去数据库查一次人
               ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
               for u in ues:
                   userids.append(u)
               calcDepts=[] #清空
            
        if len(calcDepts)>0:#最后的数量没有超过300
            ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
            for u in ues:
                userids.append(u)
    else:#没有传部门进来就按照传进来的人统计
        userids=UserIDList
        
    if userids==[]: #人员为空
        isCalcing=0
        return 0
    
    if isForce: #是否需要初始化
        InitData()
        
    try:
        global rmdattabnormite
        global rmdRecAbnormite
        AttRule=LoadAttRule(True)
        calcitem = getcalcitem()                  #取计算项目
        leavetype=getleaveitem()                  #取请假类别
        itemcontent=[]                            #默认的计算项目
        for item in calcitem:
           if item.LeaveID in [1000,1001,1002,1003,1004,1005,1008,1009,1013]:
              tempitem={'MinUnit':item.MinUnit,'Unit':item.Unit,'RemaindProc':item.RemaindProc,'ReportSymbol':item.ReportSymbol}
              itemcontent.append(tempitem)        
        for u in userids:
            #getattFields(attShifts,rmdattabnormite)
            StartDate=datetime.datetime(d1.year,d1.month,d1.day,0,0,0)
            EndDate=datetime.datetime(d2.year,d2.month,d2.day,23,59,59)
            
            u=int(u)
            UserSchPlan=LoadSchPlan(u,True,False)
            valid=bool(UserSchPlan['Valid'])
            if valid:
                uobj=Employee.objects.filter(pk=u)
                attShifts.objects.filter(
                    UserID=uobj,
                    AttDate__gte=StartDate.date(),
                    AttDate__lte=EndDate.date()
                ).delete() #考勤明细表
                attCalcLog.objects.filter(
                    UserID=uobj,
                    StartDate__gte=StartDate,
                    EndDate__lte=EndDate
                ).delete() #考勤计算日志
                attRecAbnormite.objects.filter(
                    UserID=uobj,
                    AttDate__gte=StartDate,
                    AttDate__lte=EndDate
                ).delete() #统计结果详情
                AttException.objects.filter(
                    UserID=uobj,
                    StartTime__gte=StartDate,
                    EndTime__lte=EndDate
                ).delete() #异常记录表
                
                #从此处开始由刘新喜修改。程序入口也改成attcalc_oneemp。                
                if valid:
                    #导入每个人每天的考勤记录。一天的日期应该到23:59:59
                   empcheckdata = Transaction.objects.filter(UserID = u,TTime__gte=d1,TTime__lte=d2+datetime.timedelta(days=1,hours=23,minutes=59,seconds=59)).order_by('UserID','TTime')
                   #取每个人每天的请假记录
                   empleavedata = EmpSpecDay.objects.filter(emp = u,audit_status=2,start__lte=d2+datetime.timedelta(minutes=2879),end__gte=d1).order_by('emp','start')
                   #取临时调休的设置
                   emptx = SetUserAtt.objects.filter(UserID = u,endtime__gte=d1,starttime__lte=(d2+datetime.timedelta(minutes=1439))).order_by('UserID','starttime')    
                   from mysite.att.models import USER_OF_RUN
                   shclass=None
                   usersch=[]
                   usersch=list(USER_OF_RUN.objects.filter(UserID=u,EndDate__gte=d1,StartDate__lte=(d2+datetime.timedelta(minutes=1439))).order_by('-pk').values_list('NUM_OF_RUN_ID','StartDate','EndDate'))
                   if len(usersch)>0:
                      #班次明细
                      shclass = list(NUM_RUN_DEIL.objects.filter(Num_runID__in=[e[0] for e in usersch]).order_by('Num_runID','id').values_list('SchclassID','Sdays','Num_runID'))
                   from mysite.att.models.user_temp_sch import USER_TEMP_SCH
                   #临时排班
                   etempsch = list(USER_TEMP_SCH.objects.filter(UserID = u,ComeTime__lte=d2+datetime.timedelta(days=1,hours=23,minutes=59,seconds=59),LeaveTime__gte=d1).order_by('UserID','ComeTime').values_list('SchclassID','WorkType','ComeTime','LeaveTime','Flag'))
                   from mysite.att.models import Holiday
                   #节假日表
                   isholiday=Holiday.objects.filter(start_time__gte=(d1+datetime.timedelta(days=-100))).order_by('start_time').values('name','start_time','duration')
                   #开始计算                                                                                                                                                            
                   attcalc_oneemp(u,d1,d2,calcitem,leavetype,itemcontent,empcheckdata,empleavedata,emptx,usersch,shclass,etempsch,isholiday,num_run_all)                                      
                   time.sleep(0.1)
    except:
        import traceback;traceback.print_exc()
    isCalcing=0
    return len(userids)


#计算每个人每天考勤。
def attcalc_oneemp(u,d1,d2,ci,leavetype,itemcontent,empcheckdata,empleavedata,emptx,usersch,shclass,etempsch,isholiday,num_run_all):
    global empinfo 
    empinfo = getempinfo(u)
    
    #人员u的加班单记录
    from mysite.att.models.model_overtime import OverTime
    overtimedata = OverTime.objects.filter(emp = u,audit_status=2,starttime__lte=d2+datetime.timedelta(minutes=2879),endtime__gte=d1).order_by('emp','starttime')
    
    day_current = d1
    while day_current<=d2:
        if day_current > d2 or day_current <todatetime(empinfo['HireDate']):             #如果当前日期大于结束日期或者当前日期小于聘用日期则跳出当前循环
           day_current = day_current + datetime.timedelta(days=1)            
           continue
        if empinfo['firedate']!= None:   #如果是离职人员且当前日期已经超过了离职日期则跳出当前循环
           if day_current > todatetime(empinfo['firedate']):
              day_current = day_current + datetime.timedelta(days=1)            
              continue              
        #计算每天的考勤。
        attcalc_oneemp_oneday(u,day_current,ci,leavetype,itemcontent,empcheckdata,empleavedata,emptx,usersch,shclass,etempsch,isholiday,num_run_all, overtimedata)
        day_current = day_current + datetime.timedelta(days=1)      
        
#计算每个人每天的考勤日报。
def attcalc_oneemp_oneday(u,currentday,ci,leavetype,itemcontent,empcheckdata,empleavedata,emptx,usersch,shclass,etempsch,isholiday,num_run_all, overtimedata):
    #求每个人每天的班次    
    weekday = (currentday.weekday()+1)%7    
    empshift,schclassdetail = getshift_byuserdate(u,currentday,weekday,usersch,shclass,num_run_all)
    #求每个班次所包含的时间段，但是时间段有可能会跨天，如果在设置班次时间段时没有注意顺序的话，容易出错。
    empshiftschclass = None      
    checktype = False
    try:
       temp = []
       tempworktype=[]
       tempflag=0
       if etempsch:
          for e in etempsch:
              if e[2]<=(currentday+datetime.timedelta(minutes=1439)) and e[3]>=currentday and e[2]>=currentday:
                 for elem in schclass_all:
                     if elem.pk==e[0]:
                        temp.append(elem)
                        tempworktype.append(e[1]) #WORKTYPE  工作类型
                        tempflag=e[4] #1,_(u'仅临时排班有效')),(2,_(u'追加于员工排班之后')),
       emptempsch = temp
    except:
       import traceback;traceback.print_exc()
       pass    
    
    if len(schclassdetail)==0 and not empshift and not emptempsch:  #如果没有排班也没有临时排班，则为弹性班次。
       checktype = True
       schclassdetail =[1,]
       empshift=1
    temp_list=[]      
    
    #schclassdetail,empshiftschclass为空的情况是有班次但是班次周期中没有这一天(使用弹性班次),或者只有临时排班
    if len(schclassdetail)>0:
        for e in schclassdetail:
            for elem  in schclass_all:
               if elem.pk==e:
                   temp_list.append(elem)
        #时段对象
        empshiftschclass =temp_list # filter(lambda f:(f.pk,) in schclassdetail,schclass_all)

    #求每个人每天的工作状态。
    empworktype = getworktype_byuserdate(u,currentday,weekday,empshift,schclassdetail,checktype,isholiday)
    #根据班次时间段进行循环。    
    if empshiftschclass != None:#非临时排班班次
       try:         
         if empshift!=1: #不是弹性班次
            lasttime = datetime.datetime(1900,1,1,0,0,0)             
            if not emptempsch or len(emptempsch)==0 or (len(emptempsch)>0 and tempflag==2):  #无临时排班，或者有临时排班，但是临时排班是追加在排班之后的时候。           
               iii=0
               for ef in empshiftschclass:             
                   acttime = getchecktime(ef,empcheckdata,currentday,lasttime,['I','O','0','1'],empshift,empshiftschclass[0].StartTime,iii,len(empshiftschclass) -1)  #取刷卡时间并对应签到签退
                   if emptx:   #存在调休
                      calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,calctx(ef,currentday,emptx,empworktype,empshiftschclass[0].StartTime),empshift,1,leavetype,itemcontent)  #计算实际的项目并保存。
                   else:
                      calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,empworktype,empshift,1,leavetype,itemcontent)  #计算实际的项目并保存。
                   if acttime['actcheckout']!=None:
                      lasttime = acttime['actcheckout']
                   else:
                      if acttime['actcheckin']!=None:
                         lasttime = acttime['actcheckin']
                      else:
                         lasttime = datetime.datetime(1900,1,1,0,0,0)
                   iii = iii+1
            #临时排班，以临时排班时设置的工作类型计算。
            iii=0
            nworktype=0
            for sf in emptempsch:
                ef = sf
                acttime = getchecktime(ef,empcheckdata,currentday,lasttime,['8,9'],empshift,emptempsch[0].StartTime,iii,len(emptempsch) -1)
                if emptx: 
                   calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,calctx(ef,currentday,emptx,tempworktype[nworktype],empshiftschclass[0].StartTime),0,1,leavetype,itemcontent)
                else:
                   calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,tempworktype[nworktype],0,1,leavetype,itemcontent)
                if acttime['actcheckout']!=None:
                   lasttime = acttime['actcheckout']
                else:
                   if acttime['actcheckin']!=None:
                      lasttime = acttime['actcheckin']
                   else:
                      lasttime = datetime.datetime(1900,1,1,0,0,0)
                iii=iii+1
                nworktype= nworktype+1            
         else:#弹性班次
            try:
                lasttime = datetime.datetime(1900,1,1,0,0,0) 
                empshiftschclass =  filter(lambda f: f.pk in (1,),schclass_all) 
                ii = filattercord(currentday,empcheckdata)
                if ii in [0,1]:
                  ii = 2                  
                if ii>=2:   
                  iii =0       
                  for i  in range(ii/2):             
                      acttime = getchecktime(empshiftschclass[0],empcheckdata,currentday,lasttime,['I','O','0','1','8','9'],empshift,empshiftschclass[0].StartTime,iii,ii/2)  #取刷卡时间并对应签到签退
                      if emptx:
                         calcresult = calcitemandsave(acttime,empshiftschclass[0],currentday,u,empleavedata, overtimedata,ci,calctx(empshiftschclass[0],currentday,emptx,empworktype,empshiftschclass[0].StartTime),empshift,i,leavetype,itemcontent)  #计算实际的项目并保存。                                                 
                      else:
                         calcresult = calcitemandsave(acttime,empshiftschclass[0],currentday,u,empleavedata, overtimedata,ci,empworktype,empshift,i,leavetype,itemcontent)  #计算实际的项目并保存。
                      if acttime['actcheckout']!=None:
                         lasttime = acttime['actcheckout']
                      else:
                         if acttime['actcheckin']!=None:
                            lasttime = acttime['actcheckin']
                         else:
                            lasttime = datetime.datetime(1900,1,1,0,0,0)
                      iii = iii +1
                else:
                  iii =0
                  for i  in [0]:#range(len(empleavedata)):             
                      acttime = getchecktime(empshiftschclass[0],empcheckdata,currentday,lasttime,['I','O','0','1','8','9'],empshift,empshiftschclass[0].StartTime,iii,0)  #取刷卡时间并对应签到签退
                      if emptx:
                         calcresult = calcitemandsave(acttime,empshiftschclass[0],currentday,u,empleavedata, overtimedata,ci,calctx(empshiftschclass[0],currentday,emptx,empworktype,empshiftschclass[0].StartTime),empshift,i,leavetype,itemcontent)  #计算实际的项目并保存。                                                
                      else:
                         calcresult = calcitemandsave(acttime,empshiftschclass[0],currentday,u,empleavedata, overtimedata,ci,empworktype,empshift,i,leavetype,itemcontent)  #计算实际的项目并保存。
                      if acttime['actcheckout']!=None:
                         lasttime = acttime['actcheckout']
                      else:
                         if acttime['actcheckin']!=None:
                            lasttime = acttime['actcheckin']
                         else:
                            lasttime = datetime.datetime(1900,1,1,0,0,0)
                      iii = iii +1
            except:
               import traceback;traceback.print_exc()
       except:
         import traceback;traceback.print_exc()
    else:
        #没有排班，但是有临时排班的情况。
        if emptempsch :
           try: 
              lasttime = datetime.datetime(1900,1,1,0,0,0)   
              iii =0    
              nworktype=0        
              for ef in emptempsch:
                  acttime = getchecktime(ef,empcheckdata,currentday,lasttime,['I','o','1','0','8,9'],empshift,emptempsch[0].StartTime,iii,len(emptempsch) -1)
                  if emptx:
                     calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,calctx(ef,currentday,emptx,tempworktype[nworktype],emptempsch[0].StartTime),empshift,1,leavetype,itemcontent)  #工作类型、班次代码(未知)、第几段
                  else:
                     calcresult = calcitemandsave(acttime,ef,currentday,u,empleavedata, overtimedata,ci,tempworktype[nworktype],0,1,leavetype,itemcontent)  #工作类型、班次代码(未知)、第几段
                  if acttime['actcheckout']!=None:
                     lasttime = acttime['actcheckout']
                  else:
                     if acttime['actcheckin']!=None:
                        lasttime = acttime['actcheckin']
                     else:
                        lasttime = datetime.datetime(1900,1,1,0,0,0)
                  iii = iii +1
                  nworktype = nworktype+1
           except:       
              import traceback;traceback.print_exc()
           
def filattercord(currentday,attrecord):
    ii=0
    for a in attrecord:
        if (a.TTime).day == currentday.day:
           ii =ii +1
    return ii 
        
    
#每个人每天的班次。#暂时不考虑自动排班
def getshift_byuserdate(u,currentday,wd,usersch,shclass,num_run_all):
    u"返回这一天的班次ID和时间段ID列表[ID1,ID2]，如果这一天没有排班，或者说该班次周期中没有这一天，则时间段为None"
    ushift=None #这一天所属的班次
    ushclass=[] #这一天所属时段ID
    ushiftunits=1
    ushiftcycle=1
    for u in usersch:
        if todatetime(u[1])<=todatetime(currentday) and todatetime(u[2])>=todatetime(currentday):
           ushift=u
           break
    
    if ushift:
       for s in num_run_all: #找班次
           if s.pk==ushift[0]:
              ushiftunits=s.Units
              ushiftcycle=s.Cycle
              break    
       if ushiftunits==1: #按周为周期找这一天是否有有排班
           #ycm--2011-06-03bug 原因   这里没有循环判断 以 班次的开始时间开始 计算 ，除以
          cdays = (todatetime(currentday) - todatetime(ushift[1])).days
          wd1=cdays%(ushiftcycle*7)
          if wd1>7:
              wd +=(wd1/7)*7
          
          for uc in shclass: #shclass 当前用户的班次详情，排了几天班
              if  uc[2]==ushift[0] and uc[1]==wd: #班次相等，并且这一天在班次周期中，则得到这一天的时间段ID
                  ushclass.append(uc[0])
            
       if ushiftunits==0: #按照天
          cdays = (todatetime(currentday) - todatetime(ushift[1])).days
          if cdays >= ushiftcycle:
             cdays = cdays%ushiftcycle
            
          for uc in shclass:
              if uc[2]==ushift[0] and uc[1]==cdays:
                 ushclass.append(uc[0]) 
       if ushiftunits==2: #按照月
          cdays = currentday.day -1
          for uc in shclass:
              if uc[2]==ushift[0] and uc[1]==cdays: 
                 ushclass.append(uc[0])
    else:
       ushclass = []       
    if ushclass:
       return ushift[0],ushclass
    else:
       return None,ushclass
    
def getworktype_byuserdate(u,currentday,weekday,empshift,schclassdetail,checkty,isholiday):
    empworktype = 0  #0为正常上班，1为平时加班,2为休息加班,3为节假日。
    for h in isholiday:
        if todatetime(h['start_time'])<=currentday and (todatetime(h['start_time'])+datetime.timedelta(days=h['duration']))>currentday:
           empworktype = 3
           break
        else:
            empworktype =0
    if empworktype == 0 and checkty ==True:     #未指定班次时间段时候认为是休息。
       empworktype=2
    return empworktype
    
        
    
#取每个段的刷卡时间、迟到、早退时间、提前加班时间、延迟加班时间。
def getchecktime(ef,empcheckdata,currentday,lasttime,recordstate,empsh,firststarttime,iii,lenef):    
    #构造范围
    if ef.CheckInTime1 == None:#如果没有设置开始签到时间，则设置为签到时间前30分钟
       ef.CheckInTime1 = todatetime2(ef.StartTime) + datetime.timedelta(minutes = -30)
    if ef.CheckInTime2 == None:
       ef.CheckInTime2 = todatetime2(ef.StartTime) + datetime.timedelta(minutes = 30) 
    if ef.CheckOutTime1 ==None:
       ef.CheckOutTime1 = todatetime2(ef.EndTime) + datetime.timedelta(minutes = -30)
    if ef.CheckOutTime2 == None:
       ef.CheckOutTime2 = todatetime2(ef.EndTime) + datetime.timedelta(minutes = 30)
    actcheckin = datetime.datetime(1900,1,1,0,0,0)
    actcheckout = datetime.datetime(1900,1,1,0,0,0)
    startrest1 = datetime.datetime(1900,1,1,0,0,0)
    endrest1 = datetime.datetime(1900,1,1,0,0,0)
    startrest2 = datetime.datetime(1900,1,1,0,0,0)
    endrest2 = datetime.datetime(1900,1,1,0,0,0) 
    rest1=0
    rest2=0   
    istate=''
    ostate=''
    #当前时段当天开始签到时间
    checkintqTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                               ef.CheckInTime1.hour,ef.CheckInTime1.minute,ef.CheckInTime1.second)
    #当前时段当天结束签到时间
    checkinycTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                              ef.CheckInTime2.hour,ef.CheckInTime2.minute,ef.CheckInTime2.second)
    #当前时段当天上班时间
    checkInTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                              ef.StartTime.hour,ef.StartTime.minute,ef.StartTime.second)
    if todatetime2(firststarttime)>todatetime2(ef.StartTime):     #如果第一段的上班时间大于该段的上班时间则说明后跨天
       checkInTime = checkInTime + datetime.timedelta(days=1)
    if todatetime2(ef.CheckInTime1)>todatetime2(ef.StartTime) and todatetime2(firststarttime)==todatetime2(ef.StartTime):   #如果提前时间大于上班时间说明是前跨天
        checkintqTime= checkintqTime - datetime.timedelta(days=1)
    if todatetime2(ef.CheckInTime2)<todatetime2(ef.StartTime) or todatetime2(firststarttime)>todatetime2(ef.StartTime):   #如果延迟时间小于上班时间说明是后跨天
        checkinycTime= checkinycTime + datetime.timedelta(days=1)
    if ef.StartRestTime!=None and ef.EndRestTime!=None and ef.StartRestTime!=startrest1 and ef.EndRestTime!=endrest1:
       if ef.StartRestTime>ef.StartTime:
          startrest1 = datetime.datetime(currentday.year,currentday.month,currentday.day,ef.StartRestTime.hour,
                                         ef.StartRestTime.minute,0)
       if ef.StartRestTime<=ef.StartTime:
          startrest1 = datetime.datetime(currentday.year,currentday.month,(currentday.day+1),ef.StartRestTime.hour,
                                         ef.StartRestTime.minute,0)
       if ef.EndRestTime>ef.StartRestTime:
          endrest1 = datetime.datetime(currentday.year,currentday.month,currentday.day,ef.EndRestTime.hour,
                                       ef.EndRestTime.minute,0)
       if ef.EndRestTime<=ef.StartRestTime:
          endrest1 = datetime.datetime(currentday.year,currentday.month,(currentday.day+1),ef.EndRestTime.hour,
                                       ef.EndRestTime.minute,0)
    if ef.StartRestTime1!=None and ef.EndRestTime1!=None and ef.EndRestTime!=None and ef.StartRestTime1!=startrest2 and ef.StartRestTime1!=endrest2: 
       if ef.StartRestTime1>ef.EndRestTime:
          startrest2 = datetime.datetime(currentday.year,currentday.month,currentday.day,ef.StartRestTime1.hour,
                                         ef.StartRestTime1.minute,0)
       if ef.StartRestTime1<=ef.EndRestTime:
          startrest2 = datetime.datetime(currentday.year,currentday.month,(currentday.day+1),ef.StartRestTime1.hour,
                                         ef.StartRestTime1.minute,0)
       if ef.EndRestTime1>ef.StartRestTime1:
          endrest2 = datetime.datetime(currentday.year,currentday.month,currentday.day,ef.EndRestTime1.hour,
                                       ef.EndRestTime1.minute,0)
       if ef.EndRestTime1<=ef.StartRestTime1:
          endrest2 = datetime.datetime(currentday.year,currentday.month,(currentday.day+1),ef.EndRestTime1.hour,
                                       ef.EndRestTime1.minute,0) 
    #当前时段当天开始签退时间
    checkouttqTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                               ef.CheckOutTime1.hour,ef.CheckOutTime1.minute,ef.CheckOutTime1.second)
    #当前时段当天结束签退时间
    checkoutycTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                               ef.CheckOutTime2.hour,ef.CheckOutTime2.minute,ef.CheckOutTime2.second)
    #当前时段当天下班时间
    CheckOutTime = datetime.datetime(currentday.year,currentday.month,currentday.day,
                              ef.EndTime.hour,ef.EndTime.minute,ef.EndTime.second)                            
    #if todatetime2(ef.CheckOutTime1)>todatetime2(ef.EndTime)or (ef.StartTime>ef.EndTime and todatetime2(ef.CheckOutTime1)>todatetime2(ef.EndTime)):    #如果提前时间大于下班时间说明是前跨天
    #    checkouttqTime = checkouttqTime - datetime.timedelta(days=1)
    if ef.StartTime>ef.EndTime and ef.CheckOutTime1<ef.EndTime or todatetime2(firststarttime)>todatetime2(ef.StartTime):
        checkouttqTime = checkouttqTime + datetime.timedelta(days=1)
    if todatetime2(ef.CheckOutTime2)<todatetime2(ef.EndTime) or todatetime2(firststarttime)>todatetime2(ef.StartTime) or (ef.StartTime>ef.EndTime and todatetime2(ef.CheckOutTime2)>todatetime2(ef.EndTime)):    #如果延迟时间小于下班时间说明是后跨天
        checkoutycTime = checkoutycTime + datetime.timedelta(days=1)       
    if ef.StartTime>ef.EndTime or todatetime2(firststarttime)>todatetime2(ef.StartTime):     #如果上班时间大于下班时间则说明后跨天。
       CheckOutTime = CheckOutTime + datetime.timedelta(days=1)
    #取上班时间
    intervalTime=9999
    actcheckin =None
    for itimein in empcheckdata:
       if actcheckin != None and (dtconvertint(itimein.TTime) - dtconvertint(actcheckin))<=AttRule['MinRecordInterval']:
         continue          #重复记录要过滤掉。
       if itimein.TTime<checkintqTime or itimein.TTime>checkinycTime:
         continue
       #if itimein.State!=2 and itimein.State!=3 and AttRule['OutCheckRecType']==1: #外出记录被剔除。
       if itimein.State not in recordstate and AttRule['OutCheckRecType']==1:  #外出记录被剔除。
         continue
       if itimein.TTime <=lasttime: #小于上一段的时间的卡被过滤出。
         continue
       if itimein.TTime<=currentday and empsh==1:  #弹性班次不支持跨天。
          continue
       if itimein.TTime>(currentday + datetime.timedelta(minutes=1440)) and empsh==1: #弹性班次不支持跨天。
          continue
       if AttRule['TakeCardIn'] == 2:
           i_min =(abs(dtconvertint(itimein.TTime) - dtconvertint(checkintqTime)))
       else: 
           i_min =(abs(dtconvertint(itimein.TTime) - dtconvertint(checkInTime)))        
       if empsh!=1:         
          if i_min<intervalTime:
             if AttRule['TakeCardIn'] == 2:
                 if actcheckin!= None and actcheckin !=datetime.datetime(1900,1,1,0,0,0) and itimein.TTime < checkintqTime:   
                    continue
             else:
                 if actcheckin!= None and actcheckin !=datetime.datetime(1900,1,1,0,0,0) and itimein.TTime > checkInTime:
                    continue          
             actcheckin = itimein.TTime
             intervalTime = i_min
             istate = itimein.State
       else:  #弹性班次取卡
          if (dtconvertint(itimein.TTime) - dtconvertint(lasttime))<=AttRule['MinRecordInterval']: 
              break
          else:
              actcheckin = itimein.TTime
              intervalTime = i_min
              istate = itimein.State 
              break          
    if (actcheckin==None or intervalTime==9999) and ef.CheckIn==0 and empsh!=1:   #不需要签到时，需要产生一个随机的卡。
        actcheckin = checkInTime+datetime.timedelta(minutes=-int(random()*10))
    #取下班卡
    intervalTime = 9999
    actcheckout = None
    for itimeout in empcheckdata:
        if actcheckin != None:
           if itimeout.TTime<=actcheckin: #下班时间必须大于上班时间
              continue
        if itimeout.TTime<checkouttqTime or itimeout.TTime>checkoutycTime:  #小于提前大于延迟的卡被过滤。
           continue    
        if actcheckout != None and (dtconvertint(itimeout.TTime) - dtconvertint(actcheckout))<=AttRule['MinRecordInterval']:
           continue           #重复记录要剔除   
        if actcheckin!= None and (dtconvertint(itimeout.TTime) - dtconvertint(actcheckin))<=AttRule['MinRecordInterval']:
           continue     #与上班卡相比，如果小于重复卡时间，也被过滤。
        #if itimeout.State!=2 and itimeout.State!=3 and AttRule['OutCheckRecType']==1: #外出记录被剔除。
        if itimeout.State not in recordstate and AttRule['OutCheckRecType']==1:   #外出记录被剔除。
           continue    
        if itimeout.TTime<=lasttime: #小于上一段的时间卡被过滤出。
           continue
        if itimeout.TTime<=currentday and empsh==1:  #弹性班次不支持跨天。
           continue
        if itimeout.TTime>(currentday + datetime.timedelta(minutes=1440)) and empsh==1: #弹性班次不支持跨天。
           continue       
        if actcheckin==None and lasttime.year ==1900 and ef.StartTime==firststarttime and iii==0 and lenef>0 and (abs(dtconvertint(itimeout.TTime) - dtconvertint(CheckOutTime)))>=20:     
           continue    #去掉本段是第一段并且不止一段并且无签到时占用第二段的上班时间的BUG。！！！！！！！！！！！！慎用       
        if AttRule['TakeCardOut'] == 2:
            i_min = (abs(dtconvertint(itimeout.TTime) - dtconvertint(checkoutycTime)))   
        else:       
            i_min = (abs(dtconvertint(itimeout.TTime) - dtconvertint(CheckOutTime)))   
        if empsh!=1:
           if AttRule['TakeCardOut'] == 2:
               if i_min<intervalTime or (itimeout.TTime<=checkoutycTime and actcheckout!=None and actcheckout<checkoutycTime):
                  actcheckout = itimeout.TTime
                  intervalTime = i_min
                  ostate = itimeout.State
           else:  
               if i_min<intervalTime or (itimeout.TTime>=CheckOutTime and actcheckout!=None and actcheckout<CheckOutTime):
                  actcheckout = itimeout.TTime
                  intervalTime = i_min
                  ostate = itimeout.State
        else:   #弹性班次取卡
           if actcheckin != None:
               actcheckout = itimeout.TTime
               intervalTime = i_min
               ostate = itimeout.State           
               break
           else:
               actcheckout =None
               break
            
    if (actcheckout==None or intervalTime==9999) and ef.CheckOut==0 and empsh!=1:   #不需要签退时，需要产生一个随机的卡。
        actcheckout = CheckOutTime + datetime.timedelta(minutes=int(random()*10))
    tqtime =0
    yctime =0    
    if actcheckin !=None and actcheckin<checkInTime:
       tqtime = (dtconvertint(checkInTime) - dtconvertint(actcheckin))
    if actcheckout !=None and actcheckout>CheckOutTime:
       yctime = (dtconvertint(actcheckout) - dtconvertint(CheckOutTime))
    if actcheckin != None:
       if actcheckin>checkInTime and ((dtconvertint(actcheckin) - dtconvertint(checkInTime)))>=ef.LateMinutes:
          latetime = (dtconvertint(actcheckin) - dtconvertint(checkInTime))
       else:
          latetime =0
    else:
        latetime =0
    if actcheckout != None:
       if actcheckout<CheckOutTime and ((dtconvertint(CheckOutTime) -dtconvertint(actcheckout)))>=ef.EarlyMinutes:
          earlytime = (dtconvertint(CheckOutTime) - dtconvertint(actcheckout))
       else:
          earlytime = 0
    else:
        earlytime =0
    acttime = {'actcheckin':actcheckin,'actcheckout':actcheckout,'tqtime':tqtime,'yctime':yctime,
               'latetime':latetime,'earlytime':earlytime,'bccheckin':checkInTime,'bccheckout':CheckOutTime,'istate':istate,'ostate':ostate,
               'startrest1':startrest1,'endrest1':endrest1,'startrest2':startrest2,'endrest2':endrest2,
               'rest1':(endrest1-startrest1).seconds/60,'rest2':(endrest2-startrest2).seconds/60}
    return acttime

#依据取出来的实际打卡和详细的提前及延迟时间进行各项目的计算。
#def caltime(acttime,ef,currentday,u):
def decquan(d,leng=1,flag=1):
    from decimal import Decimal,ROUND_HALF_UP,ROUND_DOWN
    if leng==1:     
       if flag==0:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_HALF_UP)
       else:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_DOWN) 
    else:
       if flag==0:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_HALF_UP)
       else:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_DOWN)
      
def calculate_overtime(currentday,ef,overtimedata,init_overtime,itemcontent):
    '''
    加班单计算
    '''
    action_type = AttRule['jbd_action_type']
    start = ef.CheckInTime1
    end = ef.CheckOutTime2
    time = datetime.timedelta(minutes=0)
    ret = ''
    val = 0
    for e in  overtimedata:
        start_time = e.starttime.time()
        start_date = e.starttime.date()
        if start_date ==currentday.date() and start_time>=start and  start_time<end:
            time += e.endtime - e.starttime
    from mysite.att.calculate.utils import deal_param
    time=deal_param(time.seconds,itemcontent,ef.shiftworktime*60, ef.WorkDay)
    if init_overtime>0:
        if time>0:
            if action_type == 1:
                ret = init_overtime
            elif action_type == 2:
                ret =  time
            elif action_type == 3:
                ret =  min(init_overtime,time)
            ret = str(ret)
            val = ret
        else:
            if action_type == 1:
                ret = str(init_overtime) + u'(加班单暂缺)'
                val = init_overtime
            else:
                ret = '0.0'
                val = 0   
    else:
        if time>0:
            if action_type == 2:
                ret = str(time) + u'(主计算为零)'
                val = time
            else:
                ret = '0.0'
                val = 0   
        else:
            ret = '0.0'
            val = 0
    return ret,val
      
def calcitemandsave(acttime,ef,currentday,u,eLeave, overtimedata, ci,worktype,empsh,itemn,leavetype,itemcontent):
    #先保存请假
    from mysite.att.models import AttException,LeaveClass,attRecAbnormite  
    #拆分请假记录。
    if ef.shiftworktime==0 and worktype==0:
       worktype=1   
    empexcept = []
    if worktype==0:
       try:
          empexcept = calcleave(acttime,ef,currentday,eLeave,empsh)
       except:
          import traceback;traceback.print_exc()
    eactleave =0
    nocheckin = 0
    nocheckout =0
    present = 0
    absent = 0
    absenttr = 0
    late =0
    early = 0
    tqycov = 0
    ov =0
    xxov =0    
    jjov =0
    check =0
    gdov =0
    ssymbol=''
    exceptid =[]
    #itemcontent=[]    
    #for item in ci:
    #    if item.LeaveID in [1000,1001,1002,1003,1004,1005,1008,1009,1013]:
    #       tempitem={'MinUnit':item.MinUnit,'Unit':item.Unit,'RemaindProc':item.RemaindProc,'ReportSymbol':item.ReportSymbol}
    #       itemcontent.append(tempitem)    
    if itemn==1:
       start_old=datetime.datetime(1900,01,01,0,0,0)
       end_old=datetime.datetime(1900,01,01,0,0,0)
       for etime,start,end,leavename in empexcept:
           if start_old==start:
              continue
           att_exp = AttException()
           att_exp.StartTime=start
           att_exp.EndTime = end
           att_exp.UserID_id =u
           att_exp.ExceptionID = leavename
           if etime>ef.shiftworktime:
              etime = ef.shiftworktime           
           k1,k2,k3 = getleaveCalcUnit(leavetype,leavename)
           if k1==1:     
              if k3==1:      
                 ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(intdata(decquan(decquan(etime,3)/60),k2,k3))
              else:
                 ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(decquan(decquan(etime,3)/60,1,1))
              att_exp.TimeLong = intdata(etime/60,k2,k3)
              #att_exp.InScopeTime = intdata(etime/60,k2,k3)              
           if k1==2:
              ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(etime)
              att_exp.TimeLong = etime#intdata(etime,k2,k3)
              #att_exp.InScopeTime = etime#intdata(etime,k2,k3)            
           if k1==3:
              if ef.shiftworktime!=0: 
                 if k3==1:                
                    ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(decquan(intdata((decquan(etime,3)/60)/(decquan(ef.shiftworktime,3)/60),k2,k3))*decquan(ef.WorkDay))
                 else:
                    ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(decquan(decquan(etime,3)/60/(decquan(ef.shiftworktime,3)/60),1,1)*decquan(ef.WorkDay))
                 att_exp.TimeLong = intdata(etime/60/ef.shiftworktime,k2,k3)
                 #att_exp.InScopeTime = intdata(etime/60/ef.shiftworktime,k2,k3)                  
              else:  
                 if k3==1:               
                    ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(intdata(decquan(decquan(etime,3)/60/(480/60)),k2,k3)*decquan(ef.WorkDay))
                 else:
                    ssymbol = ssymbol + getleaveReportSymbol(leavetype,leavename)+str(decquan(decquan(etime,3)/60/(480/60),1,1)*decquan(ef.WorkDay))
                 att_exp.TimeLong = intdata(etime/60/480,k2,k3)
                 #att_exp.InScopeTime = intdata(etime/60/480,k2,k3)  
           print ssymbol
           att_exp.InScopeTime =  etime               
           att_exp.AttDate = currentday
           att_exp.OverlapWorkDayTail = 1
           att_exp.save()  
           exceptid.append(str(att_exp.pk))
           eactleave = eactleave + etime
           start_old=start
           end_old = end
    if eactleave>ef.shiftworktime:
       eactleave=ef.shiftworktime
    #计算其它的计算项
    if acttime['actcheckin'] and acttime['actcheckin']>datetime.datetime(1900,1,1,0,0,0):
       attrecord = attRecAbnormite()     
       attrecord.UserID_id = u
       attrecord.checktime = acttime['actcheckin']
       attrecord.CheckType = acttime['istate']
       attrecord.NewType = 'I' 
       attrecord.AbNormiteID=0
       attrecord.SchID=0
       attrecord.OP=0
       attrecord.AttDate=currentday
       attrecord.save()
    if acttime['actcheckout'] and acttime['actcheckout']>datetime.datetime(1900,1,1,0,0,0):
       attrecord = attRecAbnormite()        
       attrecord.UserID_id = u
       attrecord.checktime = acttime['actcheckout']
       attrecord.CheckType = acttime['ostate']
       attrecord.NewType = 'O' 
       attrecord.AbNormiteID=0
       attrecord.SchID=0
       attrecord.OP=0
       attrecord.AttDate=currentday
       attrecord.save()             
    if empsh!=1:  #非弹性班次。           
       #计算出勤
       if acttime['actcheckin'] != None and acttime['actcheckout'] !=None:   #两次卡都有的情况
          check = (dtconvertint(acttime['actcheckout']) - dtconvertint(acttime['actcheckin']))
          actworktime = (dtconvertint(acttime['actcheckout']) - dtconvertint(acttime['actcheckin']))
          intime=(acttime['actcheckin'] - datetime.timedelta(minutes=ef.LateMinutes))<=acttime['bccheckin'] and acttime['bccheckin'] or acttime['actcheckin']
          if intime>acttime['startrest1'] and intime<acttime['endrest1'] and acttime['startrest1'].year!=1900:
             intime=acttime['endrest1']
          if intime>acttime['startrest2'] and intime<acttime['endrest2'] and acttime['startrest2'].year!=1900:
             intime=acttime['endrest2']             
          outtime=(acttime['actcheckout']+datetime.timedelta(minutes=ef.EarlyMinutes))>=acttime['bccheckout'] and acttime['bccheckout'] or acttime['actcheckout']         
          if outtime>acttime['startrest1'] and outtime<acttime['endrest1'] and acttime['startrest1'].year!=1900: 
             outtime = acttime['startrest1']
          if outtime>acttime['startrest2'] and outtime<acttime['endrest2'] and acttime['startrest2'].year!=1900: 
             outtime = acttime['startrest2']                      
          #如果是没有迟到早退、缺勤快则工作时间是班次规定的工作时间。
          if acttime['actcheckin']<=acttime['bccheckin'] and acttime['actcheckout']>=acttime['bccheckout']:
             if eactleave==0:
                if worktype!=1:
                   if ef.shiftworktime>0:
                      present = ef.shiftworktime
                   else:
                      present = dtconvertint(outtime) - dtconvertint(intime) - acttime['rest1']
                else: 
                   if dtconvertint(acttime['actcheckout'])>=dtconvertint(acttime['bccheckout']) and acttime['rest1']>0 and ((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))!=ef.shiftworktime):
                      if ef.shiftworktime>0:
                         present = ef.shiftworktime#actworktime - acttime['rest1']
                      else:
                         if acttime['actcheckin']<acttime['startrest1']:
                            present = actworktime - acttime['rest1']
                         else:
                            present = acttime 
                   else:
                      present = actworktime
             else:
                if ef.shiftworktime>0:
                   present = ef.shiftworktime - eactleave
                else:
                   present = dtconvertint(outtime) - dtconvertint(intime) - eactleave - acttime['rest1']
          else:
             if intime<=acttime['startrest1'] and outtime>acttime['endrest2'] and acttime['endrest2'].year!=1900:
                if worktype!=1:
                   present = (dtconvertint(outtime) - dtconvertint(intime)) - acttime['rest1'] - acttime['rest2']
                else:
                   present = actworktime
             else:
                if intime<=acttime['startrest1'] and outtime>=acttime['endrest1'] and acttime['endrest1'].year!=1900:
                   if eactleave==0:
                      if worktype!=1:
                         if dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])==ef.shiftworktime or dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])==(ef.shiftworktime - 1440):
                            present = (dtconvertint(outtime) - dtconvertint(intime)) 
                         else: 
                            present = (dtconvertint(outtime) - dtconvertint(intime)) - acttime['rest1'] #- eactleave
                      else:
                         if acttime['rest1']>0 and dtconvertint(acttime['actcheckout'])>=dtconvertint(acttime['endrest1']) and ((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))>ef.shiftworktime):
                            present = actworktime - acttime['rest1']
                         else:
                            present = actworktime
                   else:
                      if ef.shiftworktime>0:
                         present = ef.shiftworktime - eactleave#(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'] - eactleave
                      else:
                         present = dtconvertint(outtime) - dtconvertint(intime) - eactleave - acttime['rest1']
                else:
                   if eactleave==0:
                      if worktype!=1:
                         present = (dtconvertint(outtime) - dtconvertint(intime)) #- eactleave
                      else:
                         if dtconvertint(acttime['actcheckout'])>=dtconvertint(acttime['bccheckout']) and acttime['rest1']>0 and ((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))>ef.shiftworktime):
                            present = actworktime - acttime['rest1']
                         else:
                            present = actworktime
                   else:
                      present = ef.shiftworktime - eactleave#(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - eactleave 
             if (present+ef.LateMinutes + ef.EarlyMinutes)>ef.shiftworktime and worktype==0:  #消除有迟到、早退的情况下，出勤时间不够的问题。
                if ef.shiftworktime>0:
                   present = ef.shiftworktime
          #计算迟到、早退、旷工           
          if present<ef.shiftworktime and eactleave==0:  #出勤不满规定时间的情况
             if eactleave==0: 
                absent = ef.shiftworktime - present
             else:
                if (present + eactleave)<ef.shiftworktime:
                   absent = ef.shiftworktime - present - eactleave
                if (eactleave + present)>=ef.shiftworktime:
                   present = ef.shiftworktime - eactleave
                   absent = 0
             if absent<=(ef.LateMinutes + ef.EarlyMinutes) and worktype==0:
                absent = 0
          else:
             absent = 0
             #eactleave = 0  #有出勤的时候先默认为自动销假。
          if acttime['latetime']>ef.LateMinutes and worktype!=1:   #一次迟到超过多少分种开始计算为旷工。
             if eactleave==0:
                if acttime['latetime']>=AttRule['MinsLateAbsent'] and AttRule['LateAbsent']==1 :
#                   if absent==0:
                    absent = acttime['latetime']
                else:
                   late = acttime['latetime']
                   if worktype==0:
                      absent =0
             else:
                late =0
                if worktype==0:
                   absent =0             
          else:
             late =0
          if acttime['earlytime']>ef.EarlyMinutes and worktype!=1:  #一次早退超过多少分种开始计算为旷工。
             if eactleave==0:
                if acttime['earlytime']>=AttRule['MinsEarlyAbsent'] and AttRule['EarlyAbsent']==1:
                   if absent==0:
                      absent = acttime['earlytime']
                else:
                   early=acttime['earlytime']
                   if absent==early and worktype==0:
                      absent =0
             else:
                early =0
                if worktype==0:
                   absent =0
          else:
             early =0
       if late>0 and present<ef.shiftworktime and eactleave==0 and present>0 and absent==0:
          present = ef.shiftworktime
       if early>0 and present<ef.shiftworktime and eactleave==0 and present>0 and absent==0:
          present = ef.shiftworktime          
       if acttime['actcheckin'] == None and acttime['actcheckout'] !=None: #缺上班卡
          nocheckin = 1
          if acttime['earlytime']>ef.EarlyMinutes and AttRule['EarlyAbsent']==1:  #一次早退超过多少分种开始计算为旷工。
             if eactleave==0:
                if acttime['earlytime']>AttRule['MinsEarlyAbsent']:
                   absent = ef.shiftworktime#absent + acttime['earlytime']
                else:
                   early=acttime['earlytime']
             else:
                early =0
                absent =0
          else:
              if acttime['earlytime']>ef.EarlyMinutes:
                 early = acttime['earlytime']
          #   early =0          
          if AttRule['NoInAbsent']==2:
             if eactleave == 0:
                absent = ef.shiftworktime
             else:
                absent = ef.shiftworktime - eactleave
             if absent<0:
                absent =0
             present = 0
          else:
             if acttime['actcheckout'] >=acttime['bccheckin']:
                if absent==0:
                   present = ef.shiftworktime - eactleave #- AttRule['MinsNoIn']
                else:
                   present = 0
                if present<0:
                   present = 0
                if worktype!=1:
                   late = AttRule['MinsNoIn']
             else:
                if absent==0:
                   present = ef.shiftworktime - eactleave#(dtconvertint(acttime['actcheckout']) - dtconvertint(acttime['bccheckin'])) - AttRule['MinsNoIn']
                else:
                   present =0
                if present<0:
                   present =0
                if worktype!=1:
                   early = acttime['earlytime']   #这里暂时不考虑旷工的情况。
             late = AttRule['MinsNoIn']            
       if acttime['actcheckin'] !=None and acttime['actcheckout'] == None: #缺下班卡
          nocheckout = 1
          if acttime['latetime']>ef.LateMinutes and AttRule['LateAbsent']==1:   #一次迟到超过多少分种开始计算为旷工。
             if eactleave==0:
                if acttime['latetime']>AttRule['MinsLateAbsent']:
                   absent = ef.shiftworktime#acttime['latetime']
                else:
                   late = acttime['latetime']
                   absent =0
             else:
                late =0
                absent =0  
          else:
              if acttime['latetime']>ef.LateMinutes:
                 late = acttime['latetime']         
          if AttRule['NoOutAbsent']==2:
             if eactleave ==0:
                absent = ef.shiftworktime            
             else:
                absent = ef.shiftworktime - eactleave
                nocheckout =0
             if absent <0:
                absent = 0
             present =0                 
          else:
             if acttime['actcheckin']<acttime['bccheckin']:
                if absent ==0:
                   present = ef.shiftworktime - eactleave #- AttRule['MinsNoOut']
                else:
                   present = 0
                if present<0:
                   present =0
             else:
                if absent==0:
                   present = ef.shiftworktime - eactleave#(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - AttRule['MinsNoOut']
                else:
                   present =0
                if present<0:
                   present =0
                #late=acttime['latetime']
             early = AttRule['MinsNoOut']   # 这里暂时不考虑旷工的情况            
       if acttime['actcheckin'] ==None and acttime['actcheckout'] == None:  #缺两次卡
          nocheckin = 1
          nocheckout = 1
          if eactleave==0:
             absent = ef.shiftworktime
             present =0
          else:
             if ef.shiftworktime>eactleave:
                absent = ef.shiftworktime - eactleave            
             else:
                absent = 0
                eactleave = ef.shiftworktime
             if worktype ==3:   #如果是节假日则应该给其工作时间
                present =ef.shiftworktime
                absent =0
             else:
                present =0
       #加班 , 本应该要加上提前加班，目前暂时不考虑
       if acttime['yctime']>AttRule['MinsOutOverTime'] and ef.IsOverTime>0 and  AttRule['OutOverTime']==1 and worktype!=1:
          tqycov = acttime['yctime']
       #如果既存在旷工，又存在迟到早退的情况，应该要消除旷工时间及迟到早退，此处存在风险。 慎用
#       if absent>(late + early) and (late+early)>0:
          #absent = absent -(late+early)
#          late = 0
#          early =0
       #如果旷工时间=应工作时间，则应该不存在迟到早退。
       if absent >=ef.shiftworktime and ef.shiftworktime>0:
          late =0
          early=0
       if worktype == 1 or (ef.shiftworktime==0 and worktype==0):     #如果工作时间等于0，则本段为加班时间段。
          ov = present
          present =0
          absent =0
          late =0
          early =0          
    if empsh==1:
       if acttime['actcheckin']!=None and acttime['actcheckout']!=None:
          present =(dtconvertint(acttime['actcheckout']) - dtconvertint(acttime['actcheckin'])) - acttime['rest1']
          check = (dtconvertint(acttime['actcheckout']) - dtconvertint(acttime['actcheckin']))          
          #if itemn==1 and present>(ef.shiftworktime+AttRule['MinsOutOverTime']):
          #   tqycov = present - ef.shiftworktime
          #   present = ef.shiftwrorktime             
          late =0
          early =0
          absent =0
    if worktype in [2,3]:
       late =0
       early =0
       absent =0
    if absent>ef.shiftworktime:
       absent = ef.shiftworktime
    #根据考勤参数进行单位换算。
    #应到/实到
    yd =0
    if absent<ef.shiftworktime or ef.shiftworktime==0:
       if eactleave==0:
          if worktype!=1:
             sd =present - late - early#2011 06 21 ycm present+late +early
          else:
             sd = ov - late - early#2011 06 21 ycm ov+late +early
       else:
          sd = present
    else:
       sd =0
    if itemcontent[0]['Unit']==1:
       sd=decquan(Decimal(str(sd))/60)      #lehman 2010-08-27日  
       #sd=decquan(Decimal(str(present))/60)       
    if itemcontent[0]['Unit']==3:
       if ef.shiftworktime!=0:
          sd = decquan((Decimal(str(sd))/ef.shiftworktime) * (Decimal(str(ef.WorkDay)))) #leman 2010-08-27日
          #sd = decquan((Decimal(str(present))/ef.shiftworktime) * (Decimal(str(ef.WorkDay)))) 
          #sd = Decimal(str(round(Decimal(present)/ef.shiftworktime,2)))*Decimal(str(ef.WorkDay),2)
       else:
          if ov>0:
             sd = ef.WorkDay
          else:
             sd =0  
       if sd>1:
          sd=1   
    if sd <0:
       sd =0
    if present<0:
       present=0
    if absent<0:
       absent =0
    #sd = intdata(sd,itemcontent[0]['MinUnit'],itemcontent[0]['RemaindProc'])
    #应到
    if worktype in [0,1]:
       if empsh!=1:
          if itemcontent[0]['Unit']==3:
             if worktype==1:
                #yd = decquan(Decimal(str(ov)))/(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))*decquan(Decimal(str(ef.WorkDay)))
                if ef.shiftworktime>0:
                   yd = decquan(Decimal(str(ov)))/ef.shiftworktime*decquan(Decimal(str(ef.WorkDay)))#(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))*decquan(Decimal(str(ef.WorkDay)))
                else:
#                    2011-05-18 屏蔽  
#                    if acttime['rest1']>0 and acttime['rest1']==0: 
#                       yd = decquan(Decimal(str(ov)))/(dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'] - acttime['rest1']))*decquan(Decimal(str(ef.WorkDay)))
#                    else:
                    yd = decquan(Decimal(str(ov)))/(dtconvertint(acttime['bccheckout']) -dtconvertint(acttime['bccheckin']) - acttime['rest1'] -acttime['rest2'])*decquan(Decimal(str(ef.WorkDay)))
                if yd>decquan(Decimal(str(ef.WorkDay))):
                   yd=ef.WorkDay
             else:
                yd = ef.WorkDay 
          if itemcontent[0]['Unit']==1:
             if worktype!=1:
                yd = decquan(Decimal(str(ef.shiftworktime))/60)
             else:
                if ef.shiftworktime==0:
                   yd = decquan(Decimal(str(ov))/60)
                else:
                   yd = decquan(Decimal(str(ef.shiftworktime))/60)
          if itemcontent[0]['Unit']==2:
             if worktype !=1:
                yd = ef.shiftworktime
             else:
                if ef.shiftworktime==0:
                   yd = ov
                else:
                   yd = ef.shiftworktime
          #ef.shiftworktime
          #Decimal(str(ef.shiftworktime))/AttRule['MinsWorkDay']
       else:
          if itemcontent[0]['Unit']==3:
             yd = ef.WorkDay 
          if itemcontent[0]['Unit']==1:
             yd = decquan(Decimal(str(ef.shiftworktime))/60)
          if itemcontent[0]['Unit']==2:
             yd = ef.shiftworktime
          #ef.shiftworktime
          #Decimal(str(present))/AttRule['MinsWorkDay']
    else:
       yd = 0
    yd = intdata(yd,itemcontent[0]['MinUnit'],itemcontent[0]['RemaindProc'])
    sd = intdata(sd,itemcontent[0]['MinUnit'],itemcontent[0]['RemaindProc'])       
    if sd>yd:
       sd =yd
    #平日加班
    if ov>0:
       if itemcontent[5]['Unit']==1:
          ov = decquan(Decimal(str(ov))/60)
       if itemcontent[5]['Unit']==3:
          ov = decquan(Decimal(str(ov))/60)          
       ov=intdata(ov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])       
    #迟到
    if itemcontent[1]['Unit']==1:
       late=decquan(Decimal(str(late))/60)
    if itemcontent[1]['Unit']==3:
       if ef.shiftworktime!=0:
          late =decquan(Decimal(str(late))/ef.shiftworktime)*decquan(ef.WorkDay)
       else:
          late =decquan(Decimal(str(late))/480)*decquan(ef.WorkDay)         
    late = intdata(late,itemcontent[1]['MinUnit'],itemcontent[1]['RemaindProc'])
    #早退
    if itemcontent[2]['Unit']==1:
       early = decquan(Decimal(str(early))/60)
    if itemcontent[2]['Unit']==3:
       if ef.shiftworktime!=0:
          early = decquan(Decimal(str(early))/ef.shiftworktime)*decquan(ef.WorkDay)
       else:
          early = decquan(Decimal(str(early))/480)*decquan(ef.WorkDay) 
    early =intdata(early,itemcontent[2]['MinUnit'],itemcontent[2]['RemaindProc'])
    #请假
    if itemcontent[3]['Unit']==1:
       eactleave = decquan(Decimal(str(eactleave))/60)
    if itemcontent[3]['Unit']==3:
       if ef.shiftworktime!=0:
          eactleave = decquan(Decimal(str(eactleave))/ef.shiftworktime)*decquan(ef.WorkDay)
       else:
          eactleave = decquan(Decimal(str(eactleave))/480)*decquan(ef.WorkDay)  
    eactleave = intdata(eactleave,itemcontent[3]['MinUnit'],itemcontent[3]['RemaindProc'])
    #旷工
    absenttr = absent
    if itemcontent[4]['Unit'] ==1:
       absenttr = decquan(Decimal(str(absent))/60)
    
    if itemcontent[4]['Unit'] ==3:
       if ef.shiftworktime!=0:
          absenttr = decquan(Decimal(str(absent))/ef.shiftworktime)*decquan(ef.WorkDay)
       else:
          absenttr = decquan(Decimal(str(absent))/480)*decquan(ef.WorkDay) 
    absenttr = intdata(absenttr,itemcontent[4]['MinUnit'],itemcontent[4]['RemaindProc'])
    if itemcontent[5]['Unit'] ==1:
       tqycov = decquan(Decimal(str(tqycov))/60)
    if itemcontent[5]['Unit'] ==3:
       if ef.shiftworktime!=0:
          tqycov = decquan(Decimal(str(tqycov))/ef.shiftworktime)*decquan(ef.WorkDay)
       else:
          tqycov = decquan(Decimal(str(tqycov))/480)*decquan(ef.WorkDay) 
    tqycov = intdata(tqycov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])       
    #if worktype in [0,1]:
    if ef.OverTime>0 and absent==0 and eactleave==0 and acttime['actcheckin']!=None and acttime['actcheckout']!=None and acttime['actcheckin']<=acttime['bccheckin'] and acttime['actcheckout']>=acttime['bccheckout']:
       gdov = ef.OverTime
       if itemcontent[5]['Unit'] ==1:
           gdov = decquan(Decimal(str(gdov))/60)
       if itemcontent[5]['Unit'] ==3:
          if ef.shiftworktime!=0:
             gdov = decquan(Decimal(str(gdov))/ef.shiftworktime)*decquan(ef.WorkDay)
          else:
             gdov = decquan(Decimal(str(gdov))/480)*decquan(ef.WorkDay)
       gdov = intdata(gdov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])
    #如果是自由加班 
#    if worktype == 1:
#       #ov = present
#       if itemcontent[5]['Unit']==1:
#          ov = decquan(Decimal(str(ov))/60)
#       if itemcontent[5]['Unit']==3:
#          if ef.shiftworktime!=0:
#             ov = decquan(Decimal(str(ov))/ef.shiftworktime)*decquan(ef.WorkDay)
#          else:
#             ov = decquan(Decimal(str(ov))/480)*decquan(ef.WorkDay)
#       ov = intdata(ov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])
    #加班应该要加上延时加班
    ov = ov + tqycov + gdov
    #休息加班
    if worktype ==2:
       xxov = present
       if itemcontent[5]['Unit']==1:
          xxov =  decquan(Decimal(str(present))/60)
       if itemcontent[5]['Unit']==3:
          if ef.shiftworktime!=0:
             xxov=decquan(Decimal(str(present))/ef.shiftworktime)*decquan(ef.WorkDay)
          else:
             xxov = decquan(Decimal(str(present))/8)*decquan(ef.WorkDay)
       xxov = intdata(xxov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])
       xxov = xxov + tqycov + gdov
    #加班应该加上延时加班  
    if worktype ==3:
       jjov = present
       if itemcontent[5]['Unit']==1:
          jjov =  decquan(Decimal(str(present))/60)
       if itemcontent[5]['Unit']==3:
          if ef.shiftworktime!=0:
             jjov = decquan(Decimal(str(present))/ef.shiftworktime)*decquan(ef.WorkDay)
          else:
             jjov = decquan(Decimal(str(present))/480)*decquan(ef.WorkDay) 
       jjov = intdata(jjov,itemcontent[5]['MinUnit'],itemcontent[5]['RemaindProc'])
       jjov = jjov + tqycov + gdov
    #加班应该加上延时加班
    if xxov>0 or jjov>0:
       if present>0:
          present =0
       if absent>0:
          absent =0
       if late >0:
          late =0
       if early>0:
          early =0
    if xxov>0:
       ov =0
    if jjov>0:
       ov =0
       xxov =0    
    if late>0 and worktype==0:
       ssymbol = ssymbol + itemcontent[1]['ReportSymbol']
    if early>0 and worktype==0:
       ssymbol = ssymbol + itemcontent[2]['ReportSymbol'] 
    #if eactleave>0:
    #   ssymbol = ssymbol + itemcontent[3]['ReportSymbol'] 
    if absent>0 and worktype==0:
       ssymbol = ssymbol + itemcontent[4]['ReportSymbol']+str(absenttr)
    if ov>0 or xxov or jjov>0:
       ssymbol = ssymbol + itemcontent[5]['ReportSymbol']
    if late==0 and early==0 and absent==0 and eactleave==0 and worktype in [0,1]:
       ssymbol = ssymbol + itemcontent[0]['ReportSymbol']  
    cin = [nocheckin,nocheckin,0,0]  
    cout =[nocheckout,nocheckout,0,0]
    muin =[ef.CheckIn,ef.CheckIn,0,0] 
    muout =[ef.CheckOut,ef.CheckOut,0,0]    
    bctime =0
    if worktype in [2,3]:
       bctime =0
    else:
       if empsh==1:
          bctime = present
       else:
          bctime = ef.shiftworktime              
    if cin[worktype]!=0:
       ssymbol = ssymbol + itemcontent[6]['ReportSymbol']
    if cout[worktype]!=0:
       ssymbol = ssymbol + itemcontent[7]['ReportSymbol']                       
    try:
        attdays = attShifts()
        attdays.UserID_id = u
        attdays.AttDate = currentday
        attdays.ClockInTime = acttime['bccheckin']
        attdays.ClockOutTime = acttime['bccheckout']
        attdays.StartTime = acttime['actcheckin']
        attdays.EndTime = acttime['actcheckout']
        attdays.WorkDay=yd
        attdays.SchIndex = ef.SchclassID
        attdays.AutoSch = 0
        attdays.SchId_id = ef.SchclassID
        attdays.RealWorkDay=sd
        attdays.NoIn=cin[worktype]#(worktype  [2,3] and 0 or nocheckin)
        attdays.NoOut=cout[worktype]#(worktype in [2,3] and 0 or nocheckout)
        attdays.Late = late
        attdays.Early = early
        attdays.Absent = absenttr
        init_overtime = ov + xxov + jjov
        att_OverTime_des,att_OverTime_val = calculate_overtime(currentday,ef,overtimedata,init_overtime,itemcontent[5])#------------------------加班单处理
        
        attdays.OverTime = att_OverTime_val#ov + xxov + jjov
        attdays.OverTime_des = att_OverTime_des
        attdays.WorkTime = check
        attdays.ExceptionID=eactleave
        attdays.Symbol = ssymbol
        attdays.Exception=",".join(exceptid)
        attdays.MustIn= muin[worktype]#(worktype in [2,3] and 0 or ef.CheckIn)
        attdays.MustOut= muout[worktype]#(worktype in [2,3] and 0 or ef.CheckOut)
        attdays.OverTime1= ((ov+xxov+jjov)>0 and 1 or 0)
        attdays.WorkMins = present
        attdays.SSpeDayNormal= (worktype in [0,1] and 1 or 0)
        attdays.SSpeDayWeekend= (worktype==2 and 1 or 0)
        attdays.SSpeDayHoliday= (worktype==3 and 1 or 0)        
        attdays.AttTime = bctime#(empsh!=1 and ef.shiftworktime or present)
        attdays.SSpeDayNormalOT=ov
        attdays.SSpeDayWeekendOT= xxov
        attdays.SSpeDayHolidayOT= jjov
        attdays.AbsentMins= absent
        attdays.AttChkTime = (empsh!=1 and ef.shiftworktime or present)
        attdays.AbsentR= absenttr
        attdays.ScheduleName = ef.SchName
        attdays.IsConfirm= 0
        attdays.IsRead= 0
        attdays.save()
        return 1
    except:
        import traceback;traceback.print_exc()
        return -1
    
def intdata(source,min,flag=0):
    import decimal
    if min==0:
       min =1
    if flag==0:
       try:
          if min!=1:
             if min>1:
                 ret = int(source)/int(min)*min
             else:
                 ret=decimal.Decimal(str(source))//decimal.Decimal(str(min))*decimal.Decimal(str(min))#float
#                ret = float(source)//min*min #向下 舍入 bug
          else:
             ret = int(source) 
       except:
          import traceback;traceback.print_exc()
          ret = source
    if flag==1:   #四舍五入
        if min!=1:
           if min>1:
              if int(source)%int(min)>=(min/2 - 0.0000001):
                 ret = int(source)/int(min)*min+min
              else:
                 ret = int(source)/int(min)*min
           else:
              if int(source*100)%int(min*100)>=((min*100)/2 - 0.0000001):
                 ret = (int(source*100)/int(min*100)*min)+min
              else:
                 ret = (int(source*100)/int(min*100)*min) 
        else:
           if (source*100)%100>=50:
              ret = int(source) +1
           else:
              ret = int(source)
    if flag==2:    #向上取整，如果是最小单位大于20并且不是10的倍数则认为是大于20分钟向上取整成30分钟的情况。
        if min!=1:
           if min>1:
              if int(min)>20 and int(min)%10!=0:
                  if int(source)%(int(30 - min)+int(min))>=int(min):
                     ret = int(source)%30+30
                  else:
                     ret = int(source)%30
              else:  
                  if int(source)%int(min)>0:
                     ret = int(source)/int(min)*min+min
                  else:
                     ret = int(source)/int(min)*min
           else:
              if int(source*100)%int(min*100)>0:
                 ret = (int(source*100)/int(min*100)*min)+min
              else:
                 ret = (int(source*100)/int(min*100)*min) 
        else:
           if (source*100)%100>0:
              ret = int(source) +1
           else:
              ret = int(source)            
    return ret            
def calcleave(acttime,ef,currentday,eLeave,empsh):
   #计算请假
   empleavetime = [] 
   starttime=[]
   endtime = []
   leavename= []
   alreadyleave = False
   for eleave in eLeave: 
      alreadyleave = False         
      if empsh!=1:
         #本段段中请假
         if eleave.start>acttime['bccheckin'] and eleave.end<acttime['bccheckout']:
            if acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and acttime['startrest1']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.start<=acttime['startrest1'] and eleave.end>acttime['endrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and eleave.end<acttime['endrest2']:
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)) - acttime['rest1'])
                  alreadyleave = True
               if eleave.start<=acttime['startrest1'] and eleave.end>acttime['endrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and acttime['endrest2'].year==1900 and alreadyleave==False:
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)) - acttime['rest1']) 
                  alreadyleave = True
               if eleave.start>acttime['startrest1'] and eleave.end<acttime['bccheckout'] and eleave.end>acttime['endrest1'] and alreadyleave==False:
                  if dtconvertint(eleave.start)>dtconvertint(acttime['endrest1']):
                     empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)))
                  else:
                     empleavetime.append((dtconvertint(eleave.end) - dtconvertint(acttime['endrest1'])))                     
                  alreadyleave = True
               if (eleave.end<acttime['startrest1'] and alreadyleave==False) or (eleave.start>acttime['endrest1'] and alreadyleave==False):
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)))
                  alreadyleave = True
               if (eleave.end<=acttime['startrest1'] and alreadyleave==False):
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)))               
            else:
               empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)))
            starttime.append(eleave.start)
            endtime.append(eleave.end)
            leavename.append(eleave.leaveclass.pk)             
         #本段中只请前一部分的时间          
         if eleave.start<=acttime['bccheckin'] and eleave.end<acttime['bccheckout'] and eleave.end>=acttime['bccheckin']:
            if acttime['endrest2']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.end>=acttime['endrest2']:               
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'] - acttime['rest2'])
                  endtime.append(eleave.end)
                  alreadyleave = True
               if eleave.end<acttime['endrest2']:
                  empleavetime.append((dtconvertint(acttime['startrest2']) - dtconvertint(acttime['bccheckin'])) - acttime['rest1']) #- acttime['rest2'])
                  endtime.append(acttime['startrest2'])
                  alreadyleave = True               
            else:
               if eleave.end>=acttime['bccheckin'] and acttime['startrest1'].year==1900:               
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(acttime['bccheckin']))) 
                  endtime.append(eleave.end)
                  alreadyleave = True
            if alreadyleave==False and eleave.end>=acttime['endrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and (eleave.end<acttime['startrest2'] or acttime['startrest2'].year==1900):
               empleavetime.append((dtconvertint(eleave.end) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'])
               endtime.append(eleave.end)
               alreadyleave =True
            if alreadyleave==False and eleave.end<=acttime['endrest1'] and eleave.end>=acttime['startrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and (eleave.end<acttime['startrest2'] or acttime['startrest2'].year==1900):
               empleavetime.append((dtconvertint(acttime['startrest1']) - dtconvertint(acttime['bccheckin'])))
               endtime.append(acttime['startrest1'])
            if alreadyleave==False and eleave.end<acttime['startrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and (eleave.end<acttime['startrest2'] or acttime['startrest2'].year==1900):
               empleavetime.append((dtconvertint(eleave.end) - dtconvertint(acttime['bccheckin'])))
               endtime.append(eleave.end)                
            starttime.append(acttime['bccheckin'])
            #endtime.append(eleave.end)
            leavename.append(eleave.leaveclass.pk)        
         #本段全部请假
         if eleave.start<=acttime['bccheckin'] and eleave.end>=acttime['bccheckout']:
            if (dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin']))>ef.shiftworktime:
               empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'] - acttime['rest2'])
            else:
               empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])))                
            starttime.append(acttime['bccheckin'])
            leavename.append(eleave.leaveclass.pk)
            endtime.append(acttime['bccheckout'])
         #请后半段部分
         if eleave.start>acttime['bccheckin'] and eleave.end>=acttime['bccheckout'] and eleave.start<=acttime['bccheckout']:
            if acttime['startrest1']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.start<=acttime['startrest1']:
                  empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(eleave.start)) - acttime['rest1'])# - acttime['rest2']
                  starttime.append(eleave.start)
                  alreadyleave = True                                     
            else:
               if eleave.start<=acttime['bccheckout'] and acttime['endrest1']==datetime.datetime(1900,1,1,0,0,0):
                  empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(eleave.start)))
                  starttime.append(eleave.start)
                  alreadyleave = True 
            if alreadyleave==False and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.start>acttime['endrest1']  and eleave.start>acttime['startrest2'] and acttime['endrest2']!=datetime.datetime(1900,1,1,0,0,0):             
                  if eleave.start>acttime['endrest1'] and eleave.start<acttime['startrest2'] and eleave.start<acttime['bccheckout']:
                     empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(eleave.start)) - acttime['rest2'])
                     starttime.append(eleave.start)
               else:
                  if eleave.start>acttime['startrest1'] and eleave.start<acttime['bccheckout']:
                     if dtconvertint(eleave.start)>dtconvertint(acttime['endrest1']):
                        empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(eleave.start)))
                        starttime.append(eleave.start)
                     else:
                        empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['endrest1'])))
                        starttime.append(acttime['endrest1']) 
            #else:
               #empleavetime.append((acttime['bccheckout'] - eleave.start).seconds/60)                
            #starttime.append(eleave.start)
            endtime.append(acttime['bccheckout'])
            leavename.append(eleave.leaveclass.pk)        
      else:
         #本段段中请假
         if eleave.start>acttime['bccheckin'] and eleave.end<acttime['bccheckout']:
            if acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and acttime['startrest1']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.start<=acttime['startrest1'] and eleave.end>acttime['endrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and eleave.end<acttime['endrest2']:
                  empleavetime.append(eleave.end - eleave.start - acttime['rest1'])
                  alreadyleave = True
               if alreadyleave==False and eleave.start>acttime['startrest1'] and eleave.end<acttime['bccheckout'] and eleave.end>acttime['endrest1']:
                  empleavetime.append(eleave.end - acttime['endrest1'])
                  alreadyleave = True
               if alreadyleave==False and eleave.end<acttime['startrest1'] or eleave.start>acttime['endrest1']:
                  empleavetime.append(dtconvertint(eleave.end) - dtconvertint(eleave.start))
            else:
               empleavetime.append(dtconvertint(eleave.end) - dtconvertint(eleave.start))
            starttime.append(eleave.start)
            endtime.append(eleave.end)
            leavename.append(eleave.leaveclass.pk)          
         if alreadyleave==False and (eleave.start<=currentday and eleave.end>(currentday + datetime.timedelta(minutes=1440))):
            if acttime['endrest2']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.end>=acttime['endrest2']:              
                  empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'] - acttime['rest2'])
                  alreadyleave = True
            else:
               if eleave.end>=acttime['bccheckout']:              
                  empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])))
                  alreadyleave = True               
            if alreadyleave==False and eleave.end>=acttime['endrest1']and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and (eleave.end<acttime['startrest2'] or acttime['startrest2'].year==1900):
               empleavetime.append((dtconvertint(acttime['bccheckout']) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'])                
            starttime.append(acttime['bccheckin'])
            leavename.append(eleave.leaveclass.pk)
            endtime.append(acttime['bccheckout'])             
         if alreadyleave==False and (eleave.start>currentday and eleave.start<(currentday + datetime.timedelta(minutes=1440)) and eleave.end>(currentday + datetime.timedelta(minutes=1440))):
            empleavetime.append((dtconvertint(eleave.start) - dtconvertint(acttime['bccheckin'])) - acttime['rest1'] - acttime['rest2'])
            starttime.append(acttime['bccheckin'])
            leavename.append(eleave.leaveclass.pk)
            endtime.append(eleave.start)             
         if alreadyleave==False and (eleave.start<=currentday and eleave.end>=currentday and eleave.end<=currentday+datetime.timedelta(minutes=1440)):
            if acttime['endrest2']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.end>=acttime['endrest2']: 
                  empleavetime.append((dtconvertint(acttime['bccheckin']) - dtconvertint(eleave.end)) - acttime['rest1'] - acttime['rest2'])
                  alreadyleave = True
            else:
               if eleave.end>=acttime['bccheckin']: 
                  empleavetime.append((dtconvertint(acttime['bccheckin']) - dtconvertint(eleave.end)) - acttime['rest1'] - acttime['rest2'])
                  alreadyleave = True                
            if alreadyleave==False and eleave.end>=acttime['endrest1'] and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and (eleave.end<acttime['startrest2'] or acttime['startrest2'].year==1900):
               empleavetime.append((dtconvertint(acttime['bccheckin']) - dtconvertint(eleave.end)) - acttime['rest1'])
            starttime.append(eleave.start)
            leavename.append(eleave.leaveclass.pk)
            endtime.append(acttime['bccheckout'])                 
         if alreadyleave==False and (eleave.start>=currentday and eleave.start<=(currentday + datetime.timedelta(minutes=1440)) and eleave.end>=currentday and eleave.end<=(currentday+datetime.timedelta(minutes=1440))):
            if acttime['startrest1']!=datetime.datetime(1900,1,1,0,0,0):             
               if eleave.start<=acttime['startrest1']: 
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)) - acttime['rest1']) #- acttime['rest2'])
                  alreadyleave = True
            else:
               if eleave.start<=eleave.end: 
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)) - acttime['rest1'] - acttime['rest2'])
                  alreadyleave = True
            if alreadyleave==False and acttime['endrest1']!=datetime.datetime(1900,1,1,0,0,0) and acttime['startrest2']!=datetime.datetime(1900,1,1,0,0,0):
               if eleave.start>acttime['endrest1'] and eleave.start<acttime['startrest2']:
                  empleavetime.append((dtconvertint(eleave.end) - dtconvertint(eleave.start)) - acttime['rest2'])
            starttime.append(eleave.start)
            leavename.append(eleave.leaveclass.pk)
            endtime.append(eleave.end)
   return [(empleavetime[i],starttime[i],endtime[i],leavename[i]) for i in range(0,len(empleavetime))]
#计算本段是否调休
def calctx(ef,currentday,eTX,empworkty,firsttime):
    ret = empworkty
    estart = todatetime3(currentday,ef.StartTime)
    eend = todatetime3(currentday,ef.EndTime)
    if ef.StartTime<firsttime:
       estart = todatetime3(currentday + datetime.timedelta(days=1),ef.StartTime)
    if ef.EndTime<firsttime or ef.EndTime<ef.StartTime:
       eend = todatetime3(currentday + datetime.timedelta(days=1),ef.EndTime)
    for etx in eTX:
        if (etx.starttime<=estart and etx.endtime>=eend): #or (etx.starttime>estart and etx.starttime<eend and eend>=etx.endtime) or (etx.starttime<=estart and etx.endtime<=eend and etx.starttime<eend):
           ret = etx.atttype
           break
    return ret
#获取考勤计算项    
def getcalcitem():
    from mysite.att.models.model_leaveclass1 import LeaveClass1
    calcitem=LeaveClass1.objects.all().order_by('LeaveID')
    return calcitem
#获取考勤请假类别
def getleaveitem():
    from mysite.att.models.model_leaveclass import LeaveClass
    calcitem=LeaveClass.objects.all().order_by('LeaveID')
    return calcitem
#获取请假类别的报表符号
def getleaveReportSymbol(lrecord,leaveid):
    for item in lrecord:
        if item.LeaveID==leaveid:
           return item.ReportSymbol
    return ''
def getleaveCalcUnit(lrecord,leaveid):
    for item in lrecord:
        if item.LeaveID==leaveid:
           return item.Unit,item.MinUnit,item.RemaindProc
    return 1,1,0
        
#获取员工信息
def getempinfo(userid):
    from mysite.att.models import UserUsedSClasses,USER_OF_RUN
    Result=False
    empinfo={}
    empinfo['Valid']=1
    t=Employee.objByID(userid) #Employee.objects.filter(id=userid)            #.values('id','DeptID','ATT','AutoSchPlan','OverTime','Holiday','MinAutoSchInterval','INLATE','OutEarly','RegisterOT')
    if t.isatt==None:
        empinfo['Valid']=True
    else:
        empinfo['Valid']=t.isatt
    empinfo['AutoSchPlan']=t.AutoSchPlan
    empinfo['OverTime']=int(t.OverTime==1)
    empinfo['HasHoliday']=int((t.Holiday==None or t.Holiday==1))
    empinfo['MinAutoPlanInterval']=t.MinAutoSchInterval
    empinfo['ClockIn']=t.INLATE
    empinfo['ClockOut']=t.OutEarly
    empinfo['OTRegistry']=t.RegisterOT
    empinfo['DeptID']=t.DeptID_id
    empinfo['UserID']=t.id
    empinfo['UserName']=t.EName
    empinfo['BadgeNumber']=t.PIN
    empinfo['DeptName']=t.DeptID.name
    empinfo['HireDate']=t.Hiredday
    empinfo['firedate']=t.firedate
    return empinfo
    


# 插入日志记录
def PrepareCalcDateByDept(deptid,d1,d2,itype,isForce):
    from mysite.att.models import attCalcLog
    global StartDate,EndDate
    et=None
    nt=trunc(datetime.datetime.now())
    sql=''
    if d1==d2:
        isForce=True
    if isForce:
        if d2<nt:
            EndDate=trunc(d2)
        elif d2>=nt:
            EndDate=nt
        if StartDate<=EndDate:
            if StartDate<EndDate and EndDate==nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, deptid,0,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            elif StartDate<=EndDate and EndDate!=nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, deptid,0,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            StartDate=StartDate-datetime.timedelta(1)
            if sql:
                customSql(sql)
        else:
            return False
        return True
    attlog=attCalcLog.objects.filter(DeptID=deptid,EndDate__gte=d1,StartDate__lte=d2,Type=itype).order_by("StartDate")
    et=None
    l=len(attlog)
    sql=''
    if l==0:
        if d2<=nt:
            EndDate=d2
        else:
            EndDate=nt
        if StartDate<=EndDate:
            if StartDate<EndDate and EndDate==nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,deptid,0,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            elif StartDate<=EndDate and EndDate!=nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,deptid,0,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            if sql:
                customSql(sql)
        else:
            return False
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
        return True
    else:
        tempdate=[] 
        d=d1
        flag=0  #如果统计时间为系统当天时间允许多次统计,但是通过此标记不再插入统计时间
        while d<=d2:
            tempdate.append(d)
            d=d+datetime.timedelta(1)
        calcdate=copy.copy(tempdate)
        for t in attlog:
            t.StartDate=checkTime(t.StartDate)
            t.EndDate=checkTime(t.EndDate)
            if d1>=t.StartDate and d2<=t.EndDate and d2<nt:
                return False
            for tt in tempdate:
                if tt>=t.StartDate and tt<=t.EndDate:
                    if tt==nt:
                        flag=1
                    else:
                        calcdate.remove(tt)
            if not calcdate:
                return False
            tempdate=copy.copy(calcdate)
        if len(calcdate)>1:   #如果超过两天未统计就取两端的日期
            StartDate=calcdate[0]
            EndDate=calcdate[-1]
        else:
            StartDate=calcdate[0]    
            EndDate=calcdate[0]
        sql=''    
        if StartDate<=EndDate and ((len(calcdate)>1) or (len(calcdate)==1 and flag==0)):
            if StartDate<EndDate and EndDate==nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,deptid,0,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            elif StartDate<=EndDate and EndDate!=nt:
                sql="insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,deptid,0,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            if sql:    
                customSql(sql)
#        elif flag!=1:
#            return False
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
    return True
    



#获取考勤规则
def LoadAttRule(reloadData=False):
    from mysite.att.models import AttParam
    global AttRule
    if not reloadData and AttRule!={}:
        return AttRule
    AttRule={
        'CompanyLogo':'Our Company',
        'CompanyName' :'Our Company',
        #    'DBVersion' : '-1',
        'EarlyAbsent':0,                #一次早退大于   分钟记
        'LateAbsent':0,                 #一次迟到大于   分钟记
        'MaxShiftInterval':660,         #最长的班次时间不超过
        'MinRecordInterval':5,            #最小的记录间隔
        'MinsEarly' : 5,                  #提前多少分钟记早退
        'MinsLateAbsent':100,             #多少分钟迟到后开始计算缺勤
        'MinsEarlyAbsent':100,            #多少分钟早退后开始计算缺勤
        'MinShiftInterval':120,          #最短的班次时段
        'MinsLate' : 10,                  #超过多长时间记迟到
        'MinsNoIn' : 60,                  #无签到时记多少分钟
        'MinsNoOut' : 60,                 #无签到时记多少分钟  
        'MinsOutOverTime' : 60,           #下班后多少分钟后开始计算加班。
        'MinsWorkDay' : 480,              #日工作时间
        'MinsWorkDay1' : 0,            #计算用
        'NoInAbsent':1,                   #上班无签到是否计算缺勤
        'NoOutAbsent':1,                  #下班无签退是否计算缺勤
        'TakeCardIn':1,                   #上班签到取卡规则
        'TakeCardOut':1,                #下班签到取卡规则
        
        'jbd_action_type':1,                #加班单作用方式
        
        'OTCheckRecType':2,               #加班状态
        'OutCheckRecType':3,              #外出记录的处理方式(考勤参数)
        'OutOverTime' :1,                 #下班后记加班
        'TwoDay' : '0',                   #班次跨天时计为第一天还是第二天。
        'WorkMonthStartDay' : 1,          #工作月开始日
        'WorkWeekStartDay' : 0,           #工作周开始日
    }
    qryOptions=AttParam.objects.all()
    for qryOpt in qryOptions:
        for k in AttRule.keys():
            if k==qryOpt.ParaName:
                if qryOpt.ParaValue=='on':
                    AttRule[k]=1
                elif k not in AttRuleStrKeys:
                    AttRule[k]=int(qryOpt.ParaValue)
                else:
                    AttRule[k]=qryOpt.ParaValue
                break
    return AttRule

def InitData():
    u'''初始化过程变量'''
    global Schedules
    global SchDetail
    global schClass
    global UserSchPlan
    global AttAbnomiteRptItems
    global AbnomiteRptItems
    global LeaveClasses
    global LClasses1
    global qryLeaveClass1
    global tHoliday
    tHoliday=None
    Schedules=None
    SchDetail=None
    schClass=None
    qryLeaveClass1=None
    UserSchPlan={}
    ExceptionIDs=[]
    rmdattexception=[]
    AttAbnomiteRptItems=[]
    LeaveClasses=[]
    LClasses1=[]
    AbnomiteRptItems=[]
    calcitem=None 
    leavetype=None



#获取员工的考勤设置
def LoadSchPlan(userid,LoadAutoIds, LoadSchArray,LoadPlan=True):
    from mysite.att.models import UserUsedSClasses,USER_OF_RUN
    Result=False
    schPlan={}
    schPlan['MayUsedAutoIds']=[]
    schPlan['SchArray']=[]
    schPlan['Valid']=1
    t1=datetime.datetime.now()
    if LoadPlan:
        t=Employee.objByID(userid) #Employee.objects.filter(id=userid)            #.values('id','DeptID','ATT','AutoSchPlan','OverTime','Holiday','MinAutoSchInterval','INLATE','OutEarly','RegisterOT')
#        for t in sch:
        if t.isatt==None:
            schPlan['Valid']=True
        else:
            schPlan['Valid']=t.isatt
        schPlan['AutoSchPlan']=t.AutoSchPlan
        schPlan['OverTime']=int(t.OverTime==1)
        schPlan['HasHoliday']=int((t.Holiday==None or t.Holiday==1))
        schPlan['MinAutoPlanInterval']=t.MinAutoSchInterval
        schPlan['ClockIn']=t.INLATE
        schPlan['ClockOut']=t.OutEarly
        schPlan['OTRegistry']=t.RegisterOT
        schPlan['DeptID']=t.DeptID_id
        schPlan['UserID']=t.id
        schPlan['UserName']=t.EName
        schPlan['BadgeNumber']=t.PIN
        schPlan['DeptName']=t.DeptID.name
    if LoadAutoIds:    #智能排班
        qryUserUsedClass=UserUsedSClasses.objects.filter(UserID=userid)
        len(qryUserUsedClass)
        for t in qryUserUsedClass:
            schPlan['MayUsedAutoIds'].append(t.SchId)
    if LoadSchArray:   #排班表
        i=0
        qryEmpSchedule=USER_OF_RUN.objects.filter(UserID=userid).order_by('StartDate')
        len(qryEmpSchedule)
        for t in qryEmpSchedule:
            i=i+1
            schPlan['SchArray'].append({"numID":i,'SchId':t.NUM_OF_RUN_ID_id,'StartDate':t.StartDate,'EndDate':t.EndDate,'SchName':t.NUM_OF_RUN_ID.Name})
    return schPlan

def reCaluateAction(request):
        from mysite.personnel.models import Employee,Department        
        if request.method=="POST":
            try:
                from mysite.att.report_utils import parse_report_arg
                userids,deptids,st,et,offset = parse_report_arg(request)
                isforce=request.POST.get('isForce','0')

                if userids or deptids:        
                        t1=datetime.datetime.now()
                        #re=MainCalc(userids,deptids,st,et,int(isforce))# lehman 2010-06-01 屏蔽 
                        try:
                                                   
                           re = MainCalc_new(userids,deptids,st,et,int(isforce)) # lehman 2010-06-01 加入
                        except:
                            import traceback;
                            traceback.print_exc()     
                            re=-3                       
                        t2=datetime.datetime.now()-t1
                        if re==-3:
                                r=getJSResponse("result=-3")
                        elif re==-4:
                                r=getJSResponse("result=0;message=%s"%(_(u"账户被锁定！")))
                        else:
                                r=getJSResponse("result=0;message=%s%s%d sec"%(_(u'计算成功'),_(u'总时间'),t2.seconds))
                else:
                        r=getJSResponse("result=1")
                return r
            except:
                import traceback;traceback.print_exc()

def getattFields(self,dict):
    #f=('UserID','SchIndex','AutoSch','AttDate','SchId','ClockInTime','ClockOutTime ','StartTime',
                        #'EndTime','WorkDay','RealWorkDay','NoIn','NoOut','Late','Early','Absent',
                    #'OverTime','WorkTime','ExceptionID','Symbol','MustIn','MustOut','OverTime1',
                #'WorkMins','SSpeDayNormal','SSpeDayWeekend','SSpeDayHoliday','AttTime','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT',
            #'AbsentMins','AttChkTime','AbsentR','ScheduleName')
    field_names = [f.column for f in self._meta.fields if not isinstance(f, AutoField)]
    for t in field_names:
        dict[t]='null'
def PrepareCalcDate(u,d1,d2,itype,isForce):
    from mysite.att.models import attCalcLog
    global StartDate,EndDate
    et=None
    nt=trunc(datetime.datetime.now())
    sql=''
    if d1==d2:
        isForce=True
    if isForce:
        if d2<nt:
            EndDate=trunc(d2)
        elif d2>=nt:
            EndDate=nt
        if StartDate<=EndDate:
            if StartDate<EndDate and EndDate==nt:
                sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, u,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            elif StartDate<=EndDate and EndDate!=nt:
                sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
                
            StartDate=StartDate-datetime.timedelta(1)
            if sql:
                customSql(sql)
        else:
            return False
        return True
    attlog=attCalcLog.objects.filter(UserID=u,EndDate__gte=d1,StartDate__lte=d2,Type=itype).order_by("StartDate")
    et=None
    l=len(attlog)
    if l==0:
        if d2<=nt:
            EndDate=d2
        else:
            EndDate=nt
        if StartDate<EndDate and EndDate==nt:
            sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,u,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
        elif StartDate<=EndDate and EndDate!=nt:
            sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
        if sql:
            customSql(sql)

        return True
    else:
        tempdate=[] 
        d=d1
        flag=0  #如果统计时间为系统当天时间允许多次统计,但是通过此标记不再插入统计时间
        while d<=d2:
            tempdate.append(d)
            d=d+datetime.timedelta(1)
        calcdate=copy.copy(tempdate)
        for t in attlog:
            t.StartDate=checkTime(t.StartDate)
            t.EndDate=checkTime(t.EndDate)
            if d1>=t.StartDate and d2<=t.EndDate and d2<nt:
                return False
#            for tt in tempdate:
#                if tt>=t.StartDate and tt<=t.EndDate:
#                    if tt==nt:
#                        flag=1                 #如果当天统计过不想再统计可关闭此句
#                    else:
#                        calcdate.remove(tt)
            if not calcdate:
                return False
            tempdate=copy.copy(calcdate)
        if len(calcdate)>1:   #如果超过两天未统计就取两端的日期
            StartDate=calcdate[0]
            EndDate=calcdate[-1]
        else:
            StartDate=calcdate[0]    
            EndDate=calcdate[0]
        sql=''    
        if StartDate<=EndDate and ((len(calcdate)>1) or (len(calcdate)==1 and flag==0)):
            if StartDate<EndDate and EndDate==nt:
                sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,u,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            elif StartDate<=EndDate and EndDate!=nt:
                sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            if sql:
                customSql(sql)

#        elif flag!=1:
#            return False
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
    return True
def todatetime(idate):
    return datetime.datetime(idate.year,idate.month,idate.day,0,0,0)

def todatetime2(t):
    return datetime.datetime(1900,1,1,t.hour,t.minute,t.second)
def todatetime3(d,t):
    return datetime.datetime(d.year,d.month,d.day,t.hour,t.minute,t.second)
def dtconvertint(t):
    if t.year>1900:
       return (todatetime(t) - datetime.datetime(1900,1,1,0,0,0)).days * 24*60 + t.hour*60 + t.minute
    else:
       if t.day==1:
          return t.hour*60 + t.minute
       else:
          return t.hour*60 + t.minute +1440
      
       
#    if (t.year%4)==0:
#       s = '312931303130313130313031'
#    else:
#       s = '312931303130313130313031'
    