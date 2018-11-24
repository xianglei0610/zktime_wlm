#!/usr/bin/env python
#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.cache import cache
import string
import datetime
import time
from traceback import print_exc
from models.modelproc import getEmpCmdStr
#from dbapp.utils import *
from django.conf import settings
#from django.contrib.auth.models import User
#from django.utils.encoding import smart_str
import sys,os
#from django.db import connection as conn
#from reb import *
from django.utils.translation import ugettext_lazy as _, ugettext 

def batchOp(request, dataModel, func):
        if request.method == 'POST':
                keys=request.POST.getlist("K")
        else: 
                keys=request.GET.getlist("K")
        info=[]
        ret=None
        t1=datetime.datetime.now()
        settings.DEV_STATUS_SAVE=1
        try:
                for i in keys:
                        if dataModel==USER_SPEDAY:
                                deleteCalcLog(UserID=int(i))
                        d=dataModel.objects.in_bulk([i])
                        dev=d[d.keys()[0]]
                        ret=func(dev)
                if ("%s"%ret)==ret:
                        info.append(ret)
        except:
                pass
        settings.DEV_STATUS_SAVE=0
        #if len(keys)<3:
                #for i in keys:
                        #d=dataModel.objects.in_bulk([i])
                        #dev=d[d.keys()[0]]
                        #sendRecCMD(dev)

        t1=datetime.datetime.now()-t1
        if len(info)>0:
                return u',\n'.join([u"%s"%f for f in info])
        return ret

def getFW(dev):
        ds=dev.device_name

        if not ds:
                ds=''
        else:
                ds=ds+"/"
        return ("file/fw/%smain.gz"%ds, "%sfw/%smain.gz"%(settings.ADDITION_FILE_ROOT,ds))

def appendDevCmdOld(dObj, cmdStr, Op, cmdTime=None):
        from mysite.iclock.models.model_devcmd import DevCmd
        try:
            #print cmdStr
            cmd=DevCmd(SN=dObj, CmdOperate=Op, CmdContent=cmdStr, CmdCommitTime=(cmdTime or datetime.datetime.now()))
            cmd.save(force_insert=True)
            return cmd.id
        except:
            print_exc()

def append_dev_cmd(dObj, cmdStr, Op=None, cursor=None, cmdTime=None):
        appendDevCmdOld(dObj, cmdStr, Op, cmdTime)

def appendDevCmdReturn(dObj, cmdStr):
    from mysite.iclock.models.model_devcmd import DevCmd
    try:
        cmd=DevCmd(SN=dObj, CmdContent=cmdStr, CmdCommitTime=datetime.datetime.now(), CmdImmediately=True)
        cmd.save(force_insert=True)
        return cmd.id 
    except:
        print_exc()

def dev_update_firmware(dev):
        ds=dev.fw_version
        if not ds:
                return _(u"设备%(object_name)s固件版本号未知")%{'object_name':dev}
        else:
                mainVer, timeVer=ds[:8], ds[9:] #Ver 6.36 Oct 26 2007
#               if not (mainVer=="Ver 6.36" or (ds in [
#                                'Ver 2.00 Oct 29 2007','Ver 2.00 Oct 30 2007','Ver 6.18 Oct 31 2007',
#                                'Ver 6.18 Oct 29 2007','Ver 6.18 Oct 30 2007'])):
#                        return _("device %(objdet_name)s Firmware does not support the way through the server upgrade features")%{'object_name':dev}
        url, fname=getFW(dev)
        if os.path.exists(fname):
                append_dev_cmd(dev, "PutFile %s\tmain.gz.tmp"%url)
        else:
                return _(u"服务器上的固件文件%(object_name)s 不存在，不能对设备%(esc_name)s升级固件")%{'object_name':fname,'esc_name': dev}

def append_emp_to_dev(dev, emp, cursor=None, onlyEnrollDev=False, cmdTime=None):
        from mysite.iclock.models import Template
        bdev=None
        edev=emp.device()
        if (not onlyEnrollDev) and edev and (edev.SN==dev.SN): 
                        bdev=dev.backup_device()
        s=getEmpCmdStr(emp)
        append_dev_cmd(dev, s, cursor, cmdTime)
        if bdev: append_dev_cmd(bdev, s, cursor, cmdTime)
        fps=Template.objects.filter(UserID=emp)
        for fp in fps:
                if fp.Template:
                        try:
                                #print "tmp: ", fp.Template
                                s=u"DATA FP PIN=%s\tFID=%d\tValid=1\tTMP=%s"%(emp.pin(), fp.FingerID, fp.temp())
                                append_dev_cmd(dev, s, cursor, cmdTime)
                                if bdev: append_dev_cmd(bdev, s, cursor, cmdTime)
                        except:
                                errorLog()
        return cursor

def delEmpFromDev(superuser, emp, dev): #从机器中删除员工，如果没有指定机器的话，删除数据库中的员工同时在登记机和备份机中删除
        pin=emp.pin()
        if dev:
                return append_dev_cmd(dev, "DATA DEL_USER PIN=%s"%pin)
        if emp.SN:
                bk=emp.SN.BackupDevice()
                if bk:        
                        append_dev_cmd(bk, "DATA DEL_USER PIN=%s"%pin)
                append_dev_cmd(emp.SN, "DATA DEL_USER PIN=%s"%pin)
        if superuser:
                emp.OffDuty=1
                emp.save()

def copyDevEmpToDev(ddev, sdev, cursor=None):
        from mysite.personnel.models import Employee
        ret=cursor
        if ddev.SN==sdev.SN:
#                print "Dest and Source are same"
                return ret
        emps=Employee.objects.all().filter(SN=sdev).filter(DeptID__isnull=False)
        for e in emps:
                ret=append_emp_to_dev(ddev, e, cursor)
        return ret

def reloadDataCmd(dObj):
        dObj.OpLogStamp=0;
        dObj.LogStamp=0;
        dObj.save();
        append_dev_cmd(dObj, "CHECK");

def reloadLogDataCmd(dObj):
        dObj.LogStamp=0;
        dObj.save();
        append_dev_cmd(dObj, "CHECK");

def rebootDevice(dev):
        if dev.get_dyn_state()==DEV_STATUS_OK:
                append_dev_cmd(dev, "REBOOT")
        elif dev.IPAddress:
                rebDevs([dev.IPAddress])

def getValidDevOptions():
        return ["AutoPowerSuspend","COMKey"]
def setOpt(dev,params):
        errorInfo=""
        optName=string.strip(params["name"])
        optVal=string.strip(params["value"])
        if optName in getValidDevOptions():
                optName="SET OPTION %s %s"%(optName, optVal)
                append_dev_cmd(dev, optName)
        else:
                errorInfo=_(u"考勤机选项\"%s\"不可用")%optName
                return errorInfo

def resetPwd(dev, pin, pwd, cursor):
        if pin=="0":
                append_dev_cmd(dev, "RESET PWD PIN=%s\tPasswd=%s"%(1,pwd), cursor)
                append_dev_cmd(dev, "RESET PWD PIN=%s\tPasswd=%s"%(2,pwd), cursor)
        else:
                append_dev_cmd(dev, "RESET PWD PIN=%s\tPasswd=%s"%(pin,pwd), cursor)
        return cursor

def strToDateDef(s, defTime=None):
        import time
        d=datetime.datetime.now()
        print "s:%s"%s
        print settings.STD_DATETIME_FORMAT
        try:
                t=time.strptime(s, settings.STD_DATETIME_FORMAT)
                
                d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday,
                        t.tm_hour, t.tm_min, t.tm_sec)
                
        except:
                try:#只有日期
                        t=time.strptime(s, settings.STD_DATETIME_FORMAT.split(" ")[0])
                        if defTime:
                                d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, defTime[0], defTime[1], defTime[2])
                        else:
                                d=datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday)
                except Exception, e: #只有时间
#                        print e.message
                        t=time.strptime(s, settings.STD_DATETIME_FORMAT.split(" ")[1])                
                        d=datetime.datetime(d.year, d.month, d.day,
                                t.tm_hour, t.tm_min, t.tm_sec)
        return d

def empLeave(emp):
        dev=emp.device()
        emp.OffDuty=1
        emp.save()
        pin=emp.pin()
        if dev:
                append_dev_cmd(dev, "DATA DEL_USER PIN=%s"%pin)
                bdev=dev.backup_device()
                if bdev:
                        append_dev_cmd(bdev, "DATA DEL_USER PIN=%s"%pin)
                        return #_("The command to delete employee %s from device %s and it's backup device %s has been sent.")%(emp, dev, bdev)
                return #_("The command to delete employee %s from device %s has been sent.")%(emp, dev)
        return #_("Employee %s has no a registration device")%emp
def restoreEmpLeave(emp):
        from mysite.personnel.models import Employee
        try:
                emp.OffDuty=0
                #sql="update %s set OffDuty='%s' where userid=%s"%(employee._meta.db_table,'0',emp.id)
                #customSql(sql)
                emp.save()
        except:
                pass

def moveEmpToDev(dev, emp, cursor=None):#转移人员数据到新设备上
        pin=emp.pin()
        device=emp.SN
        if device:
                if dev.SN==device.SN: #人员的登记设备保持不变
                        return None
                append_dev_cmd(device, "DATA DEL_USER PIN=%s"%pin, cursor) #从原登记设备中删除
                device=emp.SN.backup_device()
                if device:
                        append_dev_cmd(device, "DATA DEL_USER PIN=%s"%pin, cursor) #从备份设备中删除
        emp.SN=dev #更改人员的登记设备
        emp.save()
        return append_emp_to_dev(dev, emp, cursor) #把人员的信息传送到新设备中        
def changeEmpDept(dept, emp):
        emp.DeptID=dept
        emp.save()
def enrollAEmp(dev, emp):
        from mysite.iclock.models import Template
        from mysite.personnel.models.model_emp import device_pin
        if not dev: dev=emp.Device()
        if not dev: return _(u"没有指定登记设备")
        fids=Template.objects.filter(UserID=emp).values_list('FingerID')
        for i in range(10):
                if (i,) not in fids:
                        append_dev_cmd(dev, "ENROLL_FP PIN=%s\tFID=%d\tRETRY=%d\tOVERWRITE=0"%(device_pin(emp.PIN), i, 3))
                        return
        return _(u'所有指纹已经被登记')

def appendEmpToDevWithin(dev, emp, startTime, endTime, cursor=None):
        pin=emp.pin()
        edev=emp.device()
        if not edev or (edev.SN!=dev.SN):
                append_emp_to_dev(dev, emp, cursor, False, startTime)
                if endTime and (endTime.year>2007):
                        append_dev_cmd(dev, "DATA DEL_USER PIN=%s"%pin, cursor, endTime)
                #delete at endTime
        return cursor

def appendDevCmdNew(SNS, cmdStr, cursor=None, cmdTime=None):
#        for sn in SNS:
#                sql="insert into devcmds(sn_id, cmdcontent, cmdcommittime) values('%s','%s','%s')"%(sn, cmdStr, str(cmdTime or datetime.datetime.now())[:19])
#                customSql(sql)
#                deviceHasCmd(sn)
    pass
def appendEmpToDevNew(dev, emp, cursor=None, onlyEnrollDev=False, cmdTime=None):
        bdev=None
#        edev=emp.Device()
#        if (not onlyEnrollDev) and edev and (edev.SN==dev.SN): 
#                        bdev=dev.BackupDevice()
        s=getEmpCmdStr(emp)
        appendDevCmdNew(dev, s, cursor, cmdTime)
#        if bdev: append_dev_cmd(bdev, s, cursor, cmdTime)
        fps=fptemp.objects.filter(UserID=emp)
        for fp in fps:
                if fp.Template and len(fp.Template)>50:
                        try:
                                #print "tmp: ", fp.Template
                                s=u"DATA FP PIN=%s\tFID=%d\tValid=1\tTMP=%s"%(emp.pin(), fp.FingerID, fp.temp())
                                appendDevCmdNew(dev, s, cursor, cmdTime)
#                                if bdev: append_dev_cmd(bdev, s, cursor, cmdTime)
                        except:
                                errorLog()
        return cursor
