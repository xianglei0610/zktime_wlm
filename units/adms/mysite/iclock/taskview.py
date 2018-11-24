#!/usr/bin/env python
#coding=utf-8
from models import *
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import string
import datetime
import time
import re
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User
from cab import *
import reb
import os, time
from dataprocaction import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext
from mysite.personnel.models import Employee, Department

def AppendUserDev(dispEmp, SNs, cursor):
        needSave=False
        try:
                pin=format_pin(dispEmp[0])
                try:
                        e=Employee.objects.get(PIN=pin)
                        if e.SN and (SNs!=settings.ALL_TAG) and (e.SN.SN not in SNs):
                                return _(u"没有权限传送 %s 上登记的人员")%e.SN.SN #u"没有权限传送 %s 上登记的人员"%e.SN.SN
                except:
                        e=employee(PIN=pin, DeptID=get_default_dept())
                        needSave=True
                try:
                        device=get_device(dispEmp[1])
                        if (SNs!=settings.ALL_TAG) and (device.SN not in SNs):
                                return _(u"没有权限传送人员到设备 %s")%device.SN #u"没有权限传送人员到设备 %s"%device.SN
                except:
                        if dispEmp[1]:
                                return _(u"指定的考勤机不存在") #u"指定设备不存在"
                        elif SNs!=settings.ALL_TAG:
                                return _(u"没有指定设备") #u"没有指定设备"
                        device=None
#                print "employee: dept=%s, sn=%s"%(e.DeptID, e.SN)
                if not e.DeptID:        #没有部门表示该员工已经被删除，所以需要恢复
                        e.DeptID=get_default_dept()
                        needSave=True
#                        print "save Dept of employee:", e
                if device and not e.SN: #没有登记设备的人员，则指定登记设备
                        e.SN=device
                        needSave=True
#                        print "save device of employee:", e
                if needSave: e.save()
                if not device:        return
                append_dev_cmd(device, getEmpCmdStr(e)) #, UserName=User.username)
                for afp in fptemp.objects.filter(UserID=e):
#                        print e.PIN, afp.FingerID
                        append_dev_cmd(device, u"DATA FP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s"%\
                                (e.pin(), afp.FingerID, 0, afp.Valid, afp.temp()))
        except Exception, e:
                errorLog()
                return "%s"%e

#"DATA DEL_USER PIN=%s"
def DelUserDev(dispEmp, SNs, cursor):
        try:
                pin=format_pin(dispEmp[0])
                try:
                        e=Employee.objects.get(PIN=pin)
                        if not e.DeptID:
                                return _(u"指定人员不存在")#u"指定人员不存在"
                except:
                        return _(u"指定人员不存在")#u"指定人员不存在"
                try:
                        device=get_device(dispEmp[1])
                        if (SNs!=settings.ALL_TAG) and (device.SN not in SNs):
                                return _(u"没有权限删除设备 %s 中的人员")%device #"没有权限删除设备 %s 中的人员"%device
                except:
                        if dispEmp[1]:
                                return _(u"指定的考勤机不存在!")
                        elif (SNs!=settings.ALL_TAG and (not e.SN or (e.SN_id not in SNs))):
                                if e.SN:
                                        return _(u"没有指定设备， 并且没有权限从登记设备 %s 中删除该人员")%e.SN #u"没有指定设备"+u", 并且没有权限从登记设备 %s 中删除该人员"%e.SN
                                else:
                                        return _(u"没有指定设备，并且该人员没有登记设备") #u"没有指定设备，并且该人员没有登记设备")
                        device=None
                delEmpFromDev(SNs==settings.ALL_TAG, e, device)
        except Exception, e:
                return "%s"%e

def NameUserDev(dispEmp, SNs, cursor):
        newUser=False
        assignDev=False
        try:
                device=get_device(dispEmp[2])
        except:
                device=None
        try:
                userName=dispEmp[1]
        except:
                userName=u""
        try:
                pin=dispEmp[0]
                if pin in DISABLED_PINS or re.compile(r'^0+$').match(pin) or len(pin)>settings.PIN_WIDTH:
                        return _(u"%s 不是一个合法的考勤号码")%pin #pin+u" 不是一个合法的考勤号码"
                try:
                        e=Employee.objects.get(PIN=pin)
                except:
                        e=employee(PIN=pin, EName=userName, DeptID=get_default_dept())
                        if device: e.SN=device
                        e.save()
                        newUser=True
                else:
                        if (not e.DeptID) or (userName and (userName!=e.EName)) or (device and not e.SN):
                                e.DeptID=get_default_dept()
                                e.EName=userName
                                if not e.SN:
                                        assignDev=True
                                        e.SN=device
                                e.save()

                        userName=e.EName
                        if not device:
                                device=e.SN
                if not device:
                        return _(u"没有指定合适的考勤机，或者该人员没有登记考勤机！")#u"没有指定合适的考勤机，或者该人员没有登记考勤机"
                if (not newUser) and not userName:
                        return _(u"该用户在数据库中还没有录入姓名")#u"该用户在数据库中还没有录入姓名"
                backDev=device.backup_device()
                sql= u"DATA USER PIN=%s\tName=%s"%(e.pin(), e.EName)
                append_dev_cmd(device, sql, cursor)
                if backDev:
                        append_dev_cmd(backDev, sql, cursor)
                if assignDev: #新用户同时传送指纹
                        for afp in fptemp.objects.filter(PIN=e):
                                #print e.PIN, afp.FingerID
                                sql=u"DATA FP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s"%\
                                        (e.pin(), afp.FingerID, 0, afp.Valid, afp.temp())
                                append_dev_cmd(device, sql, cursor)
                                if backDev:
                                        append_dev_cmd(backDev, sql, cursor)
        except Exception, e:
                return "%s"%e


def disp_emp(request, delemp):
        from django.db import connection as conn
        cursor = conn.cursor()
        task=(delemp and u"deluser" or ((request.path.find("name_emp")>=0) and u"username" or u"userinfo"))
        titles={"deluser": _(u"删除考勤机上的人员"),# u"删除考勤机上的人员",
                "username":_(u"传送人员姓名到考勤机"),# u"传送人员姓名到考勤机",
                "userinfo":_(u"分派人员到考勤机")}# u"分派人员到考勤机"}
        title=titles[task]
        if not (request.method == 'POST'):
                return render_to_response("disp_emp.html", {"title": title, 'task': task})
        #POST
        cc=u""

        SNs=request.user.is_superuser and settings.ALL_TAG or getUserIclocks(request.user)

        process=(task=="deluser") and DelUserDev or ((task=="userinfo") and AppendUserDev or NameUserDev)
        errorLines=[]
        i=0;
        okc=0;
        f=request.FILES["fileUpload"]
        lines=""
        for chunk in f.chunks():
                lines+=chunk
        lines=lines.decode("GBK").split("\n")
        for line in lines:
                i+=1;
                if line:
                        if line[-1] in ['\r','\n']: line=line[:-1]
                if line:
                        if line[-1] in ['\r','\n']: line=line[:-1]
                try:
#                        print line
                        if line:
                                if line.find("\t")>=0:
                                        data=(line+"\t").split("\t")
                                elif line.find(",")>=0:
                                        data=(line+",").split(",")
                                else:
                                        data=(line+" ").split(" ",1)
                                error=process(data,SNs,cursor)
                                if error:
                                        errorLines.append(u"Line %d(%s):%s"%(i,line,error))
                                okc+=1
                except  Exception, e:
                        errorLines.append(u"Line %d(%s):%s"%(i,line,str(e)))
        if okc:
                conn._commit()
        if len(errorLines)>0:
                if okc>0:
                        cc+=(_(u"%s位员工处理数据已经提交准备传送, 但是发生如下错误:")%okc)+"</p><pre>" # u"%d 位员工处理数据已经提交准备传送, 但是发生如下错误:</p><pre>"%okc
                else:
                        cc+=_(u"没有员工处理数据被传送, 发生如下错误")+"</p><pre>" # u"没有员工处理数据被传送, 发生如下错误:\n</p><pre>"
                cc+=u"\n".join(errorLines)
                cc+=u"</pre>"
        else:
                cc+=_(u"%s位员工处理数据已经提交准备传送")%okc# u"%d 位员工处理数据已经提交准备传送"%okc
        return render_to_response("info.html", {"title": title, "content": cc})

@login_required
def FileDelEmp(request):
        return disp_emp(request, True)

@login_required
def FileChgEmp(request):
        return disp_emp(request, False)

@login_required
def disp_emp_log(request):
        return render_to_response("disp_emp_log.html",{"title": _(u"分派人员到考勤机")})# u"分派人员到考勤机"})

def saveUser(pin, pwd, ename, card, grp, tzs):
        try:
                e=Employee.objects.get(PIN=pin)
        except:
                e=employee(PIN=pin, DeptID=get_default_dept())
        if ename: e.EName=unicode(ename,"gb2312")
#        if card: e.Card=card
        if pwd: e.Password=pwd
        if grp: e.AccGroup=grp
        if tzs: e.TimeZones=tzs
        e.save()

def saveFTmp(pin, fid, tmp):
        try:
                t=fptemp.objects.get(PIN=Employee.objects.get(PIN=pin), FingerID=fid)
                if t.Template!=tmp:
                        t.Template=tmp
                        t.save()
        except:
                t=fptemp(PIN=Employee.objects.get(PIN=pin), FingerID=fid, Valid=1, Template=tmp)
                t.save()

@login_required
def app_emp(request):
        if not (request.method == 'POST'):
                return render_to_response("disp_emp.html",{"title": _(u"批量上传人员列表"), # u"批量上传人员列表",
                                'task':'userinfo'})
        i=0;
        f=request.FILES["fileUpload"]
        data=""
        for chunk in f.chunks(): data+=chunk
        lines=data.splitlines()
        pin,ename,pwd,card,grp,tzs='','','','','1',''
        userTmp=[]
        for line in lines:
#                try:
                if line.find('[Users_')==0:
                        i+=1;
                        if(len(pin)>0):
                                saveUser(pin, pwd, ename, card, grp, tzs)
                                for tmp in userTmp:
                                        saveFTmp(pin, tmp['fid'], tmp['tmp'])
                        pin=line[7:-1]
                        ename,pwd,card,grp,tzs='','','','1',''
                        userTmp=[]
                elif line.find('Name=')==0: ename=line[5:]
                elif line.find('Password=')==0: pwd=line[9:]
                elif line.find('AccTZ1=')==0: tzs=line[7:]
                elif line.find('Card=')==0: card=line[5:]
                elif line.find('Grp=')==0: grp=line[4:]
                elif line.find('FPT_')==0:
                        ftmp=line.split('=')
                        fid=ftmp[0][4:]
                        userTmp.append({"fid":fid, "tmp":ftmp[1]})
#                except  Exception, e:
#                        errorLines.append("LINE(%d):%s :%s"%(i,str(e),line))
        if(len(pin)>0):
                saveUser(pin, pwd, ename, card, grp, tzs)
                for tmp in userTmp:
                        saveFTmp(pin, tmp['fid'], tmp['tmp'])
        response = HttpResponse(mimetype='text/plain')
        response.write(_(u"%(object)s 人员已经成功!")%{'object':i});
        return response


@login_required
def del_emp_log(request):
        return render_to_response("disp_emp_log.html",{"title": _(u"在设备中删除人员"), 'task':'deleteuser'})

@login_required
def upgrade(request):
        if not (request.method == 'POST'):
                return render_to_response("upgrade.html",{"title": _(u"服务器升级")})
        i=0;
        f=request.FILES["fileUpload"]
        bytes=""
        for chunk in f.chunks(): bytes+=chunk
        target=tmpDir()+"/mysite.zip"
        bkFile="%s/%s.zip"%(tmpDir(),time.strftime("%Y%m%d%H%M%S"))
        file(target,"wb+").write(bytes)
        zipDir('c:/mysite/', bkFile)
        fl=unzipFile(target, 'c:/')
        response = HttpResponse(mimetype='text/plain')
        response.write("BACKUP OLD FILE TO: "+bkFile+"\r\n"+("\r\n".join([("%s\t%s"%(fl[f], f)) for f in fl.keys()])));
        if fl:
                restartThread("iclock-server").start()
                restartThread("iclock").start()
                restartThread("Apache2").start()
        return response

from gzip import *
def getGZipSize(fname):
        g=GzipFile(filename=fname, mode="rb")
        s=0
        while True:
                chunk=g.read(1024)
                cs=len(chunk)
                if cs>0:
                        s+=cs
                else:
                        break
        return s


@login_required
def restartDev(request):
        ip=request.GET.get("IP","")
        if ip:
                url, fname=getFW(iclock(Style="X938"))
                fwSize=getGZipSize(fname)
                ret=reb.tryDoInDev(ip,["ls /mnt/mtdblock/main -l","reboot"])
                if type(ret).__doc__.find("list")==0:
#                        if ret[0].find(" %s"%fwSize)<10:
#                                ret=reb.tryDoInDev(ip,["cd /mnt/mtdblock/","wget http://192.168.1.254/iclock/file/fw/X938/main.gz","reboot"])
                        ret=_(u"成功重启设备")+ip+"</p><p>"+(ret[0].find(" %s"%fwSize)<10 and ret[0]+"</p><p>"+_("其固件大小与标准%(object_name)s需要升级固件，稍后检查如果没有自动进行固件升级的话，请手工升级固件")%{'object_name':fwSize or ""})
                else:
                        ret=_(u"重新启动机器失败")+ip+"</p><p>"+ret
        else:
                ret=_(u"请输入一个有效的 IP 地址。")
        return render_to_response("info.html",{"title": _(u"程序重新启动"), 'content': ret})

@login_required
def autoRestartDev(request):
        iclocks=Device.objects.filter(LastActivity__lt=datetime.datetime.now()-datetime.timedelta(0,(settings.REBOOT_CHECKTIME>30 and settings.REBOOT_CHECKTIME or 30)*60))
        ips=updateLastReboot(iclocks)
        rebDevsReal(ips)
        return render_to_response("info.html",{"title": _(u"自动检查呆滞设备"), 'content':gettext("The device(s) does not connect with the server more than half and an hour: </p><p>")+("<br />".join([u"%s: %s"%(i, i.IPAddress()) for i in iclocks]))+"</p><p>&nbsp;</p><p>"+(ips and gettext("The system will connect and re-start the following device automaticly: </p><p>")+("<br />".join(ips)) or "")})

