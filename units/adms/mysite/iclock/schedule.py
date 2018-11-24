#!/usr/bin/python
# -*- coding: utf-8 -*-
from mysite.iclock.models import *
from mysite.iclock.tools import *
from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.utils.encoding import  force_unicode
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _
import datetime
from mysite.iclock.iutils import *
import copy
from mysite.iclock.datas import *
from django.contrib.auth.decorators import permission_required, login_required
#from mysite.utils import errorLog
from mysite.iclock.datasproc import *
from mysite.personnel.models import Employee


global SchedulerShifts
global FTTimeZones
LastZone = 1
LastZone1 = 2*60                
(TZNormal,TZInner)=range(2)     #TZInner is Inner TimeZone
BaseDate=datetime.datetime(2000,1,1,0,0,0)

@login_required
def addShiftTimeTable(request):
        try:
                global SchedulerShifts
                global FTTimeZones
                unit=int(request.POST.get('unit','1'))
                cycle=int(request.POST.get('cycle','1'))
                isOT=request.POST.get('is_OT','off')
                overtime=0
                if isOT=='on':
                        overtime=request.POST.get('OverTime','0')
                        if overtime!='':
                                overtime=int(overtime)
                SchID=int(request.POST.get('shift_id','0'))
                weekStartDay=int(request.POST.get('weekStartDay','0'))
                if unit==0:
                        rc=1
                elif unit==1:
                        rc=7
                else:
                        rc=31
                rc=rc*cycle
                SchedulerShifts=[]
                chklbSchClass=request.POST['sTimeTbl'].split(',')
                chklbDates=request.POST['sDates'].split(',')
                schClasses=GetSchClasses()
                getSchedulerShifts(SchID,unit,weekStartDay,overtime)
                deleteShiftDetail(SchID) 
                for t in chklbSchClass:
                        t=int(t)
                        j=FindSchClassByID(t)
                        st=schClasses[j]['TimeZone']['StartTime']
                        et=schClasses[j]['TimeZone']['EndTime']
                        for tt in chklbDates:
                                tt=int(tt)
                                starttime = st+datetime.timedelta(days=tt)
                                endtime = et+datetime.timedelta(days=tt)
                                if TestTimeZone(FTTimeZones,starttime,endtime):
                                        AddScheduleShift(SchedulerShifts, starttime, endtime,t,overtime)
                for i in range(len(SchedulerShifts)):
                        if (i==0) or ((i>0) and (SchedulerShifts[i]['TimeZone']['StartTime']>SchedulerShifts[i-1]['TimeZone']['EndTime'])):
                                st=SchedulerShifts[i]['TimeZone']['StartTime']
                                et=SchedulerShifts[i]['TimeZone']['EndTime']
                                d={}
                                d['Num_RunID']=SchID
                                d['StartTime']=st.time()
                                d['EndTime']=et.time()
                                if unit==suWeek:
                                        st=st+datetime.timedelta(days=weekStartDay)
                                        et=et+datetime.timedelta(days=weekStartDay)
                                
                                d['sdays']=(st-datetime.datetime(1899,12,30,0,0)).days
                                d['edays']=(et-datetime.datetime(1899,12,30,0,0)).days
                                d['schClassID']=SchedulerShifts[i]['schClassID']
                                d['overtime']=SchedulerShifts[i]['OverTime']
                                sql=getSQL_insert_ex(NUM_RUN_DEIL._meta.db_table,d)
                                customSql(sql)
                return getJSResponse("result=0")
        except:
                return getJSResponse("result=1; message='Operation Failed';")                
                #errorLog()
@login_required
def deleteAllShiftTime(request):
        SchIDs=request.GET.get('shift_id','-1').split(',')
        for SchID in SchIDs:
                deleteShiftDetail(SchID)    
        return getJSResponse("result=0")
@login_required
def deleteEmployeeShift(request):
        pass

def deleteShiftDetail(SchID):
        from mysite.iclock.sql import deleteShiftDetail_sql
        sql=deleteShiftDetail_sql(SchID)
        customSql(sql)

@login_required
def deleteShiftTime(request):
        from mysite.iclock.sql import deleteShiftTime_sql
        start=float(request.POST.get('start'))
        end=float(request.POST.get('end'))
        shift_id=int(request.POST.get('shift_id'))
        unit=int(request.POST.get('unit'))
        weekStart=int(request.POST.get('weekStartDay'))
        sday=int(start)
        send=int(end)
        h=int((start-sday)*24)
        m=int(((start-sday)*24-h)*60)
        st=datetime.time(h,m,0)

        h=int((end-send)*24)
        m=int(((end-send)*24-h)*60)
        if m==59:
                h=h+1
                m=0
        et=datetime.time(h,m,59)
        sd=sday
        ed=send
        if unit==1:
                sd=sday+weekStart
                ed=send+weekStart
                if ed<0:
                        sd=sd+7
                        ed=ed+7
        if shift_id==1:
            return getJSResponse("result=0")
        sql=deleteShiftTime_sql(sd,ed,st,et,shift_id)
        customSql(sql)
        return getJSResponse("result=0")

def getSchedulerShifts(schid,unit,WorkWeekStartDay=0,overtime=0):
        global SchedulerShifts
        global FTTimeZones
        SchedulerShifts=[]
        FTTimeZones=[]
        SchDetail=NUM_RUN_DEIL.objects.filter(Num_runID=schid).order_by('Num_runID', 'Sdays', 'StartTime')
        for sDetail in SchDetail:
                ot=sDetail.OverTime
                st=checkTime(datetime.time(sDetail.StartTime.hour,sDetail.StartTime.minute,sDetail.StartTime.second))
                et=checkTime(datetime.time(sDetail.EndTime.hour,sDetail.EndTime.minute,sDetail.EndTime.second))
                StartDay=sDetail.Sdays
                EndDay=sDetail.Edays
                if unit==suWeek:
                        StartDay=StartDay-WorkWeekStartDay
                        EndDay=EndDay-WorkWeekStartDay
                        if EndDay<0:
                                StartDay=StartDay+7
                                EndDay=EndDay+7

                if (AddTimeZone(st+datetime.timedelta(days=StartDay), et+datetime.timedelta(days=EndDay))>=0):
                        AddScheduleShift(SchedulerShifts, st+datetime.timedelta(days=StartDay)  , et+datetime.timedelta(days=EndDay),sDetail.SchclassID_id,ot)
        return SchedulerShifts

def MergeTimeZone(TimeZones,sTime,eTime,TZProperty=TZNormal):
        Result=-1
        t=eTime-sTime
        if (t.days*24*60*60+t.seconds)<LastZone:
                return Result
        tzl=len(TimeZones)
        tz={'StartTime':sTime,'EndTime':eTime,'TZProperty':TZProperty}
        if TZProperty==TZNormal:
                i=tzl-1
                while i>=0:
                        if sTime>TimeZones[i]['StartTime']-datetime.timedelta(seconds=LastZone):
                                break
                        i=i-1
                if (i>=0) and (eTime<TimeZones[i]['EndTime']):
                        return Result
                if (tzl==0) or ((i<0) and (eTime<TimeZones[0]['StartTime'])) or ((i>=0) and (sTime>TimeZones[i]['EndTime']) and
                                                                                 ((i==tzl-1) or (eTime<TimeZones[i+1]['StartTime']))):
                        Result=i+1
                        TimeZones.insert(i+1,tz)
        return Result


def TestTimeZone(TimeZones,sTime,eTime):
        i=len(TimeZones)
        MergeTimeZone(TimeZones,sTime,eTime)
        if i<len(TimeZones):
                return True
        else:
                return False

def AddTimeZone(STime, ETime,TZProperty=TZNormal):
        global FTTimeZones
        Result=MergeTimeZone(FTTimeZones, STime, ETime,TZProperty)
        return Result

@login_required
def FetchSchPlan(request):
        from mysite.att.models.num_run import NUM_RUN
        try:
                UserIDs=[]
                deptIDs=[]
                schPlan={}
                schPlan['MayUsedAutoIds']=[]
                schPlan['SchArray']=[]
                schPlan['MinAutoPlanInterval']=24
                schPlan['AutoSchPlan']=1
                AutoSchPlan=False
                deptIDs=request.POST.getlist('deptIDs')
                UserIDs=request.POST.getlist('UserID')

                #print "Userids===",UserIDs
                if len(UserIDs)==0 :
                        #deptIDs=deptIDs.split(',')
                        UserIDs = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                        #UserIDs=",".join(["%s" % int(i) for i in userlist])
#                else:
#                        UserIDs=UserIDs.split(',')
                AutoSchPlan=(request.POST.get('auto_assign','')=='on')
                
                if AutoSchPlan:
                        try:
                                leastdays=int(request.POST.get('least_days','1'))
                        except:
                                leastdays=1
                        try:
                                leasthours=int(request.POST.get('least_hours','0'))
                        except:
                                leasthours=8
                        schPlan['MinAutoPlanInterval']=leastdays*24+leasthours
                                
                if AutoSchPlan==False:
                        schPlan['AutoSchPlan']=0
                s=request.POST['sAssigned_shifts']
                
                schList=loads(s)
                schclasses=request.POST.getlist('sTimeTbl')
#                if len(schclasses)>0:
#                        schclasses=schclasses.split(',')
                for t in schclasses:
                        schPlan['MayUsedAutoIds'].append(int(t))
                
                for t in schList:
                        try:
                                st=datetime.datetime.strptime(t['StartDate'],"%Y-%m-%d")
                                et=datetime.datetime.strptime(t['EndDate'],"%Y-%m-%d")
                        except:
                                st=datetime.datetime.strptime(t['StartDate'],'%Y-%m-%d %H:%M:%S')
                                et=datetime.datetime.strptime(t['EndDate'],'%Y-%m-%d %H:%M:%S')
                        if not allowAction(st,5,et):
                                return getJSResponse("result=2")
                        schPlan['SchArray'].append({'NUM_OF_RUN_ID':NUM_RUN.objects.get(pk=t['SchId']),'StartDate':t['StartDate'],'EndDate':t['EndDate']})
                #print "UserIDs:%s"%UserIDs
                for i in UserIDs:
                        SaveSchPlan(int(i),schPlan,st,et)
                
                return getJSResponse("result=0")
        except:
                import traceback; traceback.print_exc()
                pass
                #errorLog(request)

def SaveSchPlan(userid,dSchPlan,st,et):
        #from mysite.att.models import *
        from mysite.att.models.user_of_run import USER_OF_RUN
        from mysite.att.models.userusedsclasses import UserUsedSClasses
        from mysite.personnel.models.model_emp import Employee
        from mysite.iclock.sql import SaveSchPlan_sql1,SaveSchPlan_sql2
        sql=getSQL_update("userinfo",whereUserid=userid,AutoSchPlan=dSchPlan['AutoSchPlan'],MinAutoSchInterval=dSchPlan['MinAutoPlanInterval'])
        customSql(sql)
        cache.delete("%s_iclock_emp_%s"%(settings.UNIT,userid))
        sql=SaveSchPlan_sql1(userid)
        customSql(sql)
        for t in dSchPlan['MayUsedAutoIds']:
                sql=getSQL_insert(UserUsedSClasses._meta.db_table,UserID=userid,SchID=t)
                customSql(sql)
        sql=SaveSchPlan_sql2(userid,st,et)
        customSql(sql)
        i = 0
        #print "userid:%s"%userid
        for t in dSchPlan['SchArray']:
            
            ur=USER_OF_RUN()
            ur.UserID=Employee.objects.get(pk=userid)
            ur.ORDER_RUN=i
            for k,v in t.items():                
                ur.__setattr__(k,v)
            ur.save()
            i=i+1
#                t['userid']=userid
#                t['ORDER_RUN']=i
#                sql=getSQL_insert_ex(USER_OF_RUN._meta.db_table,t)
#                print sql
#                customSql(sql)
            
        deleteCalcLog(UserID=userid)
def addTemparyShifts(request):
        global SchedulerShifts
        global FTTimeZones
        try:
                
                st=request.POST['StartDate']
                et=request.POST['EndDate']
                st=st.replace("/","-")
                et=et.replace("/","-")
                chklbSchClass=request.POST.getlist("sTimeTbl")
                chklbDates=request.POST.getlist("sDates")
                

                OverTime=request.POST.get('OverTime','')
                
                deptIDs=request.POST.get('deptIDs',"")
                UserIDs=request.POST.getlist('UserID')
                
                is_OT=request.POST.get('is_OT','')
                is_OT=(is_OT=='on')

                if is_OT:
                        if OverTime=='':
                                OverTime=0
                        else:
                                OverTime=int(OverTime)
                st=datetime.datetime.strptime(st,'%Y-%m-%d')
                et=datetime.datetime.strptime(et,'%Y-%m-%d')
                schClasses=GetSchClasses()
                if UserIDs =="":
                        deptIDs=deptIDs.split(',')
                        UserIDs = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                        #UserIDs=",".join(["%s" % int(i) for i in userlist])
#                else:
#                        UserIDs=UserIDs.split(',')


                for i in UserIDs:
                        SchedulerShifts=[]
                        FTTimeZones=[]
                        if chklbDates<>[] and chklbSchClass<>[]:
                                UserSchPlan=LoadSchPlan(i,True,False)
                                SchedulerShifts=GetUserScheduler(i, st, et,UserSchPlan['HasHoliday'])
                        for t in SchedulerShifts:
                                AddTimeZone(t['TimeZone']['StartTime'],t['TimeZone']['EndTime'])
                        #print "chklbSchClass",chklbSchClass
                        for t in chklbSchClass:
                                t=int(t)
                                j=FindSchClassByID(t)
                                stime=schClasses[j]['TimeZone']['StartTime']
                                etime=schClasses[j]['TimeZone']['EndTime']
                                #print 'chklbDates',chklbDates
                                for tt in chklbDates:
                                        tt=tt.replace("/","-")
                                        tt=datetime.datetime.strptime(tt,'%Y-%m-%d')
                                        starttime = datetime.datetime(tt.year,tt.month,tt.day,stime.hour,stime.minute)
                                        endtime = datetime.datetime(tt.year,tt.month,tt.day,etime.hour,etime.minute)
                                        if endtime<starttime:
                                                endtime=endtime+datetime.timedelta(days=1)
                                        #print "starttime: %s     endtime: %s"%(starttime,endtime)
                                        if TestTimeZone(FTTimeZones,starttime,endtime):
                                                AddScheduleShift(SchedulerShifts, starttime, endtime,t,OverTime)
                                        else:
                                                #print "tt:%s"%tt
                                                return getJSResponse("result=1")
                                        #print "t:%s"%t
                                        SaveTempSch(i,st,et,SchedulerShifts)
                        
                return getJSResponse("result=0")
        except:
                import traceback; traceback.print_exc()
                return getJSResponse("ERROR=0")

def SaveTempSch(userid,st,et,SchedulerShifts):
        from mysite.att.models.user_temp_sch import USER_TEMP_SCH
        from mysite.personnel.models.model_emp import Employee
        from mysite.iclock.sql import SaveTempSch_sql
        sql=SaveTempSch_sql(userid,st,et)
        customSql(sql)
        #print 'SchedulerShifts',SchedulerShifts
        for t in SchedulerShifts:
                if (t['TimeZone']['EndTime']<st) or (t['TimeZone']['StartTime']>=(et+datetime.timedelta(days=1))):
                        continue
                else:
                    x=USER_TEMP_SCH()
                    x.UserID=Employee.objects.get(pk=userid)
                    x.ComeTime=t['TimeZone']['StartTime'].strftime("%Y-%m-%d %H:%M:%S")
                    x.LeaveTime=t['TimeZone']['EndTime'].strftime("%Y-%m-%d %H:%M:%S")
                    x.SchclassID=t['schClassID']
                    x.OverTime=t['OverTime']
                    x.save()
#                        sql=getSQL_insert(USER_TEMP_SCH._meta.db_table,userid=userid,comeTime=t['TimeZone']['StartTime'].strftime("%Y-%m-%d %H:%M:%S"),leavetime=t['TimeZone']['EndTime'].strftime("%Y-%m-%d %H:%M:%S"),
#                                      schclassid=t['schClassID'],overtime=t['OverTime'])
#                        
#                        customSql(sql)
        
        j=st
        
        while j<=et:
                m=0
                for t in SchedulerShifts:
                        m=0
                        if (j<=t['TimeZone']['StartTime']) and (j+datetime.timedelta(days=1)>t['TimeZone']['StartTime']):
                                m=1
                                break        
                if m==0:
                    x=USER_TEMP_SCH()
                    x.UserID=Employee.objects.get(pk=userid)
                    x.ComeTime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
                    x.LeaveTime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
                   # x.SchclassID=t['schClassID']
                    x.OverTime=0
                    x.save()
                    #
                    
#                        sql=getSQL_insert(USER_TEMP_SCH._meta.db_table,userid=userid,comeTime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),leavetime=(j+datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),overtime=0)
#                        customSql(sql)
                        
                j=j+datetime.timedelta(days=1)
        deleteCalcLog(UserID=userid)
        
@login_required
def doDeleteTmpShifts(request):     #清除指定日期、人员的临时排班 result=0成功;result=1失败
        if request.method=="POST":
                UserIDs=request.POST.get("UserIDs"," ")
                d1=request.POST.get("StartDate"," ")
                d2=request.POST.get("EndDate"," ")
                deptIDs=request.POST.get('deptIDs',"")

                d1=datetime.datetime.strptime(d1,'%Y-%m-%d')
                d2=datetime.datetime.strptime(d2,'%Y-%m-%d')
                
                if not allowAction(d1,5,d2):
                        return getJSResponse("result=2")
                if UserIDs =="":
                        deptIDs=deptIDs.split(',')
                        UserIDs = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                #UserIDs=",".join(["%s" % int(i) for i in userlist])
                else:
                        UserIDs=UserIDs.split(',')
                uids=[]
                for u in UserIDs:
                        uids.append(u)
                        deleteCalcLog(UserID=int(u))
#                uids=id.split(',')
#                USER_TEMP_SCH.objects.filter(UserID__in=uids,ComeTime__gt=d1,LeaveTime__lt=d2+datetime.timedelta(1)).delete()
                USER_TEMP_SCH.objects.filter(UserID__in=uids,ComeTime__gt=d1,LeaveTime__lt=d2+datetime.timedelta(2),ComeTime__lt=d2+datetime.timedelta(1)).delete()
                
                
                return getJSResponse("result=0")
        

@login_required
def ConvertTemparyShifts(request):
        if request.POST:
                global SchedulerShifts
                global FTTimeZones
                st=request.POST['StartDate']
                et=request.POST['EndDate']
                UserIDs=request.POST['UserIDs']
                deptIDs=request.POST.get('deptIDs',"")
                st=datetime.datetime.strptime(st,'%Y-%m-%d')
                et=datetime.datetime.strptime(et,'%Y-%m-%d')
                if not allowAction(st,5,et):
                        return getJSResponse("result=2")
                if UserIDs =="":
                        deptIDs=deptIDs.split(',')
                        UserIDs = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                        #UserIDs=",".join(["%s" % int(i) for i in userlist])
                else:
                        UserIDs=UserIDs.split(',')
                
                for i in UserIDs:
                        SchedulerShifts=[]
                        FTTimeZones=[]
                        UserSchPlan=LoadSchPlan(i,True,False)
                        SchedulerShifts=GetUserScheduler(i, st, et,UserSchPlan['HasHoliday'])
                        SaveTempSch(i,st,et,SchedulerShifts)
                return getJSResponse("result=0")
@login_required
def deleteEmployeeShift(request):
#        print request.POST
        st=request.POST['StartDate']
        et=request.POST['EndDate']
        UserIDs=request.POST['UserIDs'].split(',')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        
        chklbSchClass=request.POST['sTimeTbl'].split(',')
        if not allowAction(st,5,et):
                return getJSResponse("result=2")
        for i in UserIDs:
                SchedulerShifts=[]
                UserSchPlan=LoadSchPlan(i,True,False)
                SchedulerShifts=GetUserScheduler(i, st, et,UserSchPlan['HasHoliday'])
                for t in SchedulerShifts:
                        if (t['SchID']==int(chklbSchClass[0])) and (t['TimeZone']['StartTime'].date()>=st.date()):
                                if (t['TimeZone']['StartTime'].date()==st.date() and t['TimeZone']['EndTime'].date()==et.date()) or ((t['TimeZone']['StartTime'].date()<t['TimeZone']['EndTime'].date()) and t['TimeZone']['StartTime'].date()<=et.date()):
                                        SchedulerShifts.remove(t)
                                        break
                SaveTempSch(i,st,et,SchedulerShifts)
        return getJSResponse("result=0")
