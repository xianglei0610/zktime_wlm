#!/usr/bin/python
# -*- coding: utf-8 -*-
#from mysite.personnel.models import *
from mysite.att.models import *
from mysite.iclock.models import *
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

try:
    from django.db.models import Sum
except:
    pass
#import types

import datetime
import copy
qry_user_of_run=None
Schedules=None
SchDetail=None
qrytempsch=None
tHoliday=None
schClass=None
ExcepData=None
CheckInOutData=None
l_CheckInOutData=0  #保存记录数
qryAudit=None
qryLeaveClass1=None
UserID=0
DeptID=0

isCalcing=0
schClasses=[]
LClasses1=[]
UserSchPlan={}
AttRule={}
LeaveClasses=[]
AttAbnomiteRptItems=[]
AbnomiteRptItems=[]

AttAbnomiteRptIndex={}
WorkTimeZone=[]
AutoWorkTime={}
AutoWorkTime1={}
CheckInOutRecorNo=0
(sbStart, sbEnd)=range(2)
(rmTrunc, rmRound, rmUpTo, rmCount)=range(4)
(auDay, auHour, auMinute, auWorkDay, auTimes)=range(5) #考勤计算单位
(suDay, suWeek, suMonth)=range(3) #班次时长单位
ExceptionIDs=[]
(tsrNoShift, tsrInOut, tsrIn, tsrOut)=range(4)
(caeFreeOT,caeOT,caeOut,caeBOut)=range(-4,0)   #自由加班  加班  外出  因公外出
ExceptionName=transExceptionName()
(ocIgnore, ocOut, ocBOut, ocConfirm)=range(4)
(csShift,csOverTime, csShiftOut, csOpenLock)=range(4)
RecAbnormiteOfState=(csOverTime,csOverTime,csShiftOut,csShiftOut)
(otcIgnore, otcOT, otcConfirm)=range(3)
CCheckName=(u"%s"%_(u'上班'),u"%s"%_(u'加班'),u"%s"%_(u'外出'),u"%s"%_(u'开锁'))
(raValid, raInvalid, raRepeat, raErrorState,raOut, raOT, raFreeOT, raAutoSch)=range(8)
FirstExceptionID=2
rmdattexception=[]
rmdattabnormite={}
rmlattabnormite=[]
rmdRecAbnormite={}
rmlRecAbnormite=[]
rmdattexceptionEx=[]

ClTA=[]
ChPA=[]
ExceptDataIn=False
WorkTimeIn=False
WorkTimeIndex=0
SpecialIntervals=[]
MinDate=datetime.datetime(2000,1,1,0,0)
MaxDate=datetime.datetime(2099,12,30,0,0)
CCheckInTag=[('O','I'),('O','I'),('0','1'),('u','l')]
AttAbnomiteRptIDs=(1000,1007,1008,1009,1004,1001,1002,1005,1013,1012,1003)
(aaValid, aaHoliday,aaNoIn, aaNoOut, aaAbsent, aaLate, aaEarly,aaOT,aaFOT, aaOut, aaBLeave)=AttAbnomiteRptIDs
AttRecord = {'CheckTime':datetime.datetime(2000,1,1,0,0),
         'CheckType':'I',
         'RecordConfirmed': False,
         'TypeConfirmed':True }
for i in range(4):
    ClTA.append(AttRecord.copy())

AttCheckPoint = {'CCTime':None,
         'CCStart':None,
         'CCEnd':None,
         'CCState': None,
         'InState':None,
         'OutState':None,
         'CCMust':None,
         'CCAuto':None,
         'SNo':None,
         'SSNo':None,
         'ENo':None,
         'Index':None
     }

for i in range(3):
    ChPA.append(AttCheckPoint.copy())


def checkForget():
    dic={}
    l=[]
    l1=[]
    l3=[]
    #user=Employee.objects.all().values('id','PIN','DeptID','EName')
    #dep=Department.objects.all().values('DeptID','DeptName','parent')

    #for t  in user:
        #d={}
        #for k in t.keys():
            #d[k]=t[k]
        #l.append(d.copy())
    #for t in dep:
        #d={}
        #for k in t.keys():
            #d[k]=t[k]
        #l1.append(d.copy())
    for i in ATTSTATES:
        d=force_unicode(dict(ATTSTATES).get(i[0]), strings_only=True)
        #        d = unicode(dict(ATTSTATES).get(i[0],i[0]))
        l3.append(d)

#    dic['Employee']=l
#    dic['Department']=l1
    dic['states']=l3
    return dic




AttRuleStrKeys=('CompanyLogo','CompanyName')

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
'MinsEarly' : 0,                  #提前多少分钟记早退
'MinsLateAbsent':100,
'MinsEarlyAbsent':100,            #早退大于的分钟
'MinShiftInterval':120,          #最短的班次时段
'MinsLate' : 0,                  #超过多长时间记迟到
'MinsNoIn' : 60,                  #无签到时记? 分钟
'MinsNoOut' : 60,
'MinsOutOverTime' : 60,
'MinsWorkDay' : 480,
'MinsWorkDay1' : 0,            #计算用
'NoInAbsent':1,                   #上班无签到
'NoOutAbsent':1,
'TakeCardIn':1,                   #上班签到取卡规则
'TakeCardOut':1,                #下班签到取卡规则
'jbd_action_type':1,                #加班单作用方式
'OTCheckRecType':2,               #加班状态
'OutCheckRecType':3,
'OutOverTime' :1,                 #下班后记加班
'TwoDay' : '0',
'WorkMonthStartDay' : 1,
'WorkWeekStartDay' : 0,
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

def SaveAttRule(AttRules):
    global AttRule
    if AttRule=={}:
        AttRule=LoadAttRule()
    changeflag=0
    k=AttRule.keys()
    for t in k:
        if not t in AttRules:
            AttRule[t]=0
        elif AttRules[t]=='on':
            if AttRule[t]!=1:
                changeflag=1
            AttRule[t]=1
        elif t not in AttRuleStrKeys:
            if AttRule[t]!=int(AttRules[t]):
                changeflag=1
            AttRule[t]=int(AttRules[t])
        else:
            AttRule[t]=AttRules[t]
        if t!='LeaveClass':
            SaveAttOptions(t,AttRule[t])
    if changeflag:
        deleteCalcLog(Type=0)
def SaveAttOptions(paraName, paraValue):
    from mysite.att.models import AttParam
    ap=AttParam.objects.filter(ParaName=paraName)
    if ap:
        ap=ap[0]
        if u"%s"%ap.ParaValue!=u"%s"%paraValue:
            ap.ParaValue=paraValue
            ap.save()
    else:
        att=AttParam(ParaName=paraName,ParaValue=paraValue)
        att.save()

#编辑时才会运行此函数
def SaveLeaveClass(lClasses,type=0):
    from mysite.att.models import LeaveClass1
    from mysite.att.models import LeaveClass
    from mysite.iclock.sql import SaveLeaveClass_sql
    if type==0:
        lc = LoadCalcItems()
    else:
        lc=GetLeaveClasses(1)
#    print "()()()()()() ",lc
    changeflag=0
    for t in lClasses:
        del t['IsLeave']
#        del t['LeaveName']
        tt=t.copy()
        if changeflag!=1:
            changeflag=isChangedLeaveClass(tt,lc)
        if changeflag==0:continue
        del tt['LeaveId']
#        s=",".join(["%s='%s'" % (k, v) for k, v in tt.items()])
        s=",".join(["%s=%s" % (k, '%s') for k, v in tt.items()])
#        print "sssss ",s
        params=[]
        for k, v in tt.items():
            params.append(v)
        dbTable=LeaveClass1._meta.db_table
        if type==1:
            dbTable=LeaveClass._meta.db_table
        #sqlstr="update %s set %s where LeaveId='%s'"%(dbTable, s,t['LeaveId'])
        sqlstr=SaveLeaveClass_sql(dbTable, s,t['LeaveId'])
        customSqlEx(sqlstr,params)
    if changeflag==1:
        deleteCalcLog(Type=0)
    
def isChangedLeaveClass(newClass,oldClass):
    id=newClass['LeaveId']
    for t in oldClass:
        if t['LeaveId']==id:
            for k,v in newClass.items():
                if t[k]!=v:
#                    print t[k],v
                    return 1
    return 0            

def GetUserSchId(userid,dt):
    from mysite.att.models import USER_OF_RUN
    global qry_user_of_run
    if qry_user_of_run==None:
        qry_user_of_run=USER_OF_RUN.objects.filter(UserID=userid).order_by('-StartDate')
        len(qry_user_of_run)
    l=[]
    result=0
    for att in qry_user_of_run:
        att.EndDate=checkTime(att.EndDate)
        att.StartDate=checkTime(att.StartDate)
        if att.EndDate<dt:
            break
        elif att.StartDate<=dt and att.EndDate>=dt:
            result=att.NUM_OF_RUN_ID_id
    return result


def GetSchClasses():
    from mysite.att.models import SchClass
    global schClass
    global schClasses
    global AttRule
    AttRule=LoadAttRule()
    #if schClass==None:
    schClass=SchClass.objects.all().order_by('SchclassID')
    #else:
    #    return schClasses
    ss={}
    re=[]
    for sch in schClass:
        sch.StartTime=checkTime(sch.StartTime)
        sch.EndTime=checkTime(sch.EndTime)
        if sch.CheckInTime1!=None:
            sch.CheckInTime1=checkTime(sch.CheckInTime1)
        if sch.CheckInTime2!=None:
            sch.CheckInTime2=checkTime(sch.CheckInTime2)
        if sch.CheckOutTime1!=None:
            sch.CheckOutTime1=checkTime(sch.CheckOutTime1)
        if sch.CheckOutTime2!=None:
            sch.CheckOutTime2=checkTime(sch.CheckOutTime2)
            
        ss={'TimeZone':{'StartTime':sch.StartTime,'EndTime':sch.EndTime},
            'schClassID':sch.SchclassID,
            'SchName':sch.SchName,
            'MustClockIn':sch.CheckIn,
            'MustClockOut':sch.CheckOut,
            'MinsLate':sch.LateMinutes,
            'MinsEarly':sch.EarlyMinutes,
            'Color':sch.Color,
            'WorkDay':1,
            'WorkMins':0,               #sch.WorkMins,\                          #not used
            'OverTime':0,
            'Intime':{'StartTime':sch.CheckInTime1,'EndTime':sch.CheckInTime2},
            'Outtime':{'StartTime':sch.CheckOutTime1,'EndTime':sch.CheckOutTime2},
            'SchID':sch.SchclassID,
            'IsCalcRest':0,
            'StartRestTime':checkTime(datetime.time(0,0,0)),
            'EndRestTime':checkTime(datetime.time(0,0,0,)),
            'StartRestTime1':checkTime(datetime.time(0,0,0)),
            'EndRestTime1':checkTime(datetime.time(0,0,0,)),
            'RestTime':0,
        }
        
        if sch.CheckIn==1:
            ss['MustClockIn']=1
        else:
            ss['MustClockIn']=0
        if sch.CheckOut==1:
            ss['MustClockOut']=1
        else:
            ss['MustClockOut']=0
        if sch.LateMinutes!=None:
            ss['MinsLate']=sch.LateMinutes
        else:
            ss['MinsLate']=AttRule['MinsLate']
        if sch.EarlyMinutes!=None:
            ss['MinsEarly']=sch.EarlyMinutes
        else:
            ss['MinsEarly']=AttRule['MinsEarly']
            
        if sch.Color!=None:
            ss['Color']=sch.Color
        else:
            ss['Color']=16715535
        try:        
            if sch.IsCalcRest!=None:
                ss['IsCalcRest']=sch.IsCalcRest
                
            if ss['IsCalcRest']==1:    
                if sch.StartRestTime!=None:                              #add 2009.08.05
                    sch.StartRestTime=checkTime(sch.StartRestTime)
                if sch.EndRestTime!=None:
                    sch.EndRestTime=checkTime(sch.EndRestTime)
                try:
                    if sch.StartRestTime1!=None:                              
                        sch.StartRestTime1=checkTime(sch.StartRestTime1)
                        ss['StartRestTime1']=sch.StartRestTime1

                    if sch.EndRestTime1!=None:
                        sch.EndRestTime1=checkTime(sch.EndRestTime1)
                        ss['EndRestTime1']=sch.EndRestTime1
                        
                except:
                    pass
                
                if sch.StartRestTime!=None:
                    ss['StartRestTime']=sch.StartRestTime
                if sch.EndRestTime!=None:
                    ss['EndRestTime']=sch.EndRestTime
                if (sch.StartRestTime==checkTime(datetime.time(0,0,0))) and (sch.EndRestTime==checkTime(datetime.time(0,0,0))):
                    ss['IsCalcRest']=0    
            
        except:
            pass
        
        if ss['TimeZone']['EndTime']<ss['TimeZone']['StartTime']:
#            if AttRule['TwoDay']==1:
#                ss['TimeZone']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(days=1)
#            else:
            ss['TimeZone']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(days=1)
        
        if sch.WorkDay!=None:
            ss['WorkDay']=sch.WorkDay
            
        
        if sch.CheckInTime1!=None:
            ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-sch.StartTime+sch.CheckInTime1
        else:
            ss['Intime']['StartTime']=ss['TimeZone']['StartTime']-datetime.timedelta(hours=2)
        if sch.CheckInTime2!=None:
            ss['Intime']['EndTime']=ss['TimeZone']['StartTime']-sch.StartTime+sch.CheckInTime2
        else:
            ss['Intime']['EndTime']=ss['TimeZone']['StartTime']+(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
        if sch.CheckOutTime1!=None:
            ss['Outtime']['StartTime']=ss['TimeZone']['EndTime']-sch.EndTime+sch.CheckOutTime1
            if ss['Outtime']['StartTime']>ss['TimeZone']['EndTime']:
                ss['Outtime']['StartTime']=ss['Outtime']['StartTime']-datetime.timedelta(days=1)
        else:
            ss['Outtime']['StartTime']=ss['TimeZone']['EndTime']-(ss['TimeZone']['EndTime']-ss['TimeZone']['StartTime'])/2
        if sch.CheckOutTime2!=None:
            ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']-sch.EndTime+sch.CheckOutTime2
        else:
            ss['Outtime']['EndTime']=ss['TimeZone']['EndTime']+datetime.timedelta(hours=6)
        
        t=ss.copy()
        re.append(t)
    schClasses=re
    return re

def FindSchClassByID(SchId):
    global schClasses
    global schClass
    if schClass==None:
        GetSchClasses()
    for i in range(len( schClasses)):
        if schClasses[i]['schClassID']==SchId:
            return i
    return -1

def GetSchClassByID(SchId,  StartTime, EndTime):
    schi=FindSchClassByID(SchId)
    global schClasses
    global AttRule
    if schi==-1:
        #print "schid=%s not found"%(SchId)    #should throw exceptino
        return {}
    d=trunc(StartTime)
#    if AttRule['TwoDay']==1:
#        d=trunc(EndTime)
        
#    result=schClasses[schi].copy()
    result=copy.deepcopy(schClasses[schi])
    
    d2=result['TimeZone']['StartTime']
    d=d-datetime.datetime(d2.year,d2.month,d2.day)
    result['TimeZone']['StartTime']=result['TimeZone']['StartTime']+d
    result['TimeZone']['EndTime']=result['TimeZone']['EndTime']+d
    if result['TimeZone']['EndTime']<=result['TimeZone']['StartTime']:
        result['TimeZone']['EndTime']=result['TimeZone']['EndTime']+datetime.timedelta(days=1)
    result['Intime']['StartTime']=result['Intime']['StartTime']+d
    result['Intime']['EndTime']=result['Intime']['EndTime']+d
    if result['Intime']['StartTime']>result['TimeZone']['StartTime']:
        result['Intime']['StartTime']=result['Intime']['StartTime']-datetime.timedelta(days=1)
    if result['Intime']['EndTime']<=result['Intime']['StartTime']:
        result['Intime']['EndTime']=result['Intime']['EndTime']+datetime.timedelta(days=1)
    result['Outtime']['StartTime']=result['Outtime']['StartTime']+d
    result['Outtime']['EndTime']=result['Outtime']['EndTime']+d
    if result['IsCalcRest']==1:
        result['StartRestTime']=result['StartRestTime']+d
        result['EndRestTime']=result['EndRestTime']+d
        if result['EndRestTime']<=result['StartRestTime']:
            result['EndRestTime']=result['EndRestTime']+datetime.timedelta(days=1)
        if result['StartRestTime']<result['TimeZone']['StartTime']:
            result['StartRestTime']=result['StartRestTime']+datetime.timedelta(days=1)
        if result['StartRestTime']+datetime.timedelta(days=1)<result['TimeZone']['StartTime']:
            result['StartRestTime']=result['StartRestTime']+datetime.timedelta(days=1)
        if result['EndRestTime']+datetime.timedelta(days=1)<result['TimeZone']['EndTime']:
            result['EndRestTime']=result['EndRestTime']+datetime.timedelta(days=1)
        if result['EndRestTime']<result['TimeZone']['StartTime'] or result['StartRestTime']<result['TimeZone']['StartTime'] or result['StartRestTime']>result['TimeZone']['EndTime'] or result['EndRestTime']>result['TimeZone']['EndTime']:
            result['IsCalcRest']=0

        result['StartRestTime1']=result['StartRestTime1']+d
        result['EndRestTime1']=result['EndRestTime1']+d
        if result['EndRestTime1']<=result['StartRestTime1']:
            result['EndRestTime1']=result['EndRestTime1']+datetime.timedelta(days=1)
        if result['StartRestTime1']<result['TimeZone']['StartTime']:
            result['StartRestTime1']=result['StartRestTime1']+datetime.timedelta(days=1)
        if result['StartRestTime1']+datetime.timedelta(days=1)<result['TimeZone']['StartTime']:
            result['StartRestTime1']=result['StartRestTime1']+datetime.timedelta(days=1)
        if result['EndRestTime1']+datetime.timedelta(days=1)<result['TimeZone']['EndTime']:
            result['EndRestTime1']=result['EndRestTime1']+datetime.timedelta(days=1)
            
            
    if result['Outtime']['EndTime']<=result['Outtime']['StartTime']:
        result['Outtime']['EndTime']=result['Outtime']['EndTime']+datetime.timedelta(days=1)
        
    t=result['TimeZone']['EndTime']-result['TimeZone']['StartTime']
    if result['IsCalcRest']==1:
        rtm=(result['EndRestTime']-result['StartRestTime'])+(result['EndRestTime1']-result['StartRestTime1'])
        t=t-rtm
        result['RestTime']=rtm.days*24*60+rtm.seconds/60
    result['WorkMins']= t.days*24*60+t.seconds/60
    return result

def  AddScheduleShift(shifts,StartTime, EndTime, SchClassID ,OverTime):
    l=len(shifts)
    i=l-1
    result=l
    while i>=0:
        if shifts[i]['TimeZone']['StartTime']>EndTime:
            result=i
            i=i-1
        else:
            break
    ss=GetSchClassByID(SchClassID,StartTime,EndTime)
    if ss!={}:
        ss['OverTime']=OverTime
        shifts.insert(result,ss)
    return shifts

def IsHoliday(d):
    from mysite.att.models import Holiday as holidays
    #global tHoliday
    Result=[]
    
    cch=holidays.objects.all().order_by('start_time')
    #print "tHoliday:%s"%cch
    if not cch:
        return []
    try:
        for t in cch:
            #StDate=checkTime(t.start_time)
            if t.IsCycle==1:
                StDate=datetime.date(datetime.datetime.now().year,t.month,t.day)
            else:
                StDate=t.start_time         
            if type(d)==datetime.datetime:
                d=d.date()
            if StDate<=d:
                dur=t.duration
                if dur<1:
                    dur=1
                if dur<180:
                    dur=dur*(24*60)
                if (d-StDate).days*24*60<dur-1:
                    Result=['htCommHoliday']
                    break
        datetime.datetime.isoweekday
        if (d.isoweekday() / 6)>=1:
            Result.append('htWeekend')
    except:
        import traceback;traceback.print_exc()
    return Result

#获取正常排班时间表
def GetWorkTime(schid,d,HolSTime=datetime.datetime(2000,1,1,0,0),HolETime=datetime.datetime(2000,1,1,0,0)):
    from mysite.att.models import NUM_RUN_DEIL
    Result=[]
    global Schedules
    global AttRule
    t_sch=None
    for sch in Schedules:
        if sch.Num_runID==schid:
            t_sch=sch
            break
    if t_sch==None:
        return Result
#    units=('suDay','suWeek','suMonth')
    SchStartDate=checkTime(t_sch.StartDate)
    i=t_sch.Units
    if i==suWeek:
        j=t_sch.Cycle
        j=((d-(SchStartDate-datetime.timedelta(days=SchStartDate.isoweekday()+1))).days+6-int(AttRule['WorkWeekStartDay'])) %(7*j)+int(AttRule['WorkWeekStartDay'])
    elif i==suMonth:
        j=t_sch.Cycle
        j=((d.year-SchStartDate.year)*12+(d.month-SchStartDate.month)) % j
        j=j*31+d.day-1
    else:
        j=t_sch.Cycle
        j=(d-SchStartDate).days % j
    global SchDetail
    SchDetail=NUM_RUN_DEIL.objects.filter(Num_runID=int(schid)).order_by('Num_runID', 'Sdays', 'StartTime')
    len(SchDetail)
    for sDetail in SchDetail:
        sDetail.StartTime=checkTime(sDetail.StartTime)
        sDetail.EndtTime=checkTime(sDetail.EndTime)

        st=None
        et=None
        if sDetail.Sdays==j:
            st=datetime.datetime(d.year,d.month,d.day,sDetail.StartTime.hour,sDetail.StartTime.minute,sDetail.StartTime.second)
            et=datetime.datetime(d.year,d.month,d.day,sDetail.EndTime.hour,sDetail.EndTime.minute,sDetail.EndTime.second)+\
              datetime.timedelta(days=sDetail.Edays-sDetail.Sdays)
        if st!=None and st>=HolSTime and et<=HolETime:
            st=None
            et=None
        elif st!=None and (st>=HolSTime) and (et<=HolETime):
            st=HolETime
        elif st!=None and (et>=HolSTime) and (et<=HolETime):
            et=HolSTime
        if st<>None:
            Result=AddScheduleShift(Result,st,et,sDetail.SchclassID_id,sDetail.OverTime)
    return Result

#获取员工的上下班时间表及相关设置
def GetUserScheduler(userid, d1, d2, HasHoliday):
    from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH,Holiday as holidays
    global qry_user_of_run
    global Schedules
    global SchDetail
    global qrytempsch
    global schClass
    global schClasses
    global tHoliday
    global AttRule
    d1=datetime.datetime(d1.year,d1.month,d1.day,0,0,0,0)
    d2=datetime.datetime(d2.year,d2.month,d2.day,0,0,0,0)
    if Schedules==None:
        Schedules=NUM_RUN.objects.all().order_by('Num_runID')
        #len(Schedules)
#    if SchDetail==None:
#        SchDetail=NUM_RUN_DEIL.objects.all().order_by('Num_runID', 'Sdays', 'StartTime')
    qry_user_of_run=USER_OF_RUN.objects.filter(UserID=userid).order_by('-StartDate')
    qrytempsch=USER_TEMP_SCH.objects.filter(UserID=userid,ComeTime__gt=d1-datetime.timedelta(days=2),LeaveTime__lt=d2+datetime.timedelta(days=2)).order_by('ComeTime')
    if tHoliday==None:
        tHoliday=holidays.objects.all().order_by('start_time')
    GetSchClasses()
#    AttRule=LoadAttRule()
    j=0
    #if settings.DATABASE_ENGINE == 'ado_mssql':
    l_tempsch=len(qrytempsch)
    l_run=len(qry_user_of_run)
    #for t in qrytempsch:
        #j+=1
        #if j>1:
            #break

    d=d1
    i=0
    kml=0
    rt=[]
    while d<=d2:
        dts=datetime.datetime(d.year,d.month,d.day,0,0,0,0)
        bTempSch=False
        kml = 0
        shifts=[]
        if l_tempsch > 0 and i<l_tempsch:
            if checkTime(qrytempsch[i].ComeTime) >= dts:
                while (i>1) and (checkTime(qrytempsch[i].ComeTime) >= dts):
                    i=i-1
            else:
                while (i< l_tempsch) and (checkTime(qrytempsch[i].ComeTime) < dts):
                    i=i+1
            if i<l_tempsch and (checkTime(qrytempsch[i].ComeTime) < dts):
                i=i+1
            if i<l_tempsch and (checkTime(qrytempsch[i].ComeTime) >= dts) and \
               (checkTime(qrytempsch[i].ComeTime) < dts + datetime.timedelta(days=1)):
                bTempSch = True
        while bTempSch and i< l_tempsch:
            kml=kml+1
            t=checkTime(qrytempsch[i].LeaveTime)-checkTime(qrytempsch[i].ComeTime)
            if (t.days*24*60+t.seconds/60)>=int(AttRule['MinShiftInterval']):
                shifts=AddScheduleShift(shifts, checkTime(qrytempsch[i].ComeTime),\
                            checkTime(qrytempsch[i].LeaveTime),\
                            qrytempsch[i].SchclassID,\
                            qrytempsch[i].OverTime)
            i=i+1
            bTempSch = (i< l_tempsch) and (qrytempsch[i].ComeTime >= dts) and \
                 (qrytempsch[i].ComeTime < dts + datetime.timedelta(days=1))

        if kml==0:
            hol=HasHoliday
            
            if hol:
                hol='htCommHoliday' in IsHoliday(d)
            if not hol:
                shifts=[]
                schid=GetUserSchId(userid,d)
                if schid>0:
                    shifts=GetWorkTime(schid,d)

        for sh in shifts:
            if sh['TimeZone']['StartTime']<sh['TimeZone']['EndTime']-datetime.timedelta(seconds=1):
                rt.append(copy.deepcopy(sh))

        d=d+datetime.timedelta(days=1)
    return rt

#-------------------------------------------------------------------------------------
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

def LoadSchPlanEx(userid,LoadAutoIds, LoadSchArray,LoadPlan=True):
    global UserSchPlan
    UserSchPlan=LoadSchPlan(userid,LoadAutoIds, LoadSchArray,LoadPlan)
    return UserSchPlan
        

def FetchLeaveClass(dataobj,type=0):
    
    Result={}
    Result['LeaveId']=int(dataobj.LeaveID)
    if type==1:
        #d=force_unicode(LeaName[dataobj.LeaveID], strings_only=True)
        Result['LeaveName']=transLeaName(dataobj.LeaveID)
    else:
        Result['LeaveName']=dataobj.LeaveName
    Result['MinUnit']=float(dataobj.MinUnit)
    Result['RemaindProc']=int(dataobj.RemaindProc)              #舍入控制0,1,2
    if dataobj.Unit==-1:
        Result['Unit']=1
    else:
        Result['Unit']=int(dataobj.Unit)
    Result['RemaindCount']=int(dataobj.RemaindCount)       #累计后进行舍入
    Result['ReportSymbol']=dataobj.ReportSymbol
    Result['Color']=int(dataobj.Color)
    Result['Classify']=int(dataobj.Classify)
    if dataobj.LeaveType:
        Result['LeaveType']=int(dataobj.LeaveType)
    else:
        Result['LeaveType']=0
    if type==0:
        if dataobj.clearance:
            Result['clearance']=int(dataobj.clearance)
        else:
            Result['clearance']=0
        
    Result['IsLeave']=0
    if dataobj.LeaveID!=999:
        Result['IsLeave']=1
        if dataobj.Classify!='null':
            if (dataobj.Classify & 0x80)!=0:
                Result['IsLeave']=0
    
    return Result


def LoadCalcItems():
    from mysite.att.models.model_leaveclass1 import LeaveClass1
    from mysite.att.models.model_leaveclass import LeaveClass
    
    global qryLeaveClass1
    #if qryLeaveClass1==None:
    qryLeaveClass1=LeaveClass1.objects.all().order_by('LeaveID')
    Result=[]
    for t in qryLeaveClass1:
        if t.LeaveID in AttAbnomiteRptIDs:
            r=FetchLeaveClass(t,1)
            if len(r)>0:
                Result.append(r)
    #print "Result:%s"%Result
    return Result

#获取假类参数,type!=0时仅获取假类参数
def GetLeaveClasses(type=0):
    from mysite.att.models.model_leaveclass1 import LeaveClass1
    from mysite.att.models.model_leaveclass import LeaveClass
    
    Result=[]
#    global AttAbnomiteRptItems

    if (type ==0):
        qryLeaveClass1=LeaveClass1.objects.all().order_by('LeaveID')
        for t in qryLeaveClass1:
            if t.LeaveID in AttAbnomiteRptIDs:
                r=FetchLeaveClass(t,1)
                if len(r)>0:
                    Result.append(r)
    qryLeaveClass=LeaveClass.objects.all().order_by('LeaveID')
    for t in qryLeaveClass:
        r=FetchLeaveClass(t)
        if len(r)>0:
            Result.append(r)
#    AttAbnomiteRptItems=Result
    return Result

def InitData():
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
def LeaveIDToIndex(id):
    result =-1
    if id=='null':
        return result
    global ExceptionIDs
    GetExceptionIDS()
    for i in ExceptionIDs:
        result=result+1
        if id==i:
            return result
    return -1


def GetExceptionText(ExceptionID):
    global LClasses1
    if LClasses1==[]:
        LClasses1=GetLeaveClasses(1)
    ExceptionIndex=LeaveIDToIndex(int(ExceptionID))
    result=''
    if ExceptionIndex<4 and ExceptionIndex>-1:
        result=ExceptionName[ExceptionIndex]
    elif ExceptionIndex<len(LClasses1)+4 and ExceptionIndex>3:
        result=LClasses1[ExceptionIndex-4]['LeaveName']
    else:
        result=str(ExceptionID)
    return result

def CalcAttExcTimeLong(dDict):
    global WorkTimeZone
    global AttRule
    global StartDate
    global EndDate
    global rmdattexception
    global rmdattexceptionEx
    AttRule=LoadAttRule()
    d=dDict['StartTime']
    #qryAudit.First;
    #while not qryAudit.eof do
    #begin
    #d2 := qryAudit.fieldbyname('CheckTime').AsDateTime;
    #if abs(d-d2)<OneSecond then
    #begin
        #if qryAudit['IsLeave']=True then
        #rmdattexception['OldAuditExcID']:=LeaveIDToIndex(qryaudit['NewExcID'])
        #else
        #rmdattexception['OldAuditExcID']:=qryaudit['NewExcID'];
        #rmdattexception['AuditExcID']:=rmdattexception['OldAuditExcID'];
        #break;
    #end;
    #qryAudit.Next;
    #end;
    d2 = dDict['EndTime']
    if d2.second==59:
        d2=d2+datetime.timedelta(seconds=1)
    dDict['TimeLong'] = diffTime(d2-d)/60
    dDict['InScopeTime']=0
    rmdattexceptionEx=[]
    if d2>d:
        ot=0
        owd=0
        owdt=0
        i=-1
        c=0
        dictEx=dDict.copy()
        for ttt in WorkTimeZone:
            i=i+1
            if d<=ttt['TimeZone']['StartTime']:
                if d2>=ttt['TimeZone']['EndTime']:
                    dictEx['SchId']=ttt['SchID']
#                    if ttt['WorkMins']!=None and ttt['WorkMins']>0:
#                        c=ttt['WorkMins']
#                    else:
                    c=diffTime(ttt['TimeZone']['EndTime']-ttt['TimeZone']['StartTime'])/60
                    rt=SumRestTime(d,d2,ttt['StartRestTime'],ttt['EndRestTime'],ttt['StartRestTime1'],ttt['EndRestTime1'],1)
                    c=c-rt
                    dictEx['StartTime']=ttt['TimeZone']['StartTime']
                    dictEx['EndTime']=ttt['TimeZone']['EndTime']
                    dictEx['SchIndex']=i
                    dictEx['InScopeTime']=c
                    dictEx['clearance']=dDict['clearance']
                    d=trunc(ttt['TimeZone']['StartTime'])
                    if AttRule['TwoDay']==1 and trunc(ttt['TimeZone']['EndTime'])>d :
                        d=d+datetime.timedelta(days=1)
                    dictEx['AttDate']=d
                    rmdattexceptionEx.append(dictEx.copy())
                elif d2>ttt['TimeZone']['StartTime'] and d2<=ttt['TimeZone']['EndTime']:
                    dictEx['SchId']=ttt['SchID']
                    c=diffTime(d2-ttt['TimeZone']['StartTime'])/60
                    rt=SumRestTime(d,d2,ttt['StartRestTime'],ttt['EndRestTime'],ttt['StartRestTime1'],ttt['EndRestTime1'],1)
                    c=c-rt
                    dictEx['StartTime']=ttt['TimeZone']['StartTime']
                    dictEx['EndTime']=d2
                    dictEx['SchIndex']=i
                    dictEx['InScopeTime']=c
                    dictEx['clearance']=dDict['clearance']
                    d=trunc(ttt['TimeZone']['StartTime'])
                    if AttRule['TwoDay']==1 and trunc(ttt['TimeZone']['EndTime'])>d :
                        d=d+datetime.timedelta(days=1)
                    dictEx['AttDate']=d
                    rmdattexceptionEx.append(dictEx.copy())
                
            elif d<=ttt['TimeZone']['EndTime']:
                if d2>=ttt['TimeZone']['EndTime']:
                    c=diffTime(ttt['TimeZone']['EndTime']-d)/60
                    rt=SumRestTime(d,ttt['TimeZone']['EndTime'],ttt['StartRestTime'],ttt['EndRestTime'],ttt['StartRestTime1'],ttt['EndRestTime1'],1)
                    c=c-rt
                    dictEx['StartTime']=d
                    dictEx['EndTime']=ttt['TimeZone']['EndTime']

                else:
                    c=diffTime(d2-d)/60
                    rt=SumRestTime(d,d2,ttt['StartRestTime'],ttt['EndRestTime'],ttt['StartRestTime1'],ttt['EndRestTime1'],1)
                    c=c-rt
                    dictEx['StartTime']=d
                    dictEx['EndTime']=d2
                    
                d=trunc(ttt['TimeZone']['StartTime'])
                if AttRule['TwoDay']==1 and trunc(ttt['TimeZone']['EndTime'])>d :
                    d=d+datetime.timedelta(days=1)
                dictEx['AttDate']=d
                dictEx['SchId']=ttt['SchID']
                dictEx['clearance']=dDict['clearance']
                dictEx['SchIndex']=i
                dictEx['InScopeTime']=c
                rmdattexceptionEx.append(dictEx.copy())
                    
        if (dDict['InScopeTime']==0) and (dDict['ExceptionID'] in (caeFreeOT,caeOT)) :
            dDict['InScopeTime']=diffTime(d2-d)/60

    if rmdattexceptionEx:
        for t in rmdattexceptionEx:
            rmdattexception.append(t)
    else:
        if AttRule['MinsWorkDay1']==None or AttRule['MinsWorkDay1']==0:
            AttRule['MinsWorkDay1']=AttRule['MinsWorkDay']
        dDict['MinsWorkDay']=AttRule['MinsWorkDay1']
        d=trunc(dDict['StartTime'])
        if AttRule['TwoDay']==1 and trunc(dDict['EndTime'])>d and (dDict['ExceptionID'] in (caeFreeOT,caeOT)):
            d=d+datetime.timedelta(days=1)
        dDict['AttDate']=d
        rmdattexception.append(dDict)
def LoadUserException(userid,st,et):
    from mysite.att.models import AttException
    global ExcepData
    global rmdattexception
    rmdattexception=[]
    global ExceptionIDs
    atte={}
    fflag=False
    #field_names = [f.column for f in AttException._meta.fields if not isinstance(f, AutoField)]
    if FieldIsExist('UserSpedayID',AttException):
        fflag=True
    userspedid=0
    for t in ExcepData:
        t.start=checkTime(t.start)
        t.end=checkTime(t.end)
        if st>=t.end:continue
        if et<t.start-datetime.timedelta(days=1):break
        st1=t.start
        et1=t.end#-datetime.timedelta(seconds=1)
        if et1<=st1:continue
        if fflag:
            userspedid=t.id
        if t.leaveclass.pk>0 and int(t.state)==2 and t.leaveclass.pk in ExceptionIDs:
            while st1<et1:#按天拆分
                st11=st1
                if st11.year==et1.year and st11.month==et1.month and st11.day==et1.day:
                    st1=st1+datetime.timedelta(days=1)
                    et11=et1
                else:
                    et11=datetime.datetime(st11.year,st11.month,st11.day,23,59,59)
                    x=st1+datetime.timedelta(days=1)
                    st1=datetime.datetime(x.year,x.month,x.day,0,0,0)
                if et11>et+datetime.timedelta(days=1):
                    break
                if st1<st:continue
                if st11>=st:
                    tempexcept={'UserID':t.emp_id,'StartTime':st11,'EndTime':et11,
                                'ExceptionID':t.leaveclass.pk,'InScopeTime':0,'TimeLong':0,'OverlapTime':0,
                                'OverLapWorkDay':0,'OverlapWorkDayTail':0,'SchIndex':-1,'clearance':0,'UserSpedayID':userspedid}
                    CalcAttExcTimeLong(tempexcept)#计算一天的有效时长
def FetchClTData(dDict):
    global CheckInOutData
    global CheckInOutRecorNo
    #print "CheckInOutData:%s"%CheckInOutData
    dDict['CheckTime']=CheckInOutData[CheckInOutRecorNo].TTime
    dDict['CheckType']=CheckInOutData[CheckInOutRecorNo].State
    try:
        #if hasattr(CheckInOutData[CheckInOutRecorNo].SN,'SN'):
            #dDict['SN']=CheckInOutData[CheckInOutRecorNo].SN.SN
        #else:
        dDict['SN']=CheckInOutData[CheckInOutRecorNo].SN_id    
        dDict['VerifyCode']=CheckInOutData[CheckInOutRecorNo].Verify
    except:
        dDict['SN']=''
        dDict['VerifyCode']=1
    dDict['RecordConfirmed']=False
    dDict['TypeConfirmed']=True
def GetFirstClockInOut():
    global CheckInOutData
    global l_CheckInOutData
    global ClTA
    global CheckInOutRecorNo
    global MaxDate
    global MinDate
    ClTA[0]['CheckTime']=MinDate
    ClTA[1]['CheckTime']=MinDate
    ClTA[2]['CheckTime']= MaxDate
    CheckInOutRecorNo=0
    if l_CheckInOutData>0:
        FetchClTData(ClTA[1])
        CheckInOutRecorNo+=1
        if CheckInOutRecorNo<l_CheckInOutData:
            FetchClTData(ClTA[2])
            CheckInOutRecorNo+=1
        if CheckInOutRecorNo<l_CheckInOutData:
            FetchClTData(ClTA[3])
        else:
            ClTA[3]['CheckTime']= MaxDate

        return True
    else:
        return False

def GetNextClockInOut(CurIsInvalid=False,IsAutoSch=False):
    global MaxDate
    global CheckInOutRecorNo
    global CheckInOutData
    global l_CheckInOutData
    global ClTA
    #print "MaxDate:%s"%MaxDate
    if CurIsInvalid==False:
        ClTA[0]=ClTA[1].copy()
    if IsAutoSch:
        pass
    else:
        ClTA[1]=ClTA[2].copy()

    Result=ClTA[2]['CheckTime']<MaxDate
    if Result:
        ClTA[2]=ClTA[3].copy()
        if ClTA[3]['CheckTime']!=MaxDate:
            CheckInOutRecorNo+=1
            if CheckInOutRecorNo<l_CheckInOutData:
                FetchClTData(ClTA[3])
            else:
                ClTA[3]['CheckTime']=MaxDate
    return Result


def FetchChPData(dDict):
    global WorkTimeZone
    global WorkTimeIndex
    global WorkTimeIn
    t=WorkTimeZone[WorkTimeIndex]
    if WorkTimeIn:
        dDict['CCTime'] = t['TimeZone']['StartTime']
        dDict['CCStart'] = t['Intime']['StartTime']
        dDict['CCEnd'] = t['Intime']['EndTime']
        dDict['CCState'] = 'I'
        dDict['InState'] = True
        dDict['OutState'] = False
        dDict['CCMust'] = t['MustClockIn']
        dDict['CCAuto'] = False
    else:
        dDict['CCTime'] = t['TimeZone']['EndTime']
        dDict['CCStart'] = t['Outtime']['StartTime']
        dDict['CCEnd'] = t['Outtime']['EndTime']

        if dDict['CCEnd'] > (dDict['CCTime'] +datetime.timedelta(days=1)):
            dDict['CCEnd'] = dDict['CCEnd'] -datetime.timedelta(days=1)
        if dDict['CCStart'] >dDict['CCTime']:
            dDict['CCStart'] = dDict['CCStart'] -datetime.timedelta(days=1)
        dDict['CCState'] = 'O'
        dDict['InState'] = False
        dDict['OutState'] = True
        dDict['CCMust'] = t['MustClockOut']
        dDict['CCAuto'] = False;
    dDict['Index']= WorkTimeIndex
    WorkTimeIn = not WorkTimeIn
    if WorkTimeIn:
        WorkTimeIndex+=1



def GetFirstCheckPoint():
    global ExceptDataIn
    global WorkTimeIn
    global WorkTimeIndex
    global WorkTimeZone
    global ChPA
    ExceptDataIn=True
    WorkTimeIn=True
    WorkTimeIndex = 0
    ChPA[0]['CCTime']= MinDate
    ChPA[0]['CCStart'] = MinDate
    ChPA[0]['CCEnd']= MinDate
    ChPA[0]['OutState']= True
    ChPA[0]['InState'] = False
    ChPA[0]['CCState']= 'O'
    ChPA[0]['CCMust'] = False
    ChPA[0]['Index'] = -2

    ChPA[2]['CCTime']= MaxDate
    ChPA[2]['CCStart'] = MaxDate
    ChPA[2]['CCEnd']= MaxDate
    ChPA[2]['CCState'] = 'I'
    ChPA[2]['InState']= True
    ChPA[2]['OutState']= False
    ChPA[2]['CCMust'] = False
    ChPA[2]['Index'] = -1

    ChPA[1] = ChPA[2].copy()
    #print "WorkTimeZone:%s"%WorkTimeZone
    if len(WorkTimeZone) > 0:
        FetchChPData(ChPA[1]);
        FetchChPData(ChPA[2]);
        if ChPA[1]['CCEnd'] > ChPA[2]['CCTime']:
            ChPA[1]['CCEnd']= ChPA[2]['CCTime'] - datetime.timedelta(seconds=1)
        Result = True
    else:
        Result = False

    return Result

def GetNextCheckPoint():
    ChPA[0]= ChPA[1].copy()
    ChPA[1]= ChPA[2].copy()
    Result = ChPA[2]['CCTime'] < MaxDate
    if Result:
        if WorkTimeIn and (WorkTimeIndex >= len(WorkTimeZone)):
            ChPA[2]['CCTime'] = MaxDate
            ChPA[2]['CCStart']= MaxDate
            ChPA[2]['CCEnd'] = MaxDate
            ChPA[2]['CCState'] = 'I'
            ChPA[2]['InState']= True
            ChPA[2]['OutState']= False
            ChPA[2]['CCMust']= False
            ChPA[2]['Index'] = -1
        else:
            FetchChPData(ChPA[2])
        if ChPA[1]['CCEnd'] > ChPA[2]['CCTime']:
            ChPA[1]['CCEnd']= ChPA[2]['CCTime'] - datetime.timedelta(seconds=1)
    return Result


def GetDefaultSpecialIntervals():
    global SpecialIntervals
    SpecialIntervals=[]
    if AttRule['OTCheckRecType']!=otcIgnore:
        SpecialIntervals.append({
            'StartTag':CCheckInTag[csOverTime][1],
            'EndTag' : CCheckInTag[csOverTime][0],
            'InShift': False,
            'CancelInTag' : False,
            'CancelOutTag' : False,
            'MinInterval': 0,
            'MaxInterval' : AttRule['MaxShiftInterval'],
            'AllowSplit' : True,
            'Name' : CCheckName[csOverTime],
            'RecAbnormite' : raOT,
            'AttExceptionId' : caeFreeOT})
        if AttRule['OTCheckRecType']==otcOT:
            SpecialIntervals[len(SpecialIntervals)-1]['AttExceptionId'] =caeOT


    if AttRule['OutCheckRecType']!=ocIgnore:
        SpecialIntervals.append({
            'StartTag':CCheckInTag[csShiftOut][0],
            'EndTag' : CCheckInTag[csShiftOut][1],
            'InShift': True,
            'CancelInTag' : True,
            'CancelOutTag' : True,
            'MinInterval': 0,
            'MaxInterval' : AttRule['MaxShiftInterval'], #单位分钟
            'AllowSplit' : False,
            'Name' : CCheckName[csShiftOut],
            'RecAbnormite' : raOut,
            'AttExceptionId' : caeOut})
        if AttRule['OutCheckRecType']==ocBOut:
            SpecialIntervals[len(SpecialIntervals)-1]['AttExceptionId'] =caeBOut

def IsSpecialType(CCState):
    Result = False
    for  t in SpecialIntervals:
        if (t['StartTag']==CCState) or (t['EndTag']==CCState):
            Result = True
            break


def ClearTableData(TableName, Condition=''):
    from mysite.iclock.sql import ClearTableData_sql
    sqlstr=ClearTableData_sql(Condition,TableName)
    customSql(sqlstr)

def ClearData(DeptID, allData=True):
    from mysite.att.models import USER_TEMP_SCH,num_run_Deil
    UserCri = ''
    DeptCri = ''
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
        DeptCri = '"DeptId">1'
    else:
        DeptCri = 'DeptId>1'

    if DeptID>0:
        pass
    else:
        ClearTableData('Departments', DeptCri)
        ClearTableData('UserInfo', UserCri)
        ClearTableData('User_of_RUN', UserCri)
        ClearTableData('EmpSpecDay', UserCri)
        ClearTableData(USER_TEMP_SCH._meta.db_table, UserCri)
        ClearTableData('CheckInOut', UserCri)
        ClearTableData('Template', UserCri)
#        ClearTableData('usersmachines', UserCri)
#        ClearTableData('userACPrivilege', UserCri)
        ClearTableData('Holiday', UserCri)
        ClearTableData('securitydetails', UserCri)
#        ClearTableData('ServerLog', '')
#        ClearTableData('userupdates', '')

#        ClearTableData('EmOpLog', '')
        #if gOptions.IsAccessControl:
            #ClearTableData('ACTimeZones', '');
            #ClearTableData('ACGroup', '');
            #ClearTableData('ACUnlockComb', '');
            #ClearTableData('UserACMachines', '');

#        ClearTableData('SystemLog', '')
        ClearTableData(USER_TEMP_SCH._meta.db_table, '')
#        ClearTableData('tbkey', '')
#        ClearTableData('tbsmsinfo', '')
#        ClearTableData('tbsmsallot', '')
        ClearTableData('num_run_Deil', '')
        ClearTableData(NUM_RUN._meta.db_table, '')
        ClearTableData('checkexact', '')
        ClearTableData('SchClass', '')






def CompareCheckTime():
    Result=0
    global AttRule
    if (ClTA[1]['CheckTime'] < ChPA[1]['CCStart']) or (ChPA[1]['OutState'] and (ClTA[1]['CheckTime']<ChPA[1]['CCEnd']) and\
                               ( ( (  ( (ClTA[3]['CheckType'] =='I') or (ClTA[3]['CheckType']== 'O')) or (AttRule['OutCheckRecType']==ocIgnore)) and\
                                   (ClTA[2]['CheckTime']<ChPA[1]['CCEnd']) and (ClTA[2]['CheckTime']<ChPA[2]['CCStart'])) \
                                   or (ClTA[2]['CheckTime']<ChPA[1]['CCTime']) or \
                                   (ClTA[2]['CheckTime']<ClTA[1]['CheckTime']+ datetime.timedelta(minutes=int(AttRule['MinRecordInterval']))))):
        Result = 1

    elif (ClTA[1]['CheckTime'] >= ChPA[1]['CCEnd']) :
        Result = -1
    elif IsSpecialType(ClTA[1]['CheckType']):
        Result = 1
    else:
        if ((ClTA[1]['CheckTime'] < ChPA[0]['CCEnd']) or ((ClTA[1]['CheckTime'] < ChPA[1]['CCTime'])\
                                  and (ClTA[2]['CheckType']!=ClTA[1]['CheckType']))) and (ClTA[2]['CheckTime'] < ChPA[1]['CCEnd']) and \
           (ClTA[2]['CheckTime'] < ChPA[1]['CCTime']) and (ClTA[2]['CheckType'] == ChPA[1]['CCState']) :
            if (ClTA[1]['CheckType']== ChPA[0]['CCState']) or (ClTA[2]['CheckTime'] < ChPA[2]['CCTime']):
                Result = 1
        if ((ClTA[1]['CheckTime'] < ChPA[1]['CCTime']) and (ClTA[2]['CheckType']!=ClTA[1]['CheckType'])) and \
           (ClTA[2]['CheckTime'] < ChPA[1]['CCEnd']) and (ClTA[2]['CheckTime'] < ChPA[1]['CCTime']) and \
           (ClTA[2]['CheckType']== ChPA[1]['CCState']):
            if (ClTA[1]['CheckType'] == ChPA[0]['CCState']) or (ClTA[2]['CheckTime'] < ChPA[2]['CCTime']):
                Result = 1
        if (ClTA[1]['CheckTime'] > ChPA[2]['CCStart']) and \
               (ClTA[2]['CheckTime']>ChPA[2]['CCTime']) and \
               (((ClTA[1]['CheckType']== ChPA[2]['CCState']) and \
                 (ClTA[1]['CheckTime']>(ChPA[1]['CCTime']+(ChPA[2]['CCTime']-ChPA[1]['CCTime'])*2/3))) or \
                 (ClTA[1]['CheckTime']>(ChPA[1]['CCTime']+(ChPA[2]['CCTime']-ChPA[1]['CCTime'])/2))):
                Result = -1

    return Result

def AddAttException(exceptionid,st,et,RecException):
    global UserID
    global rmdattexception
    tempdict={'UserID':UserID,'StartTime':st['CheckTime'],'EndTime':et['CheckTime'],
                'ExceptionID':exceptionid,'InScopeTime':0,'SchId':0,'TimeLong':0,'OverlapTime':0,
                'OverLapWorkDay':0,'OverlapWorkDayTail':0,'MinsWorkDay1':0,'SchIndex':-1,'clearance':0,'UserSpedayID':0}
    
    CalcAttExcTimeLong(tempdict)
    if RecException!=raValid:
        AddRecAbnormite(st['CheckTime'],st['CheckType'],CCheckInTag[RecAbnormiteOfState[exceptionid]][1],RecException,st['SN'],st['VerifyCode'])
        AddRecAbnormite(et['CheckTime'],et['CheckType'],CCheckInTag[RecAbnormiteOfState[exceptionid]][0],RecException,et['SN'],et['VerifyCode'])


def ExcepClockRecord():
    e=raValid
    if ClTA[1]['CheckTime']<ClTA[0]['CheckTime']+datetime.timedelta(minutes=int(AttRule['MinRecordInterval'])):
        e=raRepeat
    elif ClTA[1]['CheckTime']>ClTA[2]['CheckTime']-datetime.timedelta(minutes=int(AttRule['MinRecordInterval'])):
        e=raRepeat

    Result=(e!=raValid)
    if Result:
        AddRecAbnormite(ClTA[1]['CheckTime'],ClTA[1]['CheckType'],'',e,ClTA[1]['SN'],ClTA[1]['VerifyCode'])
    return Result




def ExcepSpeInterval():
    Result=False
    global UserSchPlan

    for t in SpecialIntervals:
        if UserSchPlan['OverTime']>0 or not (t['AttExceptionId'] in [caeFreeOT,caeOT]):
            if ((t['StartTag']==ClTA[1]['CheckType']) and (t['EndTag']==ClTA[2]['CheckType']))  and +\
               (diffTime(ClTA[2]['CheckTime']-ClTA[1]['CheckTime'])<t['MaxInterval']*60)  and +\
               (diffTime(ClTA[2]['CheckTime']-ClTA[1]['CheckTime'])>t['MinInterval']*60)  and +\
               (ClTA[2]['CheckTime']<ChPA[1]['CCTime']):
                if (t['EndTag']==ClTA[2]['CheckType']):
                    AddAttException(t['AttExceptionId'],ClTA[1],ClTA[2],t['RecAbnormite'])
                GetNextClockInOut(True)
                Result=True
                return Result

    for t in SpecialIntervals:
        if (t['StartTag']==ClTA[1]['CheckType']) or (t['EndTag']==ClTA[1]['CheckType']):
            AddRecAbnormite(ClTA[1]['CheckTime'],ClTA[1]['CheckType'],'',raInvalid,ClTA[1]['SN'],ClTA[1]['VerifyCode'])
            Result=True
    return Result



class TestCShift():
    global AttRule
    
    def IsValidShift(self):
        ss=self.schdict
        return  (ss['TimeZone']['StartTime']>self.PreShiftTime+datetime.timedelta(minutes= int(AttRule['MinShiftInterval']/3))) #班次时段超过前一个预先排定的班次时间范围
    def TestAShift(self,CheckTime, NextCheckTime,CheckType, NextCheckType,PreShiftTime, NextShiftTime):
        self.CheckTime=CheckTime
        self.NextCheckTime=NextCheckTime
        self.CheckType=CheckType
        self.NextCheckType=NextCheckType
        self.PreShiftTime=PreShiftTime
        self.NextShiftTime=NextShiftTime
        self.Result=tsrNoShift
        self.schdict={}
        global UserSchPlan
        self.ValidTag=[]
        for i in range(len(UserSchPlan['MayUsedAutoIds'])+1):
            self.ValidTag.append(0)
        #the first check
        for i in range(len(UserSchPlan['MayUsedAutoIds'])):
            self.schdict=GetSchClassByID(UserSchPlan['MayUsedAutoIds'][i],CheckTime,CheckTime)
            if self.schdict!={}:
                if self.IsValidShift():
                    self.ValidTag[i+1]=1
                    ss=self.schdict
                    if ((CheckTime>ss['Intime']['StartTime']) and (CheckTime<ss['Intime']['EndTime']) and \
                       (NextCheckTime>ss['Outtime']['StartTime']) and (NextCheckTime<ss['Outtime']['EndTime']) and \
                       ((CheckType=='I') and (NextCheckType=='O'))):
                        self.Result=tsrInOut
                        break
        #the second check
        if self.Result==tsrNoShift:
            for i in range(len(UserSchPlan['MayUsedAutoIds'])):
                if self.ValidTag[i+1]==1:
                    self.schdict=GetSchClassByID(UserSchPlan['MayUsedAutoIds'][i],CheckTime,CheckTime)
                    ss=self.schdict
                    if self.schdict!={}:
                        if self.IsValidShift():
                            if ((CheckTime>ss['Intime']['StartTime']) and (CheckTime<ss['Intime']['EndTime']) and \
                                (NextCheckTime>ss['Outtime']['StartTime']) and (NextCheckTime<ss['Outtime']['EndTime']) and \
                                ((CheckType in ['I','O']) or (NextCheckType in ['I','O']))):
                                self.Result=tsrInOut
                                break
                            
                    
        if self.Result==tsrNoShift:
            for i in range(len(UserSchPlan['MayUsedAutoIds'])):
                if self.ValidTag[i+1]==1:
                    self.schdict=GetSchClassByID(UserSchPlan['MayUsedAutoIds'][i],CheckTime,CheckTime)
                    ss=self.schdict
                    if self.schdict!={}:
                        if self.IsValidShift():
                            if ((CheckTime>ss['Intime']['StartTime']) and (CheckTime<ss['Intime']['EndTime']) and (CheckType=='I')):
                                self.Result=tsrIn
                                break
                            elif ((CheckTime>ss['Outtime']['StartTime']) and (CheckTime<ss['Outtime']['EndTime']) and (CheckType=='O')):
                                self.Result=tsrOut
                                break
        
        return self.Result

 
  #if Result<>tsrNoShift then
    #if TempShift<>nil then
      #CopyMemory(TempShift, @ss, SizeOf(ss));
#end;






def AddAttAutoSch(Shift, StartTime, EndTime):
    from mysite.att.models import attShifts
    global rmdattabnormite
    global AutoWorkTime1
    global UserID
    if rmdattabnormite['SchIndex']!="null":
        rmdattabnormite['userid']=UserID
        CalcAttAbnormite(False)
        if rmdattabnormite['AttDate']>=StartDate and rmdattabnormite['AttDate']<=EndDate:
            Post(attShifts._meta.db_table, rmdattabnormite)
        getattFields(attShifts,rmdattabnormite)
    rmdattabnormite['AutoSch']=1
    AutoWorkTime1=Shift
    rmdattabnormite['SchIndex']=-1
    rmdattabnormite['SchId']=Shift['schClassID']
    AddAttAbnormite(StartTime,EndTime)

def ExcepAutoShift():
    ss={}
    global UserSchPlan
    global AutoWorkTime
    AutoWorkTime={}
    if not ExcepSpeInterval():

        if not ExcepClockRecord():
            if ChPA[0]['OutState'] or ChPA[1]['InState'] or ChPA[1]['CCTime']==MaxDate:
                TestShiftResult=tsrNoShift
                testshift=TestCShift()
                if UserSchPlan['AutoSchPlan'] and UserSchPlan['MinAutoPlanInterval']<=diffTime(ChPA[1]['CCTime']-ChPA[0]['CCTime'])/60/60:
                    TestShiftResult=testshift.TestAShift(ClTA[1]['CheckTime'],ClTA[2]['CheckTime'],ClTA[1]['CheckType'],ClTA[2]['CheckType'],ChPA[0]['CCTime'],ChPA[1]['CCTime'])
                    ss=testshift.schdict
                if TestShiftResult!=tsrNoShift:
                    if TestShiftResult!=tsrOut:
                        AutoWorkTime=ss
                        AddRecAbnormite(ClTA[1]['CheckTime'],ClTA[1]['CheckType'],'I',raAutoSch,ClTA[1]['SN'],ClTA[1]['VerifyCode'],ss['schClassID'])
                    while ((((ClTA[3]['CheckType']=='I') or (ClTA[3]['CheckType']=='O')) or (AttRule['OutCheckRecType']==ocIgnore)) and 
                           (ClTA[3]['CheckTime']<ss['Outtime']['EndTime'])) or ((ClTA[3]['CheckTime']<ClTA[2]['CheckTime']+datetime.timedelta(minutes=AttRule['MinRecordInterval'])) and 
                                                    (ClTA[3]['CheckTime']<MaxDate)):
                        AddRecAbnormite(ClTA[2]['CheckTime'],ClTA[2]['CheckType'],'',raInvalid,ClTA[2]['SN'],ClTA[2]['VerifyCode'])
                        GetNextClockInOut(True,True)
                        if UserSchPlan['AutoSchPlan'] and (UserSchPlan['MinAutoPlanInterval']<=diffTime(ChPA[1]['CCTime']-ChPA[0]['CCTime'])/60/60):
                            TestShiftResult=testshift.TestAShift(ClTA[1]['CheckTime'],ClTA[2]['CheckTime'],ClTA[1]['CheckType'],ClTA[2]['CheckType'],ChPA[0]['CCTime'],ChPA[1]['CCTime'])
                            ss=testshift.schdict
                if TestShiftResult!=tsrNoShift:
                    if TestShiftResult==tsrInOut:
                        AddAttAutoSch(ss,ClTA[1],ClTA[2])
                        AddRecAbnormite(ClTA[2]['CheckTime'],ClTA[2]['CheckType'],'O',raAutoSch,ClTA[2]['SN'],ClTA[2]['VerifyCode'],ss['SchID'])
                        ChPA[0]['CCTime']=ss['TimeZone']['EndTime']
                        ChPA[0]['CCState']='O'
                        ChPA[0]['InState']=False
                        ChPA[0]['OutState']=True
                        ChPA[0]['CCMust']=True
                        ChPA[0]['CCStart']=ss['Outtime']['StartTime']
                        ChPA[0]['CCEnd']=ss['Outtime']['EndTime']
                        ChPA[0]['CCAuto']=True
                        GetNextClockInOut(False)
                    elif TestShiftResult==tsrIn:
                        AddAttAutoSch(ss,ClTA[1],0)
                    elif TestShiftResult==tsrOut:
                        AddAttAutoSch(ss,0,ClTA[1])
                elif UserSchPlan['OverTime']>0  and (((ClTA[2]['CheckTime']<ClTA[1]['CheckTime']+datetime.timedelta(minutes=AttRule['MaxShiftInterval'])) and
                                     (ClTA[2]['CheckTime']>=ClTA[1]['CheckTime']+datetime.timedelta(minutes=AttRule['MinShiftInterval'])) and 
                                     (ClTA[2]['CheckTime']<ChPA[1]['CCTime']-datetime.timedelta(minutes=AttRule['MinShiftInterval'])) and 
                                     ((ClTA[2]['CheckType'] in ('O','o')) or (ClTA[1]['CheckTime'].hour+(float)(ClTA[1]['CheckTime'].minute)/60<12.5) or 
                                      (ClTA[2]['CheckTime'].hour+(float)(ClTA[2]['CheckTime'].minute)/60>13))) or 
                                      ((ClTA[1]['CheckType']=='I') and (ClTA[2]['CheckType']=='O') and
                                       (ClTA[2]['CheckTime']<ChPA[1]['CCStart']) and 
                                       (ClTA[2]['CheckTime']<ClTA[1]['CheckTime']+datetime.timedelta(minutes=AttRule['MaxShiftInterval'])))):
                    AddAttException(caeFreeOT,ClTA[1],ClTA[2],raFreeOT)
                    ChPA[0]['CCTime']=ClTA[2]['CheckTime']
                    ChPA[0]['CCState']='O'
                    ChPA[0]['InState']=False
                    ChPA[0]['OutState']=True
                    ChPA[0]['CCMust']=False
                    ChPA[0]['CCStart']=ClTA[2]['CheckTime']
                    ChPA[0]['CCEnd']=ClTA[2]['CheckTime']
                    ChPA[0]['CCAuto']=True
                    GetNextClockInOut(False)
                else:
                    AddRecAbnormite(ClTA[1]['CheckTime'],ClTA[1]['CheckType'],'',raInvalid,ClTA[1]['SN'],ClTA[1]['VerifyCode'])
            else:
                AddRecAbnormite(ClTA[1]['CheckTime'],ClTA[1]['CheckType'],'',raInvalid,ClTA[1]['SN'],ClTA[1]['VerifyCode'],1)


def AddRecAbnormite(CheckTime,CheckType, NewType,AbnormiteID,sn='null',Verifycode=1,SchID =-1):
#    sql="""insert into %s (userid,checktime,checktype,NewType,AbnormiteID) values('%s', '%s', '%s', '%s', '%s')""" % (attRecAbnormite._meta.db_table, UserID, CheckTime.strftime("%Y-%m-%d %H:%M:%S"), CheckType, NewType,AbnormiteID,SchID)
    from mysite.att.models import attRecAbnormite
    global rmdRecAbnormite
    global AutoWorkTime
    global UserID
    global rmdattabnormite
    global StartDate
    global EndDate
    getattFields(attRecAbnormite,rmdRecAbnormite)
    rmdRecAbnormite['userid']=UserID  #UserSchPlan['UserID']

    rmdRecAbnormite['checktime']=CheckTime
    rmdRecAbnormite['CheckType']=CheckType
    if NewType!=CheckType:
        rmdRecAbnormite['NewType']=NewType
    rmdRecAbnormite['AbNormiteID']=AbnormiteID

    if AbnormiteID==raAutoSch:
        sss=AutoWorkTime
    elif AbnormiteID==raValid or ((AbnormiteID==raRepeat) and (SchID>-1)):
        sss=WorkTimeZone[rmdattabnormite['SchIndex']]
    else:
        sss={'TimeZone':{'StartTime':CheckTime,'EndTime':CheckTime}}
        
    rmdRecAbnormite['AttDate']=trunc(sss['TimeZone']['StartTime'])
    if AttRule['TwoDay']=='1' and trunc(sss['TimeZone']['EndTime'])>trunc(sss['TimeZone']['StartTime']):
        rmdRecAbnormite['AttDate']=rmdRecAbnormite['AttDate']+datetime.timedelta(days=1)
    if SchID>-1:
        rmdRecAbnormite['SchID']=SchID
    keys=rmdRecAbnormite.keys()
    if 'SN' in keys:
        if sn=='':sn='null'
        rmdRecAbnormite['SN']=sn
    if 'verifycode' in keys:
        rmdRecAbnormite['verifycode']=Verifycode
    if rmdRecAbnormite['AttDate']>=StartDate and rmdRecAbnormite['AttDate']<=EndDate:
        Post(attRecAbnormite._meta.db_table,rmdRecAbnormite)


def getattFields(self,dict):
    #f=('UserID','SchIndex','AutoSch','AttDate','SchId','ClockInTime','ClockOutTime ','StartTime',
                        #'EndTime','WorkDay','RealWorkDay','NoIn','NoOut','Late','Early','Absent',
                    #'OverTime','WorkTime','ExceptionID','Symbol','MustIn','MustOut','OverTime1',
                #'WorkMins','SSpeDayNormal','SSpeDayWeekend','SSpeDayHoliday','AttTime','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT',
            #'AbsentMins','AttChkTime','AbsentR','ScheduleName')
    field_names = [f.column for f in self._meta.fields if not isinstance(f, AutoField)]
    for t in field_names:
        dict[t]='null'
def AddAttAbnormite(CheckIn,CheckOut):
    global rmdattabnormite
    if rmdattabnormite['SchIndex']!='null':
        if rmdattabnormite['AutoSch']==True:
            abnormiteid = raAutoSch
        else:
            abnormiteid = raValid
        if CheckIn<>0:
            rmdattabnormite['StartTime']=CheckIn['CheckTime']
            if rmdattabnormite['AutoSch']<>True:
                AddRecAbnormite(CheckIn['CheckTime'], CheckIn['CheckType'], 'I', abnormiteid,CheckIn['SN'],CheckIn['VerifyCode'], rmdattabnormite['SchId'])
        if CheckOut<>0:
            rmdattabnormite['EndTime']=CheckOut['CheckTime']
            if rmdattabnormite['AutoSch']<>True:
                AddRecAbnormite(CheckOut['CheckTime'], CheckOut['CheckType'], 'O', abnormiteid,CheckOut['SN'],CheckOut['VerifyCode'],rmdattabnormite['SchId'])


def Post(TableName,d):
    sql=getSQL_insert_ex(TableName,d)
#    print sql
    customSql(sql)
#    print "------------"
def NormalAttValueEx(**kwargs):
    """暂时未用 """
    AsWorkDay=1
    for k,v in kwargs.items():
        if k=='Value':
            Value=v
        elif k=='MinUnit':
            MinUnit=v
        elif k=='AttUnit':
            AttUnit=v
        elif k=='RemaindProc':
            RemaindProc=v
        elif k=='WorkMins':#该时段的分钟时间
            WorkMins=v
        elif k=='AsWorkDay':#该时段计为多少工作日
            AsWorkDay=v
        if AsWorkDay==0:AsWorkDay=1    
#    print "==========000==",Value,MinUnit,AttUnit,RemaindProc
    
    global AttRule
    Result=0
    if Value=='null':
        return Result
    if MinUnit < 0.01:
        MinUnit = 0.01
    if (Value > 0) and (AttUnit == auTimes):
        Result = 1
        return Result
    elif AttUnit == auTimes:
        Result = 0
        return Result
    else:
        if AttUnit==auDay:
            MinsUnit=1
        elif AttUnit==auWorkDay:
            MinsUnit=WorkMins
        elif AttUnit==auHour:
            MinsUnit=60
        elif AttUnit==auMinute:
            MinsUnit=1
    Value=value
    MinsUnit=MinsUnit
    if MinsUnit==0:
        MinsUnit=480
    if WorkdayFlag!=auWorkDay:
        Value = Value/MinsUnit   
    if RemaindProc==rmTrunc:
        c = int(Value/MinUnit)
    elif RemaindProc==rmUpTo:
        c = int(Value/MinUnit)
        if Value>MinUnit*c:
            c +=1
    elif RemaindProc==rmRound:
        c = round(Value/MinUnit)
    if RemaindProc!=rmCount:
        Result = c*MinUnit
    else:
        Result=round(Value*100)/100
    return Result


def NormalAttValue(Value, MinUnit,AttUnit, RemaindProc,WorkdayFlag=auHour,minsworkday=480):
    #print "Value=",Value
    #print "MinUnit=",MinUnit
    #print "AttUnit=",AttUnit
    #print WorkdayFlag
    global AttRule
    from decimal import ROUND_HALF_UP,Decimal
    if not AttRule:
       AttRule=LoadAttRule()
    Result=0
    if Value=='null':
        return Value
    if Value=='':
        return Value
    if MinUnit < 0.01:
        MinUnit = 0.01
    if (Value > 0) and (AttUnit == auTimes):
        Result = 1
        return Result
    elif AttUnit == auTimes:
        Result = 0
        return Result
    else:
        if AttUnit==auDay:
            MinsUnit=1
        elif AttUnit==auWorkDay:
            #if AttRule['MinsWorkDay1']==0:
            AttRule['MinsWorkDay1']=minsworkday
            if WorkdayFlag!=auWorkDay:
                MinsUnit = AttRule['MinsWorkDay1']
            else:
                MinsUnit=MinUnit
        elif AttUnit==auHour:
            MinsUnit=60
        elif AttUnit==auMinute:
            MinsUnit=1
    Value=float(Value)
    MinsUnit=float(MinsUnit)
    if MinsUnit==0:
        MinsUnit=float(minsworkday)
    if WorkdayFlag!=auWorkDay:
        Value = Value/MinsUnit   
    if RemaindProc==rmTrunc:
        c = int(Value/MinUnit)
    elif RemaindProc==rmUpTo:
        c = int(Value/MinUnit)
        if Value>MinUnit*c:
            c +=1
    elif RemaindProc==rmRound:
        c = round(Value/MinUnit)
    if RemaindProc!=rmCount:
        Result = c*MinUnit
    else:
        Result=round(Value*100)/100
    #print "Result:",Result
    r=Decimal(str(Result))
    return str(r.quantize(Decimal('0.0'),ROUND_HALF_UP))
#    if str(Result).find(".")>0:   #超过2位小数，直接舍弃
#        if len(str(Result).split(".")[1])>2:
#            Result=int(Result*100)/100
#    return Result

def GetExceptionSymbol(ExceptID):
    return ''

def GetCurExceptionIndex(exceptdict):
    Result=0
    if exceptdict['AuditExcId']=='null':
        Result=exceptdict['ExceptionId']
    else:
        Result=exceptdict['AuditExcId']
        if Result==-1:
            Result=exceptdict['ExceptionId']
    return Result


def GetRelateException(UserId, StartTime, EndTime):
    Result=[]
    global rmdattexception
    for t in rmdattexception:
        if t['UserID']!=UserId: #or t['AuditExcId']==-1:
            continue
        if not t['InScopeTime']:continue
        if t['StartTime']<=StartTime:
            if t['EndTime']>=EndTime:
#                Result.append({'ExceptionID':GetCurExceptionIndex(t),'Symbol':'','StartTime':t['StartTime'], 'EndTime':t['EndTime'],'ShiftBreaks':[sbStart, sbEnd]})
                Result.append({'ExceptionID':t['ExceptionID'],'Symbol':'','StartTime':t['StartTime'], 'EndTime':t['EndTime'],'ShiftBreaks':[sbStart, sbEnd],'clearance':t['clearance']})
            elif t['EndTime']>=StartTime:
                Result.append({'ExceptionID':t['ExceptionID'],'Symbol':'','StartTime':t['StartTime'], 'EndTime':t['EndTime'],'ShiftBreaks':[sbStart],'clearance':t['clearance']})
        else:
            if t['StartTime']<EndTime:
                if t['EndTime']>=EndTime:
                    Result.append({'ExceptionID':t['ExceptionID'],'Symbol':'','StartTime':t['StartTime'], 'EndTime':t['EndTime'],'ShiftBreaks':[sbEnd],'clearance':t['clearance']})
                elif t['EndTime']>=StartTime:
                    Result.append({'ExceptionID':t['ExceptionID'],'Symbol':'','StartTime':t['StartTime'], 'EndTime':t['EndTime'],'ShiftBreaks':[],'clearance':t['clearance']})
    return Result

def GetRelateExceptionEx(schindex,sct='null',ect='null'):
    Result=False
    global rmdattexception
    for t in rmdattexception:
        if t['SchIndex']==schindex:
            if t['EndTime']<=sct or t['StartTime']>=ect:
                Result=True
    return Result

def SumInScopeTime(schindex,st='null',et='null'):
    Result=0
    global rmdattexception
    for t in rmdattexception:
        if t['SchIndex']==schindex:
            if t['clearance']:
                if st!='null' or et!='null':
                    Result=0
                    t['InScopeTime']=0
                else:
                    Result=Result+t['InScopeTime']
                    
            else:
                Result=Result+t['InScopeTime']
    return Result

def SumRestTime(st,et,srt,ert,srt1,ert1,type=0):
    if type==0:
        if st=='null' or et=='null':
            re=datetime.timedelta(0)
        elif et<=srt or st>=ert:
            re=ert-srt
        elif et>srt and et<ert:
            re=ert-et
        elif st>srt and st<ert:
            re=st-srt
        elif st>=srt and et<=ert:
            re=(st-srt)+(ert-et)
        else:
            re=datetime.timedelta(0)
        r=re.days*24*60+re.seconds/60
        
        if st=='null' or et=='null':
            re=datetime.timedelta(0)
        elif et<=srt1 or st>=ert1:
            re=ert1-srt1
        elif et>srt1 and et<ert1:
            re=ert1-et
        elif st>srt1 and st<ert1:
            re=st-srt1
        elif st>=srt1 and et<=ert1:
            re=(st-srt1)+(ert1-et)
        else:
            re=datetime.timedelta(0)
        r=r+re.days*24*60+re.seconds/60
    else:   #计算请假所包含的休息时间
        if et<=srt or st>=ert:
            re=datetime.timedelta(0)
        elif st<=srt and et>=ert:
            re=ert-srt
        elif st<=srt and et<=ert:
            re=et-srt
        elif st>=srt and et<=ert:
            re=et-st
        elif st>=srt and et>=ert:
            re=ert-st
        else:
            re=datetime.timedelta(0)
        r=re.days*24*60+re.seconds/60
        if et<=srt1 or st>=ert1:
            re=datetime.timedelta(0)
        elif st<=srt1 and et>=ert1:
            re=ert1-srt1
        elif st<=srt1 and et<=ert1:
            re=et-srt1
        elif st>=srt1 and et<=ert1:
            re=et-st
        elif st>=srt1 and et>=ert1:
            re=ert1-st
        else:
            re=datetime.timedelta(0)
        r=r+re.days*24*60+re.seconds/60
            
#    print "sumresttime===",r
    return r

#对班次进行计算
def CalcAttAbnormite(OnlyRptItem):
    global rmdAttAbnormite
    global LeaveClasses
    global AutoWorkTime1
    global LClasses1

    d=rmdattabnormite
    
    if d['AutoSch']==True:
        ss=AutoWorkTime1
    else:
        ss=WorkTimeZone[d['SchIndex']]
    d['SchId']=ss['schClassID']
    d['ClockInTime'] = ss['TimeZone']['StartTime']
    d['ClockOutTime'] = ss['TimeZone']['EndTime']
    d['AttDate']=trunc(d['ClockInTime'])
    if AttRule['TwoDay']==1 and trunc(d['ClockOutTime'])>trunc(d['ClockInTime']):
        d['AttDate']=d['AttDate']+datetime.timedelta(days=1)

        #以下暂时无用
    #if (ss.intime.StartTime<SStartTime) and (d['attdate']>=startdate) then
        #SStartTime:=ss.InTime.StartTime;
    #if (ss.OutTime.EndTime > SEndTime) and (d['attdate']<=enddate) then
        #sendtime:=ss.OutTime.EndTime;

#    tmins=ss['workMins']
        #if ss.WorkMins<>0 then
        #d['WorkMins']:=tmins*oneminute //EncodeTime(tmins div 60,tmins mod 60,0,0);
        #else
    isholiday=IsHoliday(d['AttDate'])

    if ss['WorkMins']==0:
        t=d['ClockOutTime']-d['ClockInTime']
        if ss['IsCalcRest']==1:
            t=t-(ss['EndRestTime']-ss['StartRestTime'])
        
        ss['WorkMins']= t.days*24*60+t.seconds/60
    d['WorkMins']= ss['WorkMins']
        
    if AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['Unit']==auWorkDay:
        d['WorkDay'] = ss['WorkDay']
    else:              
        d['WorkDay']=NormalAttValue(d['WorkMins'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['MinUnit'],
                        AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['RemaindProc'])

    if AttAbnomiteRptItems[AttAbnomiteRptIndex[aaAbsent]]['Unit']==auWorkDay:
        d['AbsentR'] = ss['WorkDay']
    else:              
        d['AbsentR']=NormalAttValue(d['WorkMins'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaAbsent]]['MinUnit'],
                        AttAbnomiteRptItems[AttAbnomiteRptIndex[aaAbsent]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaAbsent]]['RemaindProc'])


    if d['StartTime']=='null' and d['EndTime']=='null':
        d['Absent']=1
        d['NoIn']=1
        d['NoOut']=1

    else:
        if d['StartTime']!='null':
            if d['StartTime']>ss['TimeZone']['StartTime']:
                t=d['StartTime']-ss['TimeZone']['StartTime']
                t=t.seconds/60
                
                if t>ss['MinsLate']:
                    d['Late']=t

        else:
            d['NoIn']=1

        if d['EndTime']!='null':
            if ss['TimeZone']['EndTime']>d['EndTime']:
                t=ss['TimeZone']['EndTime'] - d['EndTime']
                t=t.seconds/60
                if t>ss['MinsEarly']:
                    d['Early']=t
        else:
            d['NoOut']=1
            
            
    if (UserSchPlan['ClockIn']==1) or ((UserSchPlan['ClockIn']==0 or UserSchPlan['ClockIn']==None) and ss['MustClockIn']==1):
        d['MustIn']=1
    if (UserSchPlan['ClockOut']==1) or ((UserSchPlan['ClockOut']==0 or UserSchPlan['ClockOut']==None) and ss['MustClockOut']==1):
        d['MustOut']=1

    if d['NoIn']==1 and d['MustIn']!=1:
        d['NoIn']='null'
    if d['NoOut']==1 and d['MustOut']!=1:
        d['NoOut']='null'

    if d['Late']!='null' and d['MustIn']!=1:
        d['Late']='null'
    if d['Early']!='null' and d['MustOut']!=1:
        d['Early']='null'

    if d['MustIn']!=1 and d['MustOut']!=1:
        d['Absent']='null'
        d['Late']='null'
        d['Early']='null'
        d['NoOut']='null'
        d['NoIn']='null'
    sbs=GetRelateException(d['userid'],ss['TimeZone']['StartTime'],ss['TimeZone']['EndTime'])
    for t in sbs:
#        if not t['clearance'] or (t['clearance']):
        if sbStart in t['ShiftBreaks']:
            if sbEnd in t['ShiftBreaks']:
                d['ExceptionID']=t['ExceptionID']
                d['NoIn']='null'
                d['NoOut']='null'
                d['Absent']='null'
                d['Late']='null'
                d['Early']='null'
                break
            else:
                d['NoIn']='null'
                d['Late']='null'
                if d['ExceptionID']=='null':
                    d['ExceptionID']=t['ExceptionID']
        elif sbEnd in t['ShiftBreaks']:
            d['NoOut']='null'
            d['Early']='null'
            if d['ExceptionID']=='null':
                d['ExceptionID']=t['ExceptionID']
        elif t['ExceptionID'] not in (caeFreeOT,caeOT):
            d['ExceptionID']=t['ExceptionID']

    if (d['NoIn']!='null' and AttRule['NoInAbsent']>0):    #
#        d['NoIn']='null'
        if AttRule['NoInAbsent']==1:
            d['Late']=int(AttRule['MinsNoIn'])
        else:
            d['Absent']=1
    if (d['NoOut']!='null' and AttRule['NoOutAbsent']>0):
#        d['NoOut']='null'
        if AttRule['NoOutAbsent']==1:
            d['Early']=int(AttRule['MinsNoOut'])
        else:
            d['Absent']=1

    if AttRule['LateAbsent'] and  d['Late']!='null' and d['Late']>AttRule['MinsLateAbsent']:
        d['Absent']=1
    if AttRule['EarlyAbsent'] and d['Early']!='null' and d['Early']>AttRule['MinsEarlyAbsent']:
        d['Absent']=1

    if d['Absent']==1:
        d['Early']='null'
        d['Late']='null'
        d['AbsentMins']=d['WorkMins']
    if d['Absent']==1:
        d['WorkTime']=0
    ExceptIndex=LeaveIDToIndex(d['ExceptionID'])
    ExceptionTime=0
#    if (d['Absent']==1 and d['ExceptionID']<>'null' and d['ExceptionID']>=FirstExceptionID) or d['Absent']!=1:
    if (d['Absent']==1 and d['ExceptionID']<>'null' and (d['ExceptionID'] not in (caeFreeOT,caeOT))) or d['Absent']!=1:
        if d['StartTime']=='null':
            t=d['ClockInTime']
        else:
            t=d['StartTime']
        if d['EndTime']=='null':
            t2=d['ClockOutTime']
        else:
            t2=d['EndTime']
        d['AttTime']=(t2-t).days*24*60+(t2-t).seconds/60-ss['RestTime']
        d['AttTime']=d['AttTime']+SumRestTime(t,t2,ss['StartRestTime'], ss['EndRestTime'],ss['StartRestTime1'], ss['EndRestTime1'])
        if ss['WorkMins']==0:
            t=d['ClockInTime']
            t2=d['ClockOutTime']
            d['WorkTime']=(t2-t).days*24*60+(t2-t).seconds/60
            if d['Late']!='null':
                if d['WorkTime']>d['Late']:
                    d['WorkTime']=d['WorkTime']-d['Late']
                else:
                    d['WorkTime']=0
                if d['EndTime']=='null':                       #???
                    d['AttTime']=d['AttTime']-d['Late']
            if d['Early']!='null':
                if d['WorkTime']>d['Early']:
                    d['WorkTime']=d['WorkTime']-d['Early']
                else:
                    d['WorkTime']=0
                if d['StartTime']=='null':                  #???
                    d['AttTime']=d['AttTime']-d['Early']
            if d['ExceptionID']<>'null' and (d['ExceptionID'] not in (caeFreeOT,caeOT)):
                iTemp= ExceptIndex-FirstExceptionID-2
                if ExceptIndex<5 or ((ExceptIndex>4) and (LeaveClasses[iTemp]['IsLeave'])):
                        t=SumInScopeTime(d['SchIndex'])
                        if (d['WorkTime']>t):
                            d['WorkTime']=d['WorkTime']-t         
                        else:
                            d['WorkTime']=0
                        if d['AttTime']>t:
                            d['AttTime']=d['AttTime']-t
                        else:
                            d['AttTime']=0
                        if d['AbsentMins']!='null':
                            if d['AbsentMins']>t:
                                d['AbsentMins']=d['AbsentMins']-t
                            else:
                                d['AbsentMins']=0
                                d['Absent']='null'
                        if t>0:
                            d['Absent']='null'


        else:
            d['WorkTime']=d['WorkMins']
            if ss['IsCalcRest']:
                d['WorkTime']=d['WorkTime']+SumRestTime(d['StartTime'],d['EndTime'],ss['StartRestTime'], ss['EndRestTime'],ss['StartRestTime1'], ss['EndRestTime1'])
            if d['Late']!='null':
                if d['WorkTime']>d['Late']:
                    d['WorkTime']=d['WorkTime']-d['Late']
                else:
                    d['WorkTime']=0
                if d['StartTime']=='null' and d['Late']:                       #???
                    d['AttTime']=d['AttTime']-d['Late']
            if d['Early']!='null':
                if d['WorkTime']>d['Early']:
                    d['WorkTime']=d['WorkTime']-d['Early']
                else:
                    d['WorkTime']=0
                if d['EndTime']=='null':                  #???
                    d['AttTime']=d['AttTime']-d['Early']
            if d['ExceptionID']<>'null' and (ExceptIndex>=FirstExceptionID):
                iTemp=ExceptIndex -FirstExceptionID-2
                if ExceptIndex<5 or ((ExceptIndex>4) and (LClasses1[iTemp]['IsLeave'])):
#                    if (d['StartTime']=='null' and d['EndTime']=='null'):
                    t=SumInScopeTime(d['SchIndex'],d['StartTime'],d['EndTime'])
                    ExceptionTime=t
                    if t>0:
                        if (d['WorkTime']>t):
                            d['WorkTime']=d['WorkTime']-t         #此处有问题2009.08.08
                        else:
                            d['WorkTime']=0
                    if d['AttTime']>=t:#此处用于计算实际出勤时间存在不准确的问题
#                          if d['StartTime'] and d['EndTime']:
                        #    if not GetRelateExceptionEx(d['SchIndex'],d['StartTime'],d['EndTime']):
#                            d['AttTime']=d['AttTime']-t
#                        else:
                        d['AttTime']=d['AttTime']-t
                            
                    else:
                        d['AttTime']=0
                    if d['AbsentMins']!='null':
                        if d['AbsentMins']>t:
                            d['AbsentMins']=d['AbsentMins']-t
                        else:
                            d['AbsentMins']=0
                            d['Absent']='null'
                    if t>0:
                        d['Absent']='null'
                    #else:
                        #if (d['StartTime']!='null' or d['EndTime']!='null'):
                            #d['ExceptionID']='null'
                            #for ttt in rmdattexception:
                                #if ttt['AttDate']==d['AttDate']:
                                    #ttt['InScopeTime']=0
                                    #break

#        if d['Late']!='null':                            
        d['Late']=NormalAttValue(d['Late'],AttAbnomiteRptItems[AttAbnomiteRptIndex[aaLate]]['MinUnit'],
                     AttAbnomiteRptItems[AttAbnomiteRptIndex[aaLate]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaLate]]['RemaindProc'])
#        if d['Early']!='null':
        d['Early']=NormalAttValue(d['Early'],AttAbnomiteRptItems[AttAbnomiteRptIndex[aaEarly]]['MinUnit'],
                      AttAbnomiteRptItems[AttAbnomiteRptIndex[aaEarly]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaEarly]]['RemaindProc'])


        if d['WorkTime']>d['WorkMins']:
            d['WorkTime']=d['WorkMins']
        if AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]==auWorkDay:
            AttRule['MinsWorkDay1']=ss['WorkMins']
        if ss['WorkDay']==0:
            ss['WorkDay']=1
        d['RealWorkDay']=NormalAttValue(d['WorkTime'],AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['MinUnit'],
                        AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['RemaindProc'])
#        d['RealWorkDay']=NormalAttValueEx(Value=d['WorkTime'],MinUnit=AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['MinUnit'],AttUnit=AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['Unit'],RemaindProc=AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['RemaindProc'])
        if d['RealWorkDay']>d['WorkDay']:
            d['RealWorkDay']=d['WorkDay']

#        t=IsHoliday(d['AttDate'])
        if []==isholiday:
            d['SSpeDayNormal']=d['RealWorkDay']
        if 'htWeekend' in isholiday:
            d['SSpeDayWeekend']=d['RealWorkDay']
        if 'htCommHoliday' in isholiday:
            d['SSpeDayHoliday']=d['RealWorkDay']
        #print "UserSchPlan['OverTime']:%s"%UserSchPlan['OverTime']
        if UserSchPlan['OverTime']!='null' and UserSchPlan['OverTime']>=0:
            #print d['EndTime']
            if d['EndTime']!='null':
                t=(d['EndTime']-d['ClockOutTime']).seconds/60
            else:
                t=0
            if ss['OverTime']>0:
                if  t>0 and t>AttRule['MinsOutOverTime'] :                
                    d['OverTime']=ss['OverTime']
                
            elif AttRule['OutOverTime']>0 and t>0:                
                if t>AttRule['MinsOutOverTime']:
                    d['OverTime']=t
            #print t
            #print "d['OverTime']:",d['OverTime']
            if d['OverTime']>0:
                
                        
                d['OverTime']=NormalAttValue(d['OverTime'],AttAbnomiteRptItems[AttAbnomiteRptIndex[aaOT]]['MinUnit'],
                                 AttAbnomiteRptItems[AttAbnomiteRptIndex[aaOT]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[aaOT]]['RemaindProc'])
#                t=IsHoliday(d['AttDate'])
                if []==isholiday:
                    d['SSpeDayNormalOT']=d['OverTime']
                if 'htWeekend' in isholiday:
                    d['SSpeDayWeekendOT']=d['OverTime']
                if 'htCommHoliday' in isholiday:
                    d['SSpeDayHolidayOT']=d['OverTime']
    #if d['ExceptionID']!='null':
        #symbol=GetExceptionSymbol(d['ExceptionID'])
    #else:
        #symbol=''
    symbol=''
    if d['ExceptionID']!='null':
        if d['ExceptionID']==-4:
            symbol= AttAbnomiteRptItems[AttAbnomiteRptIndex[aaFOT]]['ReportSymbol']
        if d['ExceptionID']>0:    
            symbol= AttAbnomiteRptItems[AttAbnomiteRptIndex[d['ExceptionID']]]['ReportSymbol']
            if ExceptionTime>0:
                s=NormalAttValue(ExceptionTime,AttAbnomiteRptItems[AttAbnomiteRptIndex[d['ExceptionID']]]['MinUnit'],
                                 AttAbnomiteRptItems[AttAbnomiteRptIndex[d['ExceptionID']]]['Unit'] ,AttAbnomiteRptItems[AttAbnomiteRptIndex[d['ExceptionID']]]['RemaindProc'])    
                symbol=symbol+str(s)
            #symbol= AttAbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['ReportSymbol']
    if d['OverTime']!='null' and d['OverTime']>0:
        symbol=symbol+AttAbnomiteRptItems[AttAbnomiteRptIndex[aaOT]]['ReportSymbol']
        
    if d['Absent']!='null':
        symbol= AttAbnomiteRptItems[AttAbnomiteRptIndex[aaAbsent]]['ReportSymbol']+symbol
    else:
        if d['NoIn']!='null':
            symbol= symbol+AttAbnomiteRptItems[AttAbnomiteRptIndex[aaNoIn]]['ReportSymbol']
        if d['NoOut']!='null':
            symbol= symbol+AttAbnomiteRptItems[AttAbnomiteRptIndex[aaNoOut]]['ReportSymbol']
        if d['Late']!='null':
            symbol= symbol+AttAbnomiteRptItems[AttAbnomiteRptIndex[aaLate]]['ReportSymbol']
        if d['Early']!='null':
            symbol= symbol+AttAbnomiteRptItems[AttAbnomiteRptIndex[aaEarly]]['ReportSymbol']
        if symbol=='':
            if d['NoIn']=='null' and d['NoOut']=='null' and d['Late']=='null' and d['Early']=='null' and d['ExceptionID']=='null':
                symbol= AttAbnomiteRptItems[AttAbnomiteRptIndex[aaValid]]['ReportSymbol']
    
    d['Symbol']=symbol


def AddAttSch(SchIndex):
    from mysite.att.models import attShifts
    global rmdattabnormite
    global UserID
    if rmdattabnormite['SchIndex']!="null":
        rmdattabnormite['userid']=UserID
        CalcAttAbnormite(False)
        if rmdattabnormite['AttDate']>=StartDate and rmdattabnormite['AttDate']<=EndDate:
            Post(attShifts._meta.db_table, rmdattabnormite)
        getattFields(attShifts,rmdattabnormite)
    rmdattabnormite['SchIndex']=SchIndex


def ExcepInOutTime():
    if ChPA[1]['InState']==True:
        AddAttSch(ChPA[1]['Index'])
        AddAttAbnormite(ClTA[1] , 0)
    else:
        AddAttAbnormite(0,ClTA[1])
def ExcepCheckPoint():
    if ChPA[1]['InState']==True:
        AddAttSch(ChPA[1]['Index'])


def Calc():
    from mysite.att.models import attShifts,AttException
    global StartDate,EndDate
    global CheckInOutRecorNo
    global rmdattexception
    global rmdattabnormite
    CheckInOutRecorNo=0
    HasClockInOut = GetFirstClockInOut()
    HasCheckPoint = GetFirstCheckPoint()
    while True:
        try:
            #print "HasClockInOut:%s   HasCheckPoint:%s"%(HasClockInOut,HasCheckPoint)
            if HasClockInOut and HasCheckPoint:
                r=CompareCheckTime()
                #print "r:%s"%r
                if r==-1:
                    ExcepCheckPoint()
                    HasCheckPoint = GetNextCheckPoint()
                elif r==1:
                    ExcepAutoShift()
                    HasClockInOut = GetNextClockInOut(True)
                elif r==0:
                    ExcepInOutTime()
                    HasClockInOut = GetNextClockInOut()
                    HasCheckPoint = GetNextCheckPoint()
            elif HasClockInOut:
                ExcepAutoShift()
                HasClockInOut = GetNextClockInOut(True)
            elif HasCheckPoint:
                ExcepCheckPoint()
                HasCheckPoint = GetNextCheckPoint()
    
            if (not HasCheckPoint) and (not HasClockInOut):
                break
        except Exception, e:
            import traceback;traceback.print_exc()
            break
    #print "usesr %s  rmdattabnormite:%s"%(UserID,rmdattabnormite)
    if rmdattabnormite['SchIndex']!="null":
        rmdattabnormite['userid']=UserID
        CalcAttAbnormite(False)
        if rmdattabnormite['AttDate']>=StartDate and rmdattabnormite['AttDate']<=EndDate:
            if rmdattabnormite['SchId']!='null':
                Post(attShifts._meta.db_table, rmdattabnormite)
    #print "usesr %s  rmdattexception:%s"%(UserID,rmdattexception)
    if rmdattexception!=[]:
        print "rmdattexception:%s"%rmdattexception
        fflag=False
        field_names = [f.column for f in AttException._meta.fields if not isinstance(f, AutoField)]
        if 'UserSpedayID' in field_names:
            fflag=True
        for t in rmdattexception:
            if t['AttDate']>=StartDate and t['AttDate']<=EndDate:
                del t['clearance']
                if not fflag:
                    del t['UserSpedayID']
                t['status']=1
                #print "rmdattexception:%s"%t
                Post(AttException._meta.db_table,t)
                #sql=getSQL_insert_ex(AttException._meta.db_table,t)
                #customSql(sql)
    rmdattexception=[]


def PrepareUserCalc(userid,d1,d2):
    from mysite.att.models import Holiday as holidays,EmpSpecDay
    from mysite.iclock.models import Transaction    
    global tHoliday                 #节日表
    global CheckInOutData          #考勤记录
    global l_CheckInOutData
    global ExcepData               #请假记录
    global qryAudit
    global UserSchPlan
    global WorkTimeZone
    global UserID
    WorkTimeZone=[]
    UserID=int(userid)
    if tHoliday==None:
        tHoliday=holidays.objects.all().order_by('start_time')
        #len(Holiday)
    ExcepData=EmpSpecDay.objects.filter(emp__exact=int(userid),start__gte=d1-datetime.timedelta(days=180),end__lte=d2+datetime.timedelta(days=180)).order_by('start')
    
    dt1=d1-datetime.timedelta(days=1)
    dt2=d2+datetime.timedelta(days=2)
    #print "d1:%s   d2:%s"%(dt1,dt2)
    #,TTime__range=(dt1,dt2)
    CheckInOutData=Transaction.objects.filter(UserID__exact=int(userid),TTime__gte=dt1,TTime__lte=dt2).order_by('TTime')
    #CheckInOutData=CheckInOutData.filter(Q(SN=None)|Q(SN__Purpose=9)|Q(SN__Purpose=3)|Q(SN__Purpose=4)|Q(SN__Purpose=5)|Q(SN__Purpose=6)|Q(SN__Purpose=None))
    l_CheckInOutData=len(CheckInOutData)

    j=0
    #print "%s Transaction record=%s"%(UserID,len(CheckInOutData))
#    if settings.DATABASE_ENGINE == 'ado_mssql':
        #for t in CheckInOutData:    #解决SQL Server没有执行SQL的问题
        #j+=1
        #if j>0:
            #break
    try:

        WorkTimeZone = GetUserScheduler(UserID, d1-datetime.timedelta(days=1),d2, UserSchPlan['HasHoliday'])
        #print "WorkTimeZone:%s"%WorkTimeZone
        LoadUserException(UserID,d1,d2)
        Calc()
    except Exception, e:
        import traceback;traceback.print_exc()
        print "==========calc erro===========%s,userid====%d"%(e,userid)
        pass


def GetRptIndex(AttAbnomiteRptItems):
    global AttAbnomiteRptIndex
#    global AttAbnomiteRptItems
    #for t in AttAbnomiteRptIDs:
        #j=0
        #for f in AttAbnomiteRptItems:
            #if f['LeaveId']==t:
                #AttAbnomiteRptIndex[t]=j
                #break
            #j+=1

    j=0
    for f in AttAbnomiteRptItems:
#        print "==========",f['LeaveId'],f['LeaveName']
        AttAbnomiteRptIndex[f['LeaveId']]=j
        j+=1
    return AttAbnomiteRptIndex

#def PrepareCalcDate(u,d1,d2,itype,isForce):
    #global StartDate,EndDate
    #et=None
    #nt=trunc(datetime.datetime.now())
    #if isForce:
        #if d2<nt:
            #EndDate=trunc(d2)
        #elif d2>=nt:
            #EndDate=nt
        #if StartDate<=EndDate:
            #StartDate=StartDate-datetime.timedelta(1)
            #sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            #customSql(sql)
        #else:
            #return False
        #return True
##    attlog=attCalcLog.objects.extra(where=['UserID IN (%s)'%sUserID])
    #attlog=attCalcLog.objects.filter(UserID=u,EndDate__gte=nt-datetime.timedelta(60),Type=itype)
    #et=None
    #for t in attlog:
        #t.EndDate=checkTime(t.EndDate)
        #if et==None:
            #et=t.EndDate
        #elif et<t.EndDate:
            #et=t.EndDate
    ##if et!=None:
    ##    et=checkTime(et)
    #if et==None:
        #if d2<nt:
            #EndDate=d2
        #elif d2>=nt:
            #EndDate=nt
        #if StartDate<=EndDate:
            #sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table,u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
            #customSql(sql)
        #else:
            #return False
    #else:
        #if d2<=et or et>=nt:#-datetime.timedelta(1):
            #return False
        #elif d2<nt:
            #StartDate=et-datetime.timedelta(1)    #往前多统计一天
            #EndDate=d2
        #elif d2>=nt:
            #StartDate=et-datetime.timedelta(1)
            #EndDate=nt
        #if StartDate<EndDate:
            #sql="update %s set enddate='%s',opertime='%s' where userid=%s and type=%s"%(attCalcLog._meta.db_table,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),u,itype)
            #customSql(sql)
        #else:
            #return False
    #return True

    
def PrepareCalcDate(u,d1,d2,itype,isForce):
    from mysite.att.models import attCalcLog
    from mysite.iclock.sql import PrepareCalcDate_sql
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
            sql=PrepareCalcDate_sql(StartDate,EndDate,nt,u,itype)   
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
        sql=PrepareCalcDate_sql(StartDate,EndDate,nt,u,itype)
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
#        print "0000000000000",calcdate
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
#        print "3333333333333333",calcdate
        if len(calcdate)>1:   #如果超过两天未统计就取两端的日期
            StartDate=calcdate[0]
            EndDate=calcdate[-1]
        else:
            StartDate=calcdate[0]    
            EndDate=calcdate[0]
        sql=''    
        if StartDate<=EndDate and ((len(calcdate)>1) or (len(calcdate)==1 and flag==0)):
            sql=PrepareCalcDate_sql(StartDate,EndDate,nt,u,itype)
            if sql:
                customSql(sql)

#        elif flag!=1:
#            return False
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
#    print "end=====",StartDate,EndDate
    return True
    
def PrepareCalcDateByDept(deptid,d1,d2,itype,isForce):
    from mysite.att.models import attCalcLog
    from mysite.iclock.sql import PrepareCalcDateByDept_sql
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
            sql=PrepareCalcDateByDept_sql(deptid,StartDate,EndDate,nt,itype)
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
            sql=PrepareCalcDateByDept_sql(deptid,StartDate,EndDate,nt,itype)
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
#                print 2222222222222,tt
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
            sql=PrepareCalcDateByDept_sql(deptid,StartDate,EndDate,nt,itype)
            if sql:    
                customSql(sql)
#        elif flag!=1:
#            return False
        StartDate=StartDate-datetime.timedelta(1)    #往前多统计一天
#    print "end=====",StartDate,EndDate
    return True
    
    
    

def GetExceptionIDS():
    global ExceptionIDs
    global LClasses1
    if LClasses1==[]:
        LClasses1=GetLeaveClasses(1)
    if ExceptionIDs==[]:
        ExceptionIDs.append(caeFreeOT)
        ExceptionIDs.append(caeOT)
        ExceptionIDs.append(caeOut)
        ExceptionIDs.append(caeBOut)
        for t in LClasses1:
            ExceptionIDs.append(t['LeaveId'])


#def MainCalc(sUserID,d1,d2,isForce=0):
def MainCalc(UserIDList,DeptIDList,d1,d2,isForce=0):
    """UserIDList like [1,2,3,4]  d1,d2 is date type"""
    from mysite.att.models import attShifts,attRecAbnormite,AttException,attCalcLog
    from mysite.iclock.sql import MainCalc_sql1,MainCalc_sql2,MainCalc_sql3
    global isCalcing
    d1=trunc(d1)
    d2=trunc(d2+datetime.timedelta(days=1))#datetime.datetime(d2.year,d2.month,d2.day,23,59,59,0)
    if d1>d2:
        return -1
#    if isForce==0 and (d2-d1).days>31:
#        return -2
    if d2>trunc(datetime.datetime.now()+datetime.timedelta(days=1)):
        return -3
    if not allowAction(d1,1,d2):
        return -4
    if isCalcing==1:
        return -5
    isCalcing=1
    global LeaveClasses,AttRule
    global AttAbnomiteRptItems
    global StartDate,EndDate
    global UserSchPlan
    global AttRule
    userids=[]
    StartDate=d1
    EndDate=d2
    if DeptIDList:
        calcDepts=[]
        for t in DeptIDList:
            StartDate=d1
            EndDate=d2
            if PrepareCalcDateByDept(t,d1,d2,0,isForce):
                calcDepts.append(t)
                if len(calcDepts)>300:
                    ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
                    len(ues)
                    for u in ues:
                        userids.append(u)
                    calcDepts=[]
        if len(calcDepts)>0:
            ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
            len(ues)
            for u in ues:
                userids.append(u)
    else:
        userids=UserIDList
    if userids==[]:
        isCalcing=0
        return 0
    if isForce:
        InitData()
    try:
        print "caculate processing....."
        global rmdattabnormite
        global rmdRecAbnormite
        AttRule=LoadAttRule()
        LeaveClasses=GetLeaveClasses(0)
        #AttAbnomiteRptItems=LoadCalcItems()
        AttAbnomiteRptItems=GetLeaveClasses()
        GetRptIndex(AttAbnomiteRptItems)
        GetDefaultSpecialIntervals();
    
        GetExceptionIDS()
        for u in userids:
            getattFields(attShifts,rmdattabnormite)
            StartDate=d1
            EndDate=d2
            u=int(u)
            UserSchPlan=LoadSchPlan(u,True,False)
            valid=bool(UserSchPlan['Valid'])
            print "current process user: %s  valid:%s"%(u,valid)
            if (not valid) or PrepareCalcDate(u,d1,d2,0,isForce):
#                sql="delete from %s where userid=%s and attdate>='%s' and attdate<='%s'"%(attShifts._meta.db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
#                customSql(sql)
#                sql="delete from %s where userid=%s and StartDate>='%s' and EndDate<='%s'"%(attCalcLog._meta.db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
#                customSql(sql)                
#                sql="delete from %s where userid=%s and attdate>='%s' and attdate<='%s'"%(attRecAbnormite._meta.db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
#                customSql(sql)
#                sql="delete from %s where userid=%s and attdate>='%s' and attdate<='%s'"%(AttException._meta.db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
#                customSql(sql)

                sql=MainCalc_sql1(attShifts._meta.db_table,u,StartDate,EndDate)
                customSql(sql)
                sql=MainCalc_sql2(attCalcLog._meta.db_table,u,StartDate,EndDate)
                customSql(sql)                
                sql=MainCalc_sql1(attRecAbnormite._meta.db_table,u,StartDate,EndDate)
                customSql(sql)
                sql=MainCalc_sql3(AttException._meta.db_table,u,StartDate,EndDate)
                customSql(sql)
                if valid:
                    PrepareUserCalc(u,StartDate,EndDate)
    except:
        import traceback;traceback.print_exc()
    isCalcing=0
    return len(userids)

def getValidValue(value):
    if not value:return ""
    if type(value)==type(1):
        return int(value)
    if settings.DATABASE_ENGINE=='ibm_db_django':
        value=float(value)
    return value
#汇总统计数据
def SaveValue(dictv,value):
    from decimal import ROUND_HALF_UP,Decimal
    if value==None or value=="" or value=='null':
        value=0
    if dictv==None or dictv=="" or dictv=='null':
        dictv=0
    if type(value)==type(1):
        value=int(value)
    else:
        value=float(value)
    Result=""
    dictv=float(dictv)
    if dictv+value==0:
        return '0.0'
    else:
        Result=dictv+value
        
        return str(Decimal(str(Result)).quantize(Decimal('0.0'),ROUND_HALF_UP))

def formatdTime(value):
    if value=='' or value==0:
        return value
    #print "value:%s type:%s"%(value,type(value))
    t='%s:%.2d'%(int(float(value)/60),int(float(value)%60))
    return t
#新班次详情    
def CalcAttShiftsReportItem(request,deptids,userids,d1,d2,reportType=0,totalall=False):
    from mysite.att.models import attShifts,AttException
    global AbnomiteRptItems
    global AttAbnomiteRptIndex
    global ExceptionIDs
    global AttRule
    global schClasses
    preDate=MinDate
    preUserid=0
    AttRule=LoadAttRule()
    schClasses=GetSchClasses()
    if AbnomiteRptItems==[]:
        AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
#        ids.sort()
        ot=['UserID__DeptID','UserID__PIN','AttDate']
        attshifts=attShifts.objects.filter(UserID__in=ids,AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
        attExcept=AttException.objects.filter(UserID__in=ids,AttDate__gte=d1,AttDate__lte=d2).order_by('UserID')
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
        deptids=[]
        for d in deptIDS:#支持选择多部门
            deptids+=getAllAuthChildDept(d,request)
        ot=['UserID__DeptID','UserID__PIN','AttDate']
        attshifts=attShifts.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2).order_by(*ot)
        attExcept=AttException.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2).order_by('UserID')
    
    len(attshifts)
    len(attExcept)
    Result={}
    re=[]
#分页        
    try:
        offset = int(request.REQUEST.get('p', 1))
    except:
        offset=1
    if not totalall:
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #导出时使用
        paginator = Paginator(attshifts, limit)
        item_count = paginator.count
        pgList = paginator.page(offset)
        page_count=paginator.num_pages
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
    
    fieldNames,fieldCaptions,rt=ConstructAttshiftsFields1()
    disabledCols=FetchDisabledFields(request.user,'attShifts')
    Result['fieldnames']=fieldNames
    Result['fieldcaptions']=fieldCaptions
    Result['disableCols']=disabledCols
    for t in pgList.object_list:
        r=rt.copy()
        eid=int(t.UserID_id)
        e=Employee.objByID(eid)
        r['userid']=eid
        r['DeptID']=e.DeptID.name
        r['PIN']=e.PIN
        r['EName']=e.EName
        r['AttDate']=t.AttDate.date()
        r['SchId']=schClasses[FindSchClassByID(t.SchId_id)]['SchName']
        r['Schid']=getValidValue(t.SchId_id)
        r['ClockInTime']=t.ClockInTime.strftime('%H:%M:%S')
        r['ClockOutTime']=t.ClockOutTime.strftime('%H:%M:%S')
        r['StartTime']=""
        r['EndTime']=""
        if t.StartTime:
            r['StartTime']=t.StartTime.strftime('%H:%M:%S')
        if t.EndTime:    
            r['EndTime']=t.EndTime.strftime('%H:%M:%S')
        r['WorkDay']=getValidValue(t.WorkDay)
        r['RealWorkDay']=getValidValue(t.RealWorkDay)
        r['Late']=getValidValue(t.Late)
        r['Early']=getValidValue(t.Early)
        r['Absent']=IsYesNo(t.Absent)
        r['OverTime']=getValidValue(t.OverTime)
        r['WorkTime']=getValidValue(t.WorkTime)
        r['MustIn']=IsYesNo(t.MustIn)
        r['MustOut']=IsYesNo(t.MustOut)
        r['SSpeDayNormal']=getValidValue(t.SSpeDayNormal)
        r['SSpeDayWeekend']=getValidValue(t.SSpeDayWeekend)
        r['SSpeDayHoliday']=getValidValue(t.SSpeDayHoliday)
        r['AttTime']=hourAndMinute(t.AttTime)
        r['SSpeDayNormalOT']=getValidValue(t.SSpeDayNormalOT)
        r['SSpeDayWeekendOT']=getValidValue(t.SSpeDayWeekendOT)
        r['SSpeDayHolidayOT']=getValidValue(t.SSpeDayHolidayOT)
        #合并各种假
        excidlist=[]
#        if (r['AttDate']<>preDate) or (t.UserID_id<>preUserid):
        for tt in attExcept:
            if (tt.AttDate.date()<>r['AttDate']) or (tt.UserID_id<>t.UserID_id) or (t.SchId_id<>tt.schid):
                continue
            if tt.ExceptionID and tt.ExceptionID>0:
                fname=str(tt.ExceptionID)
                v=tt.InScopeTime
                r['Leave_'+fname]=SaveValue(r['Leave_'+fname],v)
                if not tt.ExceptionID in excidlist:
                    excidlist.append(tt.ExceptionID)
        for exid in excidlist:
            ve=r['Leave_'+str(exid)]
            if ve:
                r['Leave_'+str(exid)]=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['MinUnit'],
                                         AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['RemaindProc'])

        for ttt in r.keys():              #不显示空的数据
            if not r[ttt]:r[ttt]=""
            elif type(r[ttt])==type(1.0):
                if r[ttt]>int(r[ttt]):
                    r[ttt]=str(r[ttt])
        
        preDate=r['AttDate']
        preUserid=t.UserID_id
        re.append(r.copy())
    Result['datas']=re
    return Result
    
#考勤统计汇总/每日统计报表
def CalcReportItem(request,deptids,userids,d1,d2,reportType=0,totalall=False):
    from mysite.att.models import AttException,attShifts
    from mysite.iclock.sql import CalcReportItem_sql
    global AbnomiteRptItems
    global ExceptionIDs
    global AttRule
    global schClasses
    AttRule=LoadAttRule()
    #if AbnomiteRptItems==[]:
    AbnomiteRptItems=GetLeaveClasses()
    GetRptIndex(AbnomiteRptItems)
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
#        ids.sort()
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
        deptids=deptIDS
#        print "deptIDS:%s"%deptIDS
#        for d in deptIDS:#支持选择多部门
#            deptids+=getAllAuthChildDept(d,request)
        #print "======================deptids:%s"%deptids
        ot=['PIN','DeptID']
        ids=Employee.objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)
        #print len(ids)
    Result={}
    re=[]
    try:
    #分页        
        try:
            offset = int(request.REQUEST.get('p', 1))
        except:
            offset=1
        #print "offset:%s"%offset
        uids=[]
        k=0
        if not totalall:
            limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #导出时使用
            ids=ids[(offset-1)*limit:offset*limit]
            item_count =len(ids)
            if item_count % limit==0:
                page_count =item_count/limit
            else:
                page_count =int(item_count/limit)+1            
            
            if offset>page_count and page_count:offset=page_count
            
            Result['item_count']=item_count
            Result['page']=offset
            Result['limit']=limit
            Result['from']=(offset-1)*limit+1
            Result['page_count']=page_count
        for u in ids:
            uids.append(u)
        #print "reportType:%s"%reportType
        if reportType==0:  #考勤统计汇总
            r,Fields,Capt=ConstructFields()
        elif reportType==1:
            r,Fields,Capt=ConstructFields1(d1,d2)
        elif reportType==2:
            r,Fields,Capt=ConstructBaseFields2(d1,d2)
        #print "Result['fieldnames']=",Fields
        Result['fieldnames']=Fields
        Result['fieldcaptions']=Capt
        Result['datas']=r
        if reportType==1:
            lc=LoadCalcItems()
            GetExceptionIDS()

        for uid in uids:
            uid=int(uid)
            attExcept=AttException.objects.filter(UserID=uid,AttDate__gte=d1,AttDate__lte=d2).order_by('UserID')
#            len(attExcept)
#
#            sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u.ssn as ssn,s.schid as schid,s.attdate as attdate,d.deptname as deptname,s.clockInTime as clockintime,s.clockouttime as clockouttime,
#            s.starttime as starttime,s.endtime as endtime,s.workday as workday,s.realworkday as realworkday,s.noin as noin,s.noout as noout,
#            s.early as early,s.late as late,s.absent as absent,s.absentr as absentr,s.overtime as overtime,s.exceptionid as exceptionid,s.mustin as mustin,s.mustout as mustout,  
#            s.worktime as worktime,s.atttime as atttime,s.workmins as workmins,s.SSpeDayNormal as SSpeDayNormal,s.SSpeDayWeekend as SSpeDayWeekend,s.SSpeDayHoliday as SSpeDayHoliday ,s.symbol as symbol,
#            s.SSpeDayNormalOT as SSpeDayNormalOT,s.SSpeDayWeekendOT as SSpeDayWeekendOT,s.SSpeDayHolidayOT as SSpeDayHolidayOT
#            from attshifts s,userinfo u,Departments d where u.userid=s.userid and d.deptID=u.defaultdeptid and  """
#            if settings.DATABASE_ENGINE=="oracle":
#                sql=sql+""" s.attdate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and s.attdate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
#            else:
#                sql=sql+""" s.attdate>='%s' and s.attdate<='%s' and"""%(d1,d2)
#            
#            sql=sql+""" s.userid = %s order by u.badgenumber,u.defaultdeptid"""%(uid)
    #        print sql
    #        elif len(deptids)>0:
    #            sql=sql+""" u.defaultdeptid in (%s) order by u.badgenumber,u.defaultdeptid"""%(deptids)
#            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#                sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u."SSN" as ssn,s."SchId" as schid,s."AttDate" as attdate,d."DeptName" as deptname,s."ClockInTime" as clockintime,s."ClockOutTime" as clockouttime,
#                        s."StartTime" as starttime,s."EndTime" as endtime,s."WorkDay" as workday,s."RealWorkDay" as realworkday,s."NoIn" as noin,s."NoOut" as noout,
#                        s."Early" as early,s."Late" as late,s."Absent" as absent,s."AbsentR" as absentr,s."OverTime" as overtime,s."ExceptionID" as exceptionid,s."MustIn" as mustin,s."MustOut" as mustout,  
#                        s."WorkTime" as worktime,s."AttTime" as atttime,s."WorkMins" as workmins,s."SSpeDayNormal" as SSpeDayNormal,s."SSpeDayWeekend" as SSpeDayWeekend,s."SSpeDayHoliday" as SSpeDayHoliday ,s."Symbol" as symbol,
#                        s."SSpeDayNormalOT" as SSpeDayNormalOT,s."SSpeDayWeekendOT" as SSpeDayWeekendOT,s."SSpeDayHolidayOT" as SSpeDayHolidayOT
#                        from attshifts s,userinfo u,Departments d where u.userid=s.userid and d."DeptID"=u.defaultdeptid and  """
#            else:
#                sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u.ssn as ssn,s.schid as schid,s.attdate as attdate,d.deptname as deptname,s.clockInTime as clockintime,s.clockouttime as clockouttime,
#                        s.starttime as starttime,s.endtime as endtime,s.workday as workday,s.realworkday as realworkday,s.noin as noin,s.noout as noout,
#                        s.early as early,s.late as late,s.absent as absent,s.absentr as absentr,s.overtime as overtime,s.exceptionid as exceptionid,s.mustin as mustin,s.mustout as mustout,  
#                        s.worktime as worktime,s.atttime as atttime,s.workmins as workmins,s.SSpeDayNormal as SSpeDayNormal,s.SSpeDayWeekend as SSpeDayWeekend,s.SSpeDayHoliday as SSpeDayHoliday ,s.symbol as symbol,
#                        s.SSpeDayNormalOT as SSpeDayNormalOT,s.SSpeDayWeekendOT as SSpeDayWeekendOT,s.SSpeDayHolidayOT as SSpeDayHolidayOT
#                        from attshifts s,userinfo u,Departments d where u.userid=s.userid and d.deptID=u.defaultdeptid and  """
#                
#            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
#                sql=sql+""" s.attdate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and s.attdate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
#            elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#                sql=sql+""" s."AttDate">='%s' and s."AttDate"<='%s' and"""%(d1,d2)
#            else:
#                sql=sql+""" s.attdate>='%s' and s.attdate<='%s' and"""%(d1,d2)
#            sql=sql+""" s.userid = %s order by u.badgenumber,u.defaultdeptid"""%(uid)
            
            sql=CalcReportItem_sql(d1,d2,uid)
            cs=customSql(sql,False)
            
            desc=cs.description
            fldNames={}
            i=0
            for c in desc:
    #            print c[0]
                fldNames[c[0].lower()]=i
                i=i+1
            rmdAttday=r.copy()
            row=0
            rows=cs.fetchall()
    #        print "rows==",rows
            if not rows:
                emp=Employee.objByID(uid)
                for y in rmdAttday.keys():
                    rmdAttday[y]=''
                rmdAttday['userid']=uid
                rmdAttday['deptid']=emp.DeptID.name
                rmdAttday['badgenumber']=emp.PIN
                rmdAttday['username']=emp.EName
                
            for t in rows:
                row+=1
                if rmdAttday['userid']==-1:
                    rmdAttday['userid']=t[fldNames['userid']]
                    rmdAttday['deptid']=t[fldNames['deptname']]
                    rmdAttday['badgenumber']=t[fldNames['pin']]
                    rmdAttday['username']=t[fldNames['name']]
                    
                if reportType==0 or reportType==1:
                    rmdAttday['duty']=SaveValue(rmdAttday['duty'],t[fldNames['workday']])
                    rmdAttday['realduty']=SaveValue(rmdAttday['realduty'],t[fldNames['realworkday']])
                    rmdAttday['late']=SaveValue(rmdAttday['late'],t[fldNames['late']])
                    rmdAttday['early']=SaveValue(rmdAttday['early'],t[fldNames['early']])
    #                try:
    #                    rmdAttday['SSpeDayHoliday']=SaveValue(rmdAttday['SSpeDayHoliday'],t[fldNames['sspedayholiday']])
    #                except:
    #                    #print "rmdAttday:%s"%rmdAttday
    #                    import traceback;traceback.print_exc()
                    if t[fldNames['absent']]>0:
                        try:
#                            wd=attShifts.objects.filter(AttDate__exact=t[fldNames['attdate']],UserID=t[fldNames['userid']])
#                            wdmins=0                
#                            for w in wd:
#                                wdmins=wdmins+w.AttTime    
#                            #print "AbnomiteRptItems['1004']['MinUnit']:",AbnomiteRptItems[AttAbnomiteRptIndex[1004]]['MinUnit']
#                            v=NormalAttValue(t[fldNames['absent']],AbnomiteRptItems[AttAbnomiteRptIndex[1004]]['MinUnit'],
#                                                              AbnomiteRptItems[AttAbnomiteRptIndex[1004]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[1004]]['RemaindProc'],auHour,wdmins)
#                                      
#                        
                            rmdAttday['absent']=SaveValue(rmdAttday['absent'],t[fldNames['absent']])
                        except:
                            import traceback;traceback.print_exc()
                    rmdAttday['overtime']=SaveValue(rmdAttday['overtime'],t[fldNames['overtime']])
                    #print "rmdAttday['overtime']:%s"%rmdAttday['overtime']
                    rmdAttday['SSpeDayNormalOT']=SaveValue(rmdAttday['SSpeDayNormalOT'],t[fldNames['sspedaynormalot']])
                    rmdAttday['SSpeDayWeekendOT']=SaveValue(rmdAttday['SSpeDayWeekendOT'],t[fldNames['sspedayweekendot']])
                    rmdAttday['SSpeDayHolidayOT']=SaveValue(rmdAttday['SSpeDayHolidayOT'],t[fldNames['sspedayholidayot']])

    #                sch_t=t[fldNames['schid']]
    #                if sch_t and sch_t>0:
    #                    rmdAttday['sch_%d'%sch_t]=sch_t

                #if t[fldNames['mustin']]==True and reportType==0:
                    #rmdAttday['dutyinout']=SaveValue(rmdAttday['dutyinout'],1)
                #if t[fldNames['mustout']]==True and reportType==0:
                    #rmdAttday['dutyinout']=SaveValue(rmdAttday['dutyinout'],1)
                #if t[fldNames['mustin']]==True and t[fldNames['starttime']]!=None and reportType==0:
                    #rmdAttday['clockin']=SaveValue(rmdAttday['clockin'],1)
                #if t[fldNames['mustout']]==True and t[fldNames['endtime']]!=None and reportType==0:
                    #rmdAttday['clockout']=SaveValue(rmdAttday['clockout'],1)
                #if t[fldNames['mustin']]==True and t[fldNames['starttime']]==None and reportType==0:
                    #rmdAttday['noin']=SaveValue(rmdAttday['noin'],1)
                #if t[fldNames['mustout']]==True and t[fldNames['endtime']]==None and reportType==0:
                    #rmdAttday['noout']=SaveValue(rmdAttday['noout'],1)
                
                if reportType==0:
                    if t[fldNames['mustin']]:
                        rmdAttday['dutyinout']=int(float(SaveValue(rmdAttday['dutyinout'],1)))
                        rmdAttday['clockin']=int(float(SaveValue(rmdAttday['clockin'],1)))
                    if t[fldNames['mustout']]:
                        rmdAttday['dutyinout']=int(float(SaveValue(rmdAttday['dutyinout'],1)))
                        rmdAttday['clockout']=int(float(SaveValue(rmdAttday['clockout'],1)))
      
                        
                    #rmdAttday['noin']=SaveValue(t[fldNames['noin']],1)
                    #rmdAttday['noout']=SaveValue(t[fldNames['noout']],1)
                        
                    if t[fldNames['mustin']] and t[fldNames['starttime']] is None:
                        rmdAttday['noin']=int(float(SaveValue(rmdAttday['noin'],1)))
                    if t[fldNames['mustout']] and t[fldNames['endtime']] is None:
                        rmdAttday['noout']=int(float(SaveValue(rmdAttday['noout'],1)))
                    rmdAttday['worktime']=SaveValue(rmdAttday['worktime'],t[fldNames['worktime']])
                    rmdAttday['workmins']=SaveValue(rmdAttday['workmins'],t[fldNames['workmins']])
            
                    #rmdAttday['SSpeDayNormal']=SaveValue(rmdAttday['SSpeDayNormal'],t[fldNames['sspedaynormal']])
                    #rmdAttday['SSpeDayWeekend']=SaveValue(rmdAttday['SSpeDayWeekend'],t[fldNames['sspedayweekend']])
                    
                if reportType==2:
                    dt=t[fldNames['attdate']]
                    dof=str(dt.day)
                    tt=t[fldNames['schid']]
                    if tt:
                        schindex=FindSchClassByID(int(tt))
                        
                        rmdAttday[dof]=schClasses[schindex]['SchName']
                if reportType==1:
                    dt=t[fldNames['attdate']]
                    dof=str(dt.day)
                    tt=t[fldNames['symbol']]
                    if tt:
                        rmdAttday[dof]=rmdAttday[dof]+tt

                    #if t[fldNames['absent']]!=None:
                        #if t[fldNames['absent']]>0:
                            #rmdAttday[dof]=rmdAttday[dof]+GetCalcRptSymbol(lc,1004)
                    #elif t[fldNames['late']]!=None:
                        #if t[fldNames['late']]>0:
                            #rmdAttday[dof]=rmdAttday[dof]+GetCalcRptSymbol(lc,1001)
                    #elif  t[fldNames['early']]!=None:
                        #if t[fldNames['early']]>0:
                            #rmdAttday[dof]=rmdAttday[dof]+GetCalcRptSymbol(lc,1002)
                    #elif t[fldNames['realworkday']]!=None and t[fldNames['workday']]!=None:
                        #if t[fldNames['realworkday']]>=t[fldNames['workday']]:
                            #rmdAttday[dof]=rmdAttday[dof]+GetCalcRptSymbol(lc,1000)
                    #if t[fldNames['exceptionid']] in ExceptionIDs:
                        #rmdAttday[dof]=GetCalcRptSymbol(lc,1003)
            if row>0 and (reportType==0 or reportType==1):
                
                for ex in attExcept: 
                    excidlist=[]
                    if ex.UserID_id!=rmdAttday['userid']:
                        continue
                    exceptid=ex.ExceptionID
                    wd=attShifts.objects.filter(AttDate__exact=ex.AttDate,UserID=ex.UserID)
                    wdmins=0                
                    for w in wd:
                        wdmins=wdmins+w.AttTime                
                    #print "wdmins:%s"%wdmins
                    if exceptid in [caeFreeOT,caeOT,caeOut,caeBOut]:
                        pass
                    elif exceptid>0:
                        if exceptid in AttAbnomiteRptIndex:
                            if (reportType==0) or (reportType==1):
                                if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindCount']==0:
                                    v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
                                             AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'],auHour,wdmins)
                                else:
                                    v=ex.InScopeTime
                                    v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
                                             AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'],auHour,wdmins)
    #                                if not exceptid in excidlist:
    #                                    excidlist.append(exceptid)
                                rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
    #                        if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1 and AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindCount']==0:    #只有计为请假时才累计 2009.5.6
    #                            v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
    #                                     AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'],auHour,wdmins)
    #                            rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
    #                        if excidlist:
    #                            for exid in excidlist:
    #                                ve=rmdAttday['Leave_'+str(exid)]
    #                                rmdAttday['Leave_'+str(exid)]=NormalAttValue(ve,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['MinUnit'],
    #                                                     AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exid]]['RemaindProc'],auHour,wdmins)
                                if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1:    
                                    v=NormalAttValue(ex.InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
                                             AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'],auHour,wdmins)
                                    rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
            if rmdAttday['userid']>-1:
                if reportType==0:
                    rmdAttday['worktime']=formatdTime(rmdAttday['worktime'])
                    rmdAttday['workmins']=formatdTime(rmdAttday['workmins'])
                for ttt in rmdAttday.keys():              
                    if type(rmdAttday[ttt])==type(1.0):
                        if rmdAttday[ttt]>int(rmdAttday[ttt]):
                            rmdAttday[ttt]=smart_str(rmdAttday[ttt])

                re.append(rmdAttday.copy())
        Result['datas']=re
        if reportType==0:
            Result['disableCols']=FetchDisabledFields(request.user,'attTotal')
        elif reportType==1:
            Result['disableCols']=FetchDisabledFields(request.user,'attDailyTotal')
        elif reportType==2:
            Result['disableCols']=[]
        #print "Result[fieldsname]",Result['fieldnames']
        return Result
    except:
        import traceback;traceback.print_exc()

def CalcLeaveReportItem(request,deptids,userids,d1,d2,reportType=0,totalall=False):
    global AbnomiteRptItems
    global ExceptionIDs
    global AttRule
    global schClasses
    global LClasses1
    from mysite.att.models import AttException,attShifts
    AttRule=LoadAttRule()
    #if AbnomiteRptItems==[]:
    AbnomiteRptItems=GetLeaveClasses()
    GetRptIndex(AbnomiteRptItems);
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
        emps=AttException.objects.filter(AttDate__gte=d1,AttDate__lte=d2).values('UserID').annotate().filter(UserID__in=ids)
#        ids.sort()
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
        deptids=deptIDS
#        for d in deptIDS:#支持选择多部门
#            deptids+=getAllAuthChildDept(d,request)
        ot=['UserID__DeptID','UserID__PIN']
        emps=AttException.objects.filter(UserID__DeptID__in=deptids,AttDate__gte=d1,AttDate__lte=d2).values('UserID').annotate().order_by(*ot)
    #print len(emps)
    Result={}
    re=[]
    
    try:
        offset = int(request.REQUEST.get('p', 1))
    except:
        offset=1
    #print "offset,",offset
    uids=[]
    k=0       
#    print "totalall,",totalall 
    if not totalall:
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #导出时使用
        item_count =len(emps)
        if item_count % limit==0:
            page_count =item_count/limit
        else:
            page_count =int(item_count/limit)+1
        if offset>page_count and page_count:offset=page_count
        #print "offset,",offset
#        print "limit,",limit
        emps=emps[(offset-1)*limit:offset*limit]
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
    r,Fields,Capt=ConstructFields()
    r,FieldNames,FieldCaption=ConstructLeaveFields()
    #if LClasses1==[]:
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        FieldNames.append(fName)
        r[fName]=''
        FieldCaption.append(t['LeaveName'])
        
    #print "FieldNames:",FieldNames    
    Result['fieldnames']=FieldNames
    Result['fieldcaptions']=FieldCaption
    Result['datas']=r
    for uid in emps:
        uid=int(uid['UserID'])
        try:
            emp=Employee.objByID(uid)
        except: 
            continue
        rmdAttday=r.copy()
        attExcept=AttException.objects.filter(UserID=uid,AttDate__gte=d1,AttDate__lte=d2)#.values('ExceptionID').annotate(inscopetime=Sum('InScopeTime'))
        
        for y in rmdAttday.keys():
            rmdAttday[y]=''
        rmdAttday['userid']=uid
        rmdAttday['deptid']=emp.DeptID.name
        rmdAttday['badgenumber']=emp.PIN
        rmdAttday['username']=emp.EName
        #rmdAttday['ssn']=emp.SSN
        try:        
            for ex in attExcept:             
                    exceptid=ex.ExceptionID
                   
                    wd=attShifts.objects.filter(AttDate__exact=ex.AttDate,UserID=ex.UserID)
                    wdmins=0
                    
                    for w in wd:
                        wdmins=wdmins+w.AttTime
                    
                    InScopeTime=ex.InScopeTime
                    if exceptid in [caeFreeOT,caeOT,caeOut,caeBOut]:
                        continue
                    elif exceptid>0:
                        
                        v=NormalAttValue(InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['MinUnit'],
                            AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['RemaindProc'],auHour,wdmins)
                        rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
                        
                        if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1:    #只有计为请假时才累计 2009.5.6
                            v=NormalAttValue(InScopeTime,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['MinUnit'],
                                     AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['Unit'] ,AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]['RemaindProc'],auHour,wdmins)
                            rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
            re.append(rmdAttday.copy())
        except:
            import traceback;traceback.print_exc()
    Result['datas']=re
    Result['disableCols']=[]
    return Result

        
def ConstructFields():
    """为汇总报表构造字段  """
    global LClasses1

    r,FieldNames,FieldCaption=ConstructBaseFields()
    #if LClasses1==[]:
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        FieldNames.append(fName)
        r[fName]=''
        FieldCaption.append(u"%s"%_(t['LeaveName']))
    """因有的单位时段太多暂不统计时段"""
    #schClasses=GetSchClasses()
    #for t in schClasses:
        #fName='sch_'+str(t['schClassID'])
        #FieldNames.append(fName)
        #r[fName]=''
        #FieldCaption.append(t['SchName'])
        
#    print FieldNames
    return [r,FieldNames,FieldCaption]

def ConstructFields1(d1,d2):
    """为每日明细汇总表构造字段  """
    global LClasses1
    r,FieldNames,FieldCaption=ConstructBaseFields1(d1,d2)
    #if LClasses1==[]:
    LClasses1=GetLeaveClasses(1)
    
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        FieldNames.append(fName)
        r[fName]=''
        FieldCaption.append(u"%s"%_(t['LeaveName']))
    #schClasses=GetSchClasses()
    #for t in schClasses:
        #fName='sch_'+str(t['schClassID'])
        #FieldNames.append(fName)
        #r[fName]=''
        #FieldCaption.append(t['SchName'])
#    print FieldNames
    return [r,FieldNames,FieldCaption]


def ConstructAttshiftsFields1():
    """为班次明细表构造字段  """
    FieldCaptions= FetchModelFieldsCaption('attShifts')
    FieldNames=FetchModelFields('attShifts')
    FieldNames.insert(0,'userid')
    FieldCaptions.insert(0,'UserID')
    global LClasses1
    r={}
    for t in FieldNames:
        r[t]=''
    #if LClasses1==[]:
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        FieldNames.append(fName)
        r[fName]=''
        FieldCaptions.append(u"%s"%_(t['LeaveName']))

    return FieldNames,FieldCaptions,r

#取统计项目计算单位--begin
def GetAttUnitText(AttUnit):
    Result=GetUnitText(int(AttUnit))
    return unicode(Result)

def GetCalcUnit():
    #d={}
    #lc=LoadCalcItems()
    #for t in lc:
        #d[t['LeaveName']]=GetAttUnitText(int(t['Unit']))

    lc=GetLeaveClasses(0)
    result=''
    for t in lc:
        result=result+','+t['LeaveName']+':'+GetAttUnitText(int(t['Unit']))
        #d[t['LeaveName']]=GetAttUnitText(int(t['Unit']))
    return result[1:]

def GetCalcSymbol():
    d={}
    #lc=LoadCalcItems()
    lc=GetLeaveClasses()
    result=''
    for t in lc:
        result=result+','+t['LeaveName']+':'+t['ReportSymbol']
    #    d[t['LeaveName']]=t['ReportSymbol']
    #result=', '.join([ "%s:%s"% (k,v) for k ,v in d.items()])
    return result[1:]

def GetCalcRptSymbol(lclass,LeaveID):
    d={}
#    lc=LoadCalcItems()
    for t in lclass:
        if LeaveID==t['LeaveId']:
            return t['ReportSymbol']
    return ''
    





def PriReportCalc(UserIDList,DeptIDList,d1,d2,isForce=0):
    """UserIDList like [1,2,3,4]  d1,d2 is date type"""
    d1=trunc(d1)
    d2=trunc(d2)#datetime.datetime(d2.year,d2.month,d2.day,23,59,59,0)
    if d1>d2:
        return -1
    if d2>trunc(datetime.datetime.now()):
        return -3
#    if not allowAction(d1,1,d2):
#        return -4
    
    global LeaveClasses,AttRule
    global StartDate,EndDate
    global UserSchPlan
    global AttRule
    userids=[]
    StartDate=d1
    EndDate=d2
    if DeptIDList:
        calcDepts=[]
        for t in DeptIDList:
            if PrepareCalcDateByDept(t,d1,d2,1,isForce):
                calcDepts.append(t)
                if len(calcDepts)>300:
                    ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
                    for u in ues:
                        userids.append(u)
                    calcDepts=[]
        if len(calcDepts)>0:
            ues=Employee.objects.filter(DeptID__in=calcDepts,OffDuty__lt=1 ).values_list('id', flat=True).order_by('id')
            for u in ues:
                userids.append(u)
    else:
        userids=UserIDList
    if userids==[]:
        return 0
    if isForce:
        InitData()
    global rmdattabnormite
    global rmdRecAbnormite
    AttRule=LoadAttRule()

    for u in userids:
#        getattFields(attShifts,rmdattabnormite)
        StartDate=d1
        EndDate=d2
        u=int(u)
        if  PrepareCalcDate(u,d1,d2,1,isForce):
            sql="delete from %s where userid=%s and attdate>='%s' and attdate<='%s'"%(attpriReport._meta.db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
            customSql(sql)
            PrepareUserPriReportCalc(u,StartDate,EndDate)
    return len(userids)


def PrepareUserPriReportCalc(userid,d1,d2):
    from mysite.att.models import EmpSpecDay,Holiday as holidays
    global CheckInOutData          #考勤记录
    global ExcepData               #请假记录
    global qryAudit
    global UserSchPlan
    global WorkTimeZone
    global UserID
    WorkTimeZone=[]
    UserID=int(userid)
    tHoliday=holidays.objects.all().order_by('start_time')
    ExcepData=EmpSpecDay.objects.filter(emp=UserID,start__gte=d1-datetime.timedelta(days=100),end__lte=d2+datetime.timedelta(days=100)).order_by('start')
    #qryAudit=AuditedExc.objects.filter(UserID=UserID,CheckTime__gte=d1-datetime.timedelta(days=4),CheckTime__lte=d2+datetime.timedelta(days=1),NewExcID__gt=0).order_by('CheckTime')
    CheckInOutData=Transaction.objects.filter((Q(Verify__gt=5)|Q(Verify__lt=5)),UserID=UserID,TTime__gte=d1,TTime__lte=d2+datetime.timedelta(days=1)).order_by('TTime')
    AddCheckInOutData=Transaction.objects.filter(UserID=UserID,TTime__gte=d1,TTime__lte=d2+datetime.timedelta(days=1),Verify=5).order_by('TTime')

#    if settings.DATABASE_ENGINE == 'ado_mssql':
#        l=len(CheckInOutData)
    WorkTimeZone = GetUserScheduler(UserID, d1-datetime.timedelta(days=1),d2, True)
    try:
        dict={'UserID':UserID,
              'AttDate':d1,
              'AttChkTime':'',
              'AttAddChkTime':'',
              'AttLeaveTime':'',
              'SchName':'',
              'Reserved':''
              }
        d=d1
        re=[]
        #生成基本日历数据
        while d<=d2:
            dict['AttDate']=d
            re.append(dict.copy())
            d=d+datetime.timedelta(1)
        #生成原始考勤记录数据
        for t in CheckInOutData:
            ll=CheckData(t.TTime,re,None)
            if ll:
                for i in ll:
                    if len(re[i]['AttChkTime'])<90:
                        re[i]['AttChkTime']=re[i]['AttChkTime']+t.TTime.strftime('%H:%M:%S')+'  '
                        #为用户定制实现 标准版不用此功能
                        if len(re[i]['Reserved'])<35:
                            if t.WorkCode=='1':
                                re[i]['Reserved']=re[i]['Reserved']+'I'+t.TTime.strftime('%H:%M:%S')
                            elif t.WorkCode=='2':
                                re[i]['Reserved']=re[i]['Reserved']+'O'+t.TTime.strftime('%H:%M:%S')
                            
        for t in WorkTimeZone:
            ll=CheckData(t['TimeZone']['StartTime'],re,t['TimeZone']['EndTime'])
            if ll:
                for i in ll:#有可能一天有两个时段
                    if re[i]['AttDate'].date()==t['TimeZone']['StartTime'].date():
                        re[i]['SchName']=re[i]['SchName']+t['SchName']+'  '
        for t in ExcepData:
            ll=CheckData(t.start,re,t.end)
            for i in ll:
                re[i]['AttLeaveTime']=re[i]['AttLeaveTime']+t.start.strftime('%m-%d %H:%M')+' '+t.end.strftime('%m-%d %H:%M')+'   '
        
        for t in AddCheckInOutData:
            ll=CheckData(t.TTime,re,None)
            if ll:
                for i in ll:
                    if len(re[i]['AttChkTime'])<90:
                        re[i]['AttAddChkTime']=re[i]['AttAddChkTime']+t.TTime.strftime('%H:%M:%S')+'  '
                    if len(re[i]['Reserved'])<35:
                        if t.State=='I':
                            re[i]['Reserved']=re[i]['Reserved']+'I'+t.TTime.strftime('%H:%M:%S')
                        elif t.State=='O':
                            re[i]['Reserved']=re[i]['Reserved']+'O'+t.TTime.strftime('%H:%M:%S')

        
        sqls=""
        for t in re:
            sql,params=getSQL_insert_new(attpriReport._meta.db_table,t)
            customSqlEx(sql,params)
    except Exception, e:
        print "==========calc erro===========%s,userid====%d"%(e,userid)
        pass


def CheckData(st,Dict,et=None):
    j=0
    l=[]
    for d in Dict:
        if st.date()==d['AttDate'].date() and et==None:
            l.append(j)
            break
        if et!=None:
            if d['AttDate'].date()>=st.date() and d['AttDate'].date()<=et.date():
                l.append(j)
        j=j+1
    return l




#---------------------------------------------------End

def test():
    #global AttAbnomiteRptItems
    #qn = connection.ops.quote_name
    #field_names = [f.column for f in attShifts._meta.fields if not isinstance(f, AutoField)]
    #AttAbnomiteRptItems=LoadCalcItems()
    #GetRptIndex()
    #print AttAbnomiteRptItems[AttAbnomiteRptIndex[1000]]
#    r=NormalAttValue(3,0.1,auHour,rmTrunc)
    user=3
    r=attCalcLog.objects.extra(select={'EndDate':'select max(enddate) from attcalclog where userid=%s'%(user)},)



