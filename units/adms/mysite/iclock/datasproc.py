#coding=utf-8
from django.utils.translation import ugettext as _
from mysite.iclock.models import *
from mysite.personnel.models import Employee, EmpForeignKey,Department
from mysite.iclock.models.modelproc import *
from django.db.models.fields import AutoField, FieldDoesNotExist
from django.contrib.auth.models import User, Permission, Group
import datetime


def transLeaName(leaveID):
        LeaName={ #999: _('BL'),
                  1000:_(u'应到/实到'),  
                  1001:_(u'迟到'),
                  1002:_(u'早退'),
                  1003:_(u'请假'),
                  1004:_(u'旷工'),
                  1005:_(u'加班'), 
                  1007:_(u'休息日'),
                  1008:_(u'未签到'),
                  1009:_(u'未签退'),
                  1010:_(u'出'),    
                  1011:_(u'出'),  
                  1012:_(u'外出'),
                  1013:_(u'自由加班'),
                  
                  }
        return LeaName[leaveID]

def transLeaveName(lName):
        if lName=='Sick leave':
                return _(u'请假')
        elif lName=='Private affair leave':
                return _(u'私事离开')
        elif lName=='Home leave':
                return _(u'人员离职')
        elif lName=='Business leave':
                return _(u'公事离开')
        else:
                return lName

def transExceptionName():
        return (_(u'出'),_(u'出'),_(u'出'),_(u'BL'))

def GetUnitText(AttUnit):
        UnitName={0:_(u'日'),1:_(u'小时'),2:_(u'分钟'),3:_(u'日'),4:_(u'考勤时间')}
        if AttUnit>=0 and AttUnit<=4:
                return UnitName[AttUnit]
        else:
                return ''
        
        
def ConstructBaseFields():
        r={}
        strFieldNames=['deptid','badgenumber','username','ssn']
        FieldNames=['userid','badgenumber','username','deptid','duty','realduty','late','early','absent',
                    #'out',
                    'dutyinout','clockin',
            'clockout','noin','noout','worktime','workmins',
            #'SSpeDayNormal',
            #'SSpeDayWeekend','SSpeDayHoliday',
            'overtime',
            'SSpeDayNormalOT',
            'SSpeDayWeekendOT','SSpeDayHolidayOT',
            'Leave']
        for t in FieldNames:
                if t in strFieldNames:
                        r[t]=''
                else:
                        r[t]=''
        r['userid']=-1;
        FieldCaption=[_(u'用户ID'),_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'应到'),_(u'实到'),_(u'迟到'),_(u'早退'),_(u'旷工'),
                      #_(u'外出'),
                      _(u'应签次数'),_(u'应签到'),
                    _(u'应签退'),_(u'未签到'),_(u'未签退'),_(u'出勤时长'),_(u'工作时间'),
                    #_(u'平日'),
                   # _(u'休息日'),_(u'节假日'),
                    _(u'加班时间'),
                    _(u'平日加班'),
                    _(u'休息日加班'),_(u'节假日加班'),
                    _(u'请假')]
        return [r,FieldNames,FieldCaption]
        
def ConstructBaseFields1(d1,d2):
        r={}
        strFieldNames=['deptid','badgenumber','username']
        FieldNames=['userid','badgenumber','username','deptid']
        FieldCaption=[_(u'用户ID'),_(u'人员编号'),_(u'姓名'),_(u'部门名称'),]
        r1=['duty','realduty','late','early','absent','overtime',
        #'SSpeDayHoliday',
        'SSpeDayNormalOT',
            'SSpeDayWeekendOT','SSpeDayHolidayOT',
            'Leave']
        for t in FieldNames:
            if t in strFieldNames:
                r[t]=''
        for t in r1:
            r[t]=''
        t=d1
        while t<=d2:
            f=str(t.day)
            r[f]=''
            FieldNames.append(f)
            FieldCaption.append(f)
            t=t+datetime.timedelta(1)
        FieldNames=FieldNames+r1
        FieldCaption=FieldCaption+[_(u'应到'),_(u'实到'),_(u'迟到'),_(u'早退'),_(u'旷工'),_(u'加班时间'),
                                #_(u'节假日'),
                                _(u'平日加班'),
                                   _(u'休息日加班'),_(u'节假日加班'),
                                   _(u'请假')]
        r['userid']=-1
        return [r,FieldNames,FieldCaption]


def ConstructBaseFields2(d1,d2):
        r={}
        strFieldNames=['deptid','badgenumber','username']
        FieldNames=['userid','badgenumber','username','deptid']
        FieldCaption=[_(u'用户ID'),_(u'人员编号'),_(u'姓名'),_(u'部门名称'),]
#        r1=['duty','realduty','late','early','absent','overtime','Leave']
        for t in FieldNames:
                if t in strFieldNames:
                        r[t]=''
#        for t in r1:
#                r[t]=''
        t=d1
        while t<=d2:
                f=str(t.day)
                r[f]=''
                FieldNames.append(f)
                FieldCaption.append(f)
                t=t+datetime.timedelta(1)
#        FieldNames=FieldNames+r1
#        FieldCaption=FieldCaption+[_('duty'),_('realduty'),_('late'),_('early'),_('absent'),_('overtime'),_('Leave')]
        r['userid']=-1
        return [r,FieldNames,FieldCaption]

def FetchBaseDisabledFields(user,tblName,itemType='report_fields_define'):
        try:
                item=ItemDefine.objects.filter(Author=user,ItemName=tblName,ItemType=itemType)
                if item:
                        if item[0].ItemValue:
                                return item[0].ItemValue.split(',')
        except:
                pass
        return []

def FetchDisabledFields(user,tblName,itemType='report_fields_define'):
        re= FetchBaseDisabledFields(user,tblName,itemType)
        if re:
                return re
        
        admins=User.objects.filter(is_superuser=True)
        for tadmin in admins:
                re= FetchBaseDisabledFields(tadmin,tblName,itemType)
                if re:
                        return re
        
        return []
def FetchModelFields(tbl):
        if tbl=="attShifts":
                attshiftsbasefields= ['DeptID','PIN','EName','AttDate','SchId','ClockInTime','ClockOutTime','StartTime','EndTime','WorkDay','RealWorkDay','Late','Early','Absent','OverTime','WorkTime','MustIn','MustOut','SSpeDayNormal','SSpeDayWeekend','SSpeDayHoliday','AttTime','SSpeDayNormalOT','SSpeDayWeekendOT','SSpeDayHolidayOT']
                return attshiftsbasefields
        else:
                return  [f.column for f in tbl._meta.fields if not isinstance(f, AutoField)]
def FetchModelFieldsCaption(tbl):
        if tbl=="attShifts":
                return [_(u'部门名称'),_(u'部门编号'),_(u'人员姓名'),_(u'日期'),_(u'时段名称'),_(u'签到时间'),_(u'签退时间'),_(u'起始时间'),_(u'结束时间'),_(u'工作日'),_(u'实到'),_(u'迟到'),_(u'早退'),_(u'旷工'),_(u'加班签到'),_(u'考勤时间'),_(u'应签到'),_(u'应签退'),_(u'平日'),_(u'休息日'),_(u'节假日'),_(u'时间'),_(u'平日加班'),_(u'休息日加班'),_(u'节假日加班')]
        else:
                return [f.verbose_name.capitalize() for f in tbl._meta.fields if not isinstance(f, AutoField)]
        return r
def GetdisableFieldsIndex(user,tbl):
        if tbl=="attShifts":
                rFieldNames=FetchModelFields('attShifts')
                dis=FetchDisabledFields(user,'attShifts')
                result=[]
                if dis:
                        for t in dis:
                                try:
                                        result.append(rFieldNames.index(t))
                                except:
                                        return []
                return result
        
def GetAnnualleave(userid):   #自动计算年假天数 参数:入职日期
        if not userid: return ''
        t=employee.objByID(int(userid))
        if not t:
                return 0
#        for t in emp:
        Hiredday=t.Hiredday
        Annualleave=t.Annualleave
        if str(type(Hiredday))!="<type 'datetime.date'>" and str(type(Hiredday))!="<type 'datetime.datetime'>":
                return 0
        nowyear=datetime.datetime.now().year
        hireyear=checkTime(Hiredday).year
        if hireyear<1960:
                return 0
        diff=nowyear-hireyear
        re=0
        if diff>=1 and diff<10:
                re=5
        elif diff>=10 and diff<20:
                re=10
        elif diff>=20:
                re=15
        if Annualleave!=None:
                if Annualleave<re:
                        re=Annualleave
        return re
def GetLeaveDays(userid,type):
        LClass=GetLeaveClasses(1)
        LeaveID=0
        for t in LCLASS:
                if t['LeaveType']==int(type):
                        LeaveID=t['LeaveID']
                        break
        if LeaveID==0:
                return 0
        AttExcep=AttException.objects.filter(UserID=userid,ExceptionID=LeaveID)
        return len(AttExcep)

def allowAction(startdate,type,enddate=None):
        st=checkTime(startdate)
        if enddate!=None:
                et=checkTime(enddate)
        #account=accounts.objects.filter(StartTime__gte=st-datetime.timedelta(days=180))
        account=""
        if not account:
                return True
        type=int(type)
        for t in account:
                if (st>=checkTime(t.StartTime) and st<=checkTime(t.EndTime)) or (enddate!=None and (et>=checkTime(t.StartTime) and et<=checkTime(t.EndTime))):
                        if t.Status==1 and (t.Type==99 or t.Type==type):
                                return False
        return True
#为综合排班列表构造表头                        
def ConstructScheduleFields():
        FieldNames=['userid','deptid','badgenumber','username','starttime','endtime','schname']
        FieldCaption=[_(u'用户ID'),_(u'部门名称'),_(u'考勤号码'),_(u'名称'),_(u'开始时间'),_(u'结束时间'),_(u'班次名称')]
        return [FieldNames,FieldCaption]
#为假类汇总构造表头        
def ConstructLeaveFields():
        r={}
        FieldNames=['userid','badgenumber','username','deptid','Leave']
        for t in FieldNames:
                        r[t]=''
        r['userid']=-1;
        FieldCaption=[_(u'用户ID'),_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'请假')]
        return [r,FieldNames,FieldCaption]

#从原datas移过来的
def trunc(DTime):
        return datetime.datetime(DTime.year,DTime.month,DTime.day,0,0,0)

def diffTime(diffT):
        return diffT.days*86400+diffT.seconds

def deleteCalcLog(**kwargs):
        deptid=0
        userid=0
        Type=-1
        for k,v in kwargs.items():
                if k=='DeptID':deptid=v
                elif k=='UserID':userid=v
                elif k=='Type':Type=v
        Type=-1    #此句的作用是把该人要重新统计
        sql="""delete from attcalclog where """
        if Type==-1:
                sql=sql+"Type>%s"%(Type)
        else:
                sql=sql+"Type=%s"%(Type)
        if deptid>0:
                sql=sql+" and deptid=%s"%(deptid)
        if userid>0:
                sql=sql+" and userid=%s"%(userid)
#        print sql
        customSql(sql)
        
def FieldIsExist(fieldName,DataModel):
        field_names = [f.column for f in DataModel._meta.fields if not isinstance(f, AutoField)]
        if fieldName in field_names:
                return True
        return False

def hourAndMinute(value):
        if value:
                h=str(int(value)/60)
                m=str(int(value)%60)
                if int(m)<10:
                        m='0'+str(m)
                return h+':'+m
        return ""

Absent={
        "0":_(u"否"),
        "1":_(u"是"),
        }
def IsYesNo(value):
        if value:
                return Absent['1']
        return Absent['0']

def IsTrueOrFalse(value):
        if value:
                return Absent['0']
        return Absent['1']

def getValidValue(value):
        if not value:return ""
        if type(value)==type(1):
                return int(value)
        value=float(value)
        return value

def checkTime(t):
        if str(type(t))=="<type 'datetime.datetime'>":
                return datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second)
        elif str(type(t))=="<type 'datetime.time'>":
                return datetime.datetime(1899,12,30,t.hour,t.minute,t.second)
        elif str(type(t))=="<type 'datetime.date'>":
                return datetime.datetime(t.year,t.month,t.day,0,0,0)
