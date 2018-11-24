#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from dbapp.modelutils import batchSql
from mysite.personnel.models import Employee, EmpForeignKey


def get_device(n):
    n=n and string.strip(n) or ""
    if not n: return None
    dev=cache.get("iclock_"+n)
    if dev:
#        print 'from cache', dev
        return dev
    try:
        dev=Device.objects.get(SN=n)
    except ObjectDoesNotExist:
        dev=Device.objects.get(Alias=n)
    cache.set("iclock_"+n, dev)
    return dev


def setValueDic(data):
    d={}
    for line in data.split("\n"):
        if line:
            v=line.split("\r")[0]
        else:
            v=line
        nv=v.split("=", 1)
        if len(nv)>1:
            try:
                v=str(nv[1])
                d[nv[0]]=v
            except:
#print nv
                pass
    return d

def setValueFor(data, key, value):
    d={}
    for line in data.split("\n"):
        if line:
            v=line.split("\r")[0]
        else:
            v=line
        nv=v.split("=", 1)
        if len(nv)>1:
            try:
                v=str(nv[1])
                d[nv[0]]=v
            except:
#print nv
                pass
    if key:
        d[key]=value
    return "\n".join(["%s=%s"%(k, d[k]) for k in d.keys()])

def mergeValues(data1, data2):
    return setValueFor(data1+"\n"+data2, "","")

last_reboot_cname="%s_lastReboot"%settings.UNIT    

def updateLastReboot(iclocks):
    lastReboot=cache.get(last_reboot_cname)
    d=datetime.datetime.now()
    rebInterval=(REBOOT_CHECKTIME>0 and REBOOT_CHECKTIME or 10)
    ips=[]
#    print "lastReboot:",lastReboot
    if not lastReboot: lastReboot={}
    for i in iclocks:
        ip=i.IPAddress()
        if ip:
            if ip in lastReboot:
                if d-lastReboot[ip]>datetime.timedelta(0,rebInterval*60):
                    ips.append(ip)
                    lastReboot[ip]=d
#                    print "reboot:", ip, lastReboot[ip]
            else:
                ips.append(ip)
                lastReboot[ip]=d
    if ips: cache.set(last_reboot_cname, lastReboot, rebInterval*60)
#    print "lastReboot:",lastReboot
    return ips

def removeLastReboot(ip):
    lastReboot=cache.get(last_reboot_cname)
    if not lastReboot: return
    if ip in lastReboot:
        lastReboot.pop(ip)
        cache.set(last_reboot_cname, lastReboot)
def checkTime(t):
    if str(type(t))=="<type 'datetime.datetime'>":
        return datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.time'>":
        return datetime.datetime(1899,12,30,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.date'>":
        return datetime.datetime(t.year,t.month,t.day,0,0,0)




def ValidIClocks(qs):
    return qs.filter(Q(DelTag__isnull=True)|Q(DelTag=0)).order_by("Alias")



def getNormalCard(card):
    if not card: return ""    
    try:
        num=int(str(card))
        card="[%02X%02X%02X%02X%02X]"%(num & 0xff, (num >> 8) & 0xff, (num >> 16) & 0xff, (num >> 24) & 0xff, (num >> 32) & 0xff)
    except:
        pass
    return card

def getEmpCmdStr(emp):    
    ename=emp.EName and emp.EName.strip() or ""
    ret= "DATA USER PIN=%s\t%s\t%s\t%s\t%s\t%s\tGrp=%s"%(emp.pin(), 
            ename and ("Name=%s"%ename) or "", 
            "Pri=%s"%(emp.Privilege and emp.Privilege or 0), 
            emp.Password and ("Passwd=%s"%emp.Password) or "", 
            emp.Card and ("Card=%s"%getNormalCard(emp.Card)) or "", 
            emp.TimeZones and ("TZ=%s"%emp.TimeZones) or "", 
            emp.AccGroup or 1)
                                        
    return ret                            


def isUpdatingFW(device):
    return devcmds.objects.filter(SN=device, CmdReturn__isnull=True, CmdContent__startswith='PutFile ', CmdContent__endswith='main.gz.tmp',).count()

def clearData():
    for obj in Employee.objects.all(): obj.delete()
    for obj in devcmds.objects.all():
        obj.CmdOverTime=None
        obj.CmdTransTime=None
        obj.save()
    for obj in Device.objects.all():
        obj.LogStamp=1
        obj.OpLogStamp=1
        obj.save()



def customSql(sql,action=True):
#    from django.db import connection
    cursor = connection.cursor()
    
    cursor.execute(sql)
    if action:
        connection._commit()
    return cursor

def customSqlEx(sql,params=[],action=True):
	try:
		cursor = connection.cursor()
		if settings.DATABASE_ENGINE == 'ibm_db_django':
			if not params:params=()
		if params:
			cursor.execute(sql,params)
		else:
			cursor.execute(sql)
		
		if action:
			connection._commit()
		return cursor
	except:
		return None



def createDefautValue():
    sqls=(
"ALTER TABLE departments ADD CONSTRAINT sdf DEFAULT 1 FOR supdeptid",
"ALTER TABLE userinfo ADD CONSTRAINT ddf DEFAULT 1 FOR defaultdeptid",
"ALTER TABLE userinfo ADD CONSTRAINT tdf DEFAULT 1 FOR ATT",
"ALTER TABLE userinfo ADD CONSTRAINT indf DEFAULT 1 FOR INLATE",
"ALTER TABLE userinfo ADD CONSTRAINT oedf DEFAULT 1 FOR OutEarly",
"ALTER TABLE userinfo ADD CONSTRAINT otdf DEFAULT 1 FOR OverTime",
"ALTER TABLE userinfo ADD CONSTRAINT hdf DEFAULT 1 FOR Holiday",
"ALTER TABLE userinfo ADD CONSTRAINT ldf DEFAULT 1 FOR Lunchduration",
"ALTER TABLE userinfo ADD CONSTRAINT sepdf DEFAULT 1 FOR SEP",
"ALTER TABLE userinfo ADD CONSTRAINT offdutydf DEFAULT 0 FOR OffDuty",
"ALTER TABLE userinfo ADD CONSTRAINT DelTagdf DEFAULT 0 FOR DelTag",
"ALTER TABLE userinfo ADD CONSTRAINT enamedf DEFAULT ' ' FOR name",
"ALTER TABLE template ADD CONSTRAINT fiddf DEFAULT 0 FOR FingerID",
"ALTER TABLE template ADD CONSTRAINT vdf DEFAULT 1 FOR Valid",
"ALTER TABLE template ADD CONSTRAINT dtdf DEFAULT 0 FOR DelTag",
"ALTER TABLE checkinout ADD CONSTRAINT stdf DEFAULT 'I' FOR checktype",
"ALTER TABLE checkinout ADD CONSTRAINT vcedf DEFAULT 0 FOR verifycode",
"ALTER TABLE checkexact ADD CONSTRAINT uidf DEFAULT 0 FOR UserID",
"ALTER TABLE checkexact ADD CONSTRAINT ctdf DEFAULT 0 FOR CHECKTIME",
"ALTER TABLE checkexact ADD CONSTRAINT ctydf DEFAULT 0 FOR CHECKTYPE",
"ALTER TABLE checkexact ADD CONSTRAINT isdf DEFAULT 0 FOR ISMODIFY",
"ALTER TABLE checkexact ADD CONSTRAINT idldf DEFAULT 0 FOR ISDELETE",
"ALTER TABLE checkexact ADD CONSTRAINT icdf DEFAULT 0 FOR INCOUNT",
"ALTER TABLE checkexact ADD CONSTRAINT icodf DEFAULT 0 FOR ISCOUNT",
"ALTER TABLE holidays ADD CONSTRAINT hddf DEFAULT 1 FOR HolidayDay",
"ALTER TABLE NUM_RUN_DEIL ADD CONSTRAINT siddf DEFAULT -1 FOR SchclassID",
"ALTER TABLE NUM_RUN ADD CONSTRAINT oldiddf DEFAULT -1 FOR OLDID",
"ALTER TABLE NUM_RUN ADD CONSTRAINT sddf DEFAULT '2000-1-1' FOR StartDate",
"ALTER TABLE NUM_RUN ADD CONSTRAINT eddf DEFAULT '2099-12-31' FOR EndDate",
"ALTER TABLE NUM_RUN ADD CONSTRAINT cedf DEFAULT 1 FOR Cyle",
"ALTER TABLE NUM_RUN ADD CONSTRAINT usdf DEFAULT 1 FOR Units",
"ALTER TABLE USER_OF_RUN ADD CONSTRAINT sdedf DEFAULT '1900-1-1' FOR StartDate",
"ALTER TABLE USER_OF_RUN ADD CONSTRAINT ede1df DEFAULT '2099-12-31' FOR EndDate",
"ALTER TABLE USER_OF_RUN ADD CONSTRAINT irndf DEFAULT 0 FOR ISNOTOF_RUN",
"ALTER TABLE USER_SPEDAY ADD CONSTRAINT ssdf DEFAULT '1900-1-1' FOR StartSpecDay",
"ALTER TABLE USER_SPEDAY ADD CONSTRAINT diddf DEFAULT -1 FOR DateID",
"ALTER TABLE USER_SPEDAY ADD CONSTRAINT esddf DEFAULT '2099-12-31' FOR EndSpecDay",
"ALTER TABLE USER_TEMP_SCH ADD CONSTRAINT otedf DEFAULT 0 FOR OverTime",
"ALTER TABLE USER_TEMP_SCH ADD CONSTRAINT tedf DEFAULT 0 FOR Type",
"ALTER TABLE USER_TEMP_SCH ADD CONSTRAINT fgdf DEFAULT 1 FOR Flag",
"ALTER TABLE USER_TEMP_SCH ADD CONSTRAINT ssiddf DEFAULT -1 FOR SchclassID",
"ALTER TABLE LeaveClass ADD CONSTRAINT mudf DEFAULT 1 FOR MinUnit",
"ALTER TABLE LeaveClass ADD CONSTRAINT utdf DEFAULT 1 FOR Unit",
"ALTER TABLE LeaveClass ADD CONSTRAINT rpdf DEFAULT 1 FOR RemaindProc",
"ALTER TABLE LeaveClass ADD CONSTRAINT rcdf DEFAULT 1 FOR RemaindCount",
"ALTER TABLE LeaveClass ADD CONSTRAINT rsdf DEFAULT '-' FOR ReportSymbol",
"ALTER TABLE LeaveClass ADD CONSTRAINT coldf DEFAULT 0 FOR Color",
"ALTER TABLE LeaveClass ADD CONSTRAINT cfydf DEFAULT 0 FOR Classify",
"ALTER TABLE LeaveClass ADD CONSTRAINT dedudf DEFAULT 0 FOR Deduct",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT mutdf DEFAULT 1 FOR MinUnit",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT uitdf DEFAULT 0 FOR Unit",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT rpcdf DEFAULT 2 FOR RemaindProc",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT rctdf DEFAULT 1 FOR RemaindCount",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT rsldf DEFAULT '_' FOR ReportSymbol",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT dctdf DEFAULT 0 FOR Deduct",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT colodf DEFAULT 0 FOR Color",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT cifydf DEFAULT 0 FOR Classify",
"ALTER TABLE LeaveClass1 ADD CONSTRAINT ltedf DEFAULT 0 FOR LeaveType",
"ALTER TABLE SchClass ADD CONSTRAINT cindf DEFAULT 1 FOR CheckIn",
"ALTER TABLE SchClass ADD CONSTRAINT coudf DEFAULT 1 FOR CheckOut",
"ALTER TABLE SchClass ADD CONSTRAINT colordf DEFAULT 16715535 FOR Color",
"ALTER TABLE SchClass ADD CONSTRAINT abdf DEFAULT 1 FOR AutoBind",
"CREATE UNIQUE INDEX USERFINGER ON TEMPLATE(USERID, FINGERID)",
"CREATE UNIQUE INDEX HOLIDAYNAME ON HOLIDAYS(HOLIDAYNAME)",
"CREATE INDEX DEPTNAME ON DEPARTMENTS(DEPTNAME)",
"CREATE UNIQUE INDEX EXCNOTE ON EXCNOTES(USERID, ATTDATE)",
"ALTER TABLE iclock ADD CONSTRAINT accfundf DEFAULT 0 FOR AccFun",
"ALTER TABLE iclock ADD CONSTRAINT tzadjdf DEFAULT 8 FOR TZAdj",
"ALTER TABLE user_temp_sch ADD CONSTRAINT ovt default 0 FOR OverTime",
    )
    batchSql(sqls);


def tryAddPermission(ct, cn, cname):
    try:
        Permission.objects.get(content_type=ct, codename=cn)
    except:
        try:
            Permission(content_type=ct, codename=cn, name=cname).save()
            print "Add permission %s OK"%cn
        except Exception, e:
            print "Add permission %s failed:"%cn, e

def checkAndCreateModelPermission(model):
    ct=ContentType.objects.get_for_model(model)

    cn='browse_'+model.__name__.lower()
    cname='Can browse %s'%model.__name__
    tryAddPermission(ct, cn, cname)
    for perm in model._meta.permissions:
        tryAddPermission(ct, perm[0], perm[1])

def checkAndCreateModelPermissions(appName):
    from django.db.models.loading import get_app
    from django.db import models
    app=get_app(appName)
    for i in dir(app):
        try:
            a=app.__getattribute__(i)
            if issubclass(a, models.Model):
                checkAndCreateModelPermission(a)
        except:
            pass
    try:
        ct=ContentType.objects.get_for_model(Transaction)
        Permission(content_type=ct, codename='init_database', name='Init database').save()
    except: pass
    try:        
        ct=ContentType.objects.get_for_model(Group)
        Permission(content_type=ct, codename='browse_'+Group.__name__.lower(), name='Can browse %s'%Group.__name__).save()
    except: pass

def __permission_unicode__(self):
    ct_id=self.content_type_id
    ckey="%s_ct_%s"%(settings.UNIT,ct_id)
    ct=cache.get(ckey)
    if not ct:
        ct=self.content_type
        cache.set(ckey, ct, 60*30)
    return u"%s | %s | %s" % (
        unicode(ct.app_label),
        unicode(ct),
        unicode(self.name))

Permission.__unicode__=__permission_unicode__

def __mci_init__(self, field):
    self.field = field
    q=[]
    for obj in field.queryset.all():
        q.append(obj)
    self.queryset=q

def __mci_iter__(self):
    if self.field.empty_label is not None:
        yield (u"", self.field.empty_label)
    if self.field.cache_choices:
        if self.field.choice_cache is None:
            self.field.choice_cache = [
                self.choice(obj) for obj in self.queryset
            ]
        for choice in self.field.choice_cache:
            yield choice
    else:
        for obj in self.queryset:
            yield self.choice(obj)

if settings.DATABASE_ENGINE=="ado_mssql":
    ModelChoiceIterator.__init__=__mci_init__
    ModelChoiceIterator.__iter__=__mci_iter__

def upgradeDB():
    sqls=(
    "ALTER TABLE userinfo ADD AutoSchPlan int NULL",
    "ALTER TABLE userinfo ADD MinAutoSchInterval int NULL",
    "ALTER TABLE userinfo ADD RegisterOT int NULL",
    "ALTER TABLE userinfo ADD Image_id int NULL",
    "ALTER TABLE SchClass ADD WorkDay int NULL",
    "ALTER TABLE iclock ADD PhotoStamp varchar(20) NULL",
    "ALTER TABLE iclock ADD FWVersion varchar(30) NULL",
    "ALTER TABLE iclock ADD FPCount varchar(10) NULL",
    "ALTER TABLE iclock ADD TransactionCount varchar(10) NULL",
    "ALTER TABLE iclock ADD UserCount varchar(10) NULL",
    "ALTER TABLE iclock ADD MainTime varchar(20) NULL",
    "ALTER TABLE iclock ADD MaxFingerCount int NULL",
    "ALTER TABLE iclock ADD MaxAttLogCount int NULL",
    "ALTER TABLE iclock ADD DeviceName varchar(30) NULL",
    "ALTER TABLE iclock ADD AlgVer varchar(30) NULL",
    "ALTER TABLE iclock ADD FlashSize varchar(10) NULL",
    "ALTER TABLE iclock ADD FreeFlashSize varchar(10) NULL",
    "ALTER TABLE iclock ADD Language varchar(30) NULL",
    "ALTER TABLE iclock ADD VOLUME varchar(10) NULL",
    "ALTER TABLE iclock ADD DtFmt varchar(10) NULL",
    "ALTER TABLE iclock ADD IPAddress varchar(20) NULL",
    "ALTER TABLE iclock ADD IsTFT varchar(5) NULL",
    "ALTER TABLE iclock ADD Platform varchar(20) NULL",
    "ALTER TABLE iclock ADD Brightness varchar(5) NULL",
    "ALTER TABLE iclock ADD BackupDev varchar(30) NULL",
    "ALTER TABLE iclock ADD OEMVendor varchar(30) NULL",
    "ALTER TABLE iclock ADD AccFun int NOT NULL DEFAULT 0",
    "ALTER TABLE iclock ADD TZAdj int NOT NULL DEFAULT 8",
    "ALTER TABLE checkinout ADD WorkCode VARCHAR(20) NULL",
    "ALTER TABLE checkinout ADD Reserved VARCHAR(20) NULL",
    "ALTER TABLE iclock DROP COLUMN CheckInterval")
    batchSql(sqls)
    from mysite.iclock.modpin import checkPINWidth
    checkPINWidth()                                        

def initDB():
    from mysite.iclock.models import AttParam,LeaveClass,LeaveClass1,department,iclock
    try:
        checkAndCreateModelPermissions(Device._meta.app_label)
    except: pass

    upgradeDB()
    createDefautValue()
#    return
    if AttParam.objects.all().count()==0:
        AttParam(ParaName='MinsEarly',ParaValue="5").save()
        AttParam(ParaName='MinsLate',ParaValue="10").save()
        AttParam(ParaName='MinsNoBreakIn',ParaValue="60").save()
        AttParam(ParaName='MinsNoBreakOut',ParaValue="60").save()
        AttParam(ParaName='MinsNoIn',ParaValue="60").save()
        AttParam(ParaName='MinsNoLeave',ParaValue="60").save()
        AttParam(ParaName='MinsNotOverTime',ParaValue="60").save()
        AttParam(ParaName='MinsWorkDay',ParaValue="420").save()
        AttParam(ParaName='NoBreakIn',ParaValue="1012").save()
        AttParam(ParaName='NoBreakOut',ParaValue="1012").save()
        AttParam(ParaName='NoIn',ParaValue="1001").save()
        AttParam(ParaName='NoLeave',ParaValue="1002").save()
        AttParam(ParaName='OutOverTime',ParaValue="0").save()
        AttParam(ParaName='TwoDay',ParaValue="0").save()
        AttParam(ParaName='CheckInColor',ParaValue="16777151").save()
        AttParam(ParaName='CheckOutColor',ParaValue="12910591").save()
        AttParam(ParaName='DBVersion',ParaValue="167").save()
    if LeaveClass.objects.all().count()==0:
        LeaveClass(LeaveName="%s"%'Sick leave',Unit=1,ReportSymbol='B',Color=3398744).save()
        LeaveClass(LeaveName="%s"%'Private affair leave',Unit=1,ReportSymbol='S',Color=8421631).save()
        LeaveClass(LeaveName="%s"%'Home leave',Unit=1,ReportSymbol='T',Color=16744576).save()
    if LeaveClass1.objects.all().count()==0:
#        for i in range(1, 999):
#            l=LeaveClass1(LeaveName=u'正常')
#            l.save()
#            l.delete()
        LeaveClass1(LeaveID=999,LeaveName="%s"%'BL',MinUnit=0.5,Unit=3,RemaindProc=1,RemaindCount=1,ReportSymbol='G',LeaveType="3",Calc='if(AttItem(LeaveType1)=999,AttItem(LeaveTime1),0)+if(AttItem(LeaveType2)=999,AttItem(LeaveTime2),0)+if(AttItem(LeaveType3)=999,AttItem(LeaveTime3),0)+if(AttItem(LeaveType4)=999,AttItem(LeaveTime4),0)+if(AttItem(LeaveType5)=999,AttItem(LeaveTime5),0)').save()
        LeaveClass1(LeaveID=1000,LeaveName="%s"%'OK',MinUnit=0.5,Unit=3,RemaindProc=1,RemaindCount=0,ReportSymbol=' ',LeaveType="3").save()
        LeaveClass1(LeaveID=1001,LeaveName="%s"%'Late',MinUnit=10,Unit=2,RemaindProc=2,RemaindCount=1,ReportSymbol='>',LeaveType="3",Calc='AttItem(minLater)').save()
        LeaveClass1(LeaveID=1002,LeaveName="%s"%'Early',MinUnit=10,Unit=2,RemaindProc="2",RemaindCount="1",ReportSymbol='<',LeaveType="3",Calc='AttItem(minEarly)').save()
        LeaveClass1(LeaveID=1003,LeaveName="%s"%'ALF',MinUnit="1",Unit="1",RemaindProc="1",RemaindCount="1",ReportSymbol='V',LeaveType="3",Calc='if((AttItem(LeaveType1)>0) and (AttItem(LeaveType1)<999),AttItem(LeaveTime1),0)+if((AttItem(LeaveType2)>0) and (AttItem(LeaveType2)<999),AttItem(LeaveTime2),0)+if((AttItem(LeaveType3)>0) and (AttItem(LeaveType3)<999),AttItem(LeaveTime3),0)+if((AttItem(LeaveType4)>0) and (AttItem(LeaveType4)<999),AttItem(LeaveTime4),0)+if((AttItem(LeaveType5)>0) and (AttItem(LeaveType5)<999),AttItem(LeaveTime5),0)').save()
        LeaveClass1(LeaveID=1004,LeaveName="%s"%'Absent',MinUnit="0.5",Unit="3",RemaindProc="1",RemaindCount="0",ReportSymbol='A',LeaveType="3",Calc='AttItem(MinAbsent)').save()
        LeaveClass1(LeaveID=1005,LeaveName="%s"%'OT',MinUnit="1",Unit="1",RemaindProc="1",RemaindCount="1",ReportSymbol='+',LeaveType="3",Calc='AttItem(MinOverTime)').save()
        LeaveClass1(LeaveID=1006,LeaveName="%s"%'OTH',MinUnit="1",Unit="1",RemaindProc="0",RemaindCount="1",ReportSymbol='=',LeaveType="0",Calc='if(HolidayId(1)=1, AttItem(MinOverTime),0)').save()
        LeaveClass1(LeaveID=1007,LeaveName="%s"%'Hol.',MinUnit="0.5",Unit="3",RemaindProc="2",RemaindCount="1",ReportSymbol='-',LeaveType="2").save()
        LeaveClass1(LeaveID=1008,LeaveName="%s"%'NoIn',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='[',LeaveType="2",Calc='If(AttItem(CheckIn)=null,If(AttItem(OnDuty)=null,0,if(((AttItem(LeaveStart1)=null) or (AttItem(LeaveStart1)>AttItem(OnDuty))) and AttItem(DutyOn),1,0)),0)').save()
        LeaveClass1(LeaveID=1009,LeaveName="%s"%'NoOut',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol=']',LeaveType="2",Calc='If(AttItem(CheckOut)=null,If(AttItem(OffDuty)=null,0,if((AttItem(LeaveEnd1)=null) or (AttItem(LeaveEnd1)<AttItem(OffDuty)),if((AttItem(LeaveEnd2)=null) or (AttItem(LeaveEnd2)<AttItem(OffDuty)),if(((AttItem(LeaveEnd3)=null) or (AttItem(LeaveEnd3)<AttItem(OffDuty))) and AttItem(DutyOff),1,0),0),0)),0)').save()
        LeaveClass1(LeaveID=1010,LeaveName="%s"%'ROT',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='{',LeaveType="3").save()
        LeaveClass1(LeaveID=1011,LeaveName="%s"%'BOUT',MinUnit="1",Unit="4",RemaindProc="2",RemaindCount="1",ReportSymbol='}',LeaveType="3").save()
        LeaveClass1(LeaveID=1012,LeaveName="%s"%'OUT',MinUnit="1",Unit="1",RemaindProc="2",RemaindCount="1",ReportSymbol='L',LeaveType="3").save()
        LeaveClass1(LeaveID=1013,LeaveName="%s"%'FOT',MinUnit="1",Unit="1",RemaindProc="2",RemaindCount="1",ReportSymbol='F',LeaveType="3").save()

    if department.objects.all().count()==0:
        department(DeptName='Our Company', DeptID=1).save()




