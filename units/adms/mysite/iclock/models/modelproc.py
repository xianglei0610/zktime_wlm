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
from mysite.iclock.models.model_devcmd import DevCmd

def set_value_dic(data):
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

def checkTime(t):
    if str(type(t))=="<type 'datetime.datetime'>":
            return datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.time'>":
            return datetime.datetime(1899,12,30,t.hour,t.minute,t.second)
    elif str(type(t))=="<type 'datetime.date'>":
            return datetime.datetime(t.year,t.month,t.day,0,0,0)




def ValidIClocks(qs):
    return qs.filter(Q(DelTag__isnull=True)|Q(DelTag=0)).order_by("Alias")



def get_normal_card(card):
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
                    emp.Card and ("Card=%s"%get_normal_card(emp.Card)) or "", 
                    emp.TimeZones and ("TZ=%s"%emp.TimeZones) or "", 
                    emp.AccGroup or 1)
                                                                            
    return ret                                                        


def is_updating_fw(device):
    return DevCmd.objects.filter(SN=device, CmdReturn__isnull=True, CmdContent__startswith='PutFile ', CmdContent__endswith='main.gz.tmp',).count()

def clearData():
    from mysite.personnel.models import Employee
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
#        from django.db import connection
    cursor = connection.cursor()
    
    cursor.execute(sql)
    if action:
            connection._commit()
    return cursor


def createDefautValue():
#    from mysite.iclock.sql import createDefautValue_sql
#    sqls=createDefautValue_sql()
    
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
"CREATE INDEX DEPTNAME ON DEPARTMENTS(DEPTNAME)",
"CREATE UNIQUE INDEX EXCNOTE ON EXCNOTES(USERID, ATTDATE)",
"ALTER TABLE iclock ADD CONSTRAINT accfundf DEFAULT 0 FOR AccFun",
"ALTER TABLE iclock ADD CONSTRAINT tzadjdf DEFAULT 8 FOR TZAdj",
    )
    batchSql(sqls);


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

if "ado_mssql" in settings.DATABASES['default']['ENGINE']:
    ModelChoiceIterator.__init__=__mci_init__
    ModelChoiceIterator.__iter__=__mci_iter__

def upgradeDB():
    sqls=(
    "ALTER TABLE userinfo ADD AutoSchPlan int NULL",
    "ALTER TABLE userinfo ADD MinAutoSchInterval int NULL",
    "ALTER TABLE userinfo ADD RegisterOT int NULL",
    "ALTER TABLE userinfo ADD Image_id int NULL",
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

    from mysite.personnel.models.model_dept import Department
    from model_device import Device
    try:
            checkAndCreateModelPermissions(Device._meta.app_label)
    except: pass

    upgradeDB()
    createDefautValue()
    if Department.objects.all().count()==0:
            department(name='Our Company', id=1).save()




