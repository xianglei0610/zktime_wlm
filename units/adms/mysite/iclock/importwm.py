#coding=utf-8
from mysite.iclock.models import *
from mysite.iclock.devview import checkDevice, commitLog
from django.shortcuts import render_to_response
import time, datetime
from mysite.iclock.empdevsyn import *
from django.conf import settings
from mysite.personnel.models import Employee, Department


#新入职人员的工号,卡号,姓名,employee20080815165451.txt
#SampleEmp="""
#I        10000165        00000000        李三
#I        10000172        87654321        赵四(xjl test)
#D        00000190        00000000        C007100038"""

import os
from ftplib import FTP

def insertEmp(pin, card, name):
        try:
                card="%s"%int(card)
        except:
                pass
        try:
                emp=Employee.objects.get(PIN=pin)
        except:
                emp=employee(PIN=pin, Card=card, EName=name)
                print "New employee: %s, %s"%(pin,name)
        else:
                if emp.EName==name and emp.Card==card and not emp.DelTag:
                        print "Employee %s already exists"%pin
                        return
                emp.EName=name
                emp.Card=card
                emp.DelTag=0
                print "Modify employee: %s"%emp         
        try:
                emp.save()
                dispatchEmpToAll(emp)
        except Exception, e:
                print e.message

def deleteEmp(pin):
        deleteEmpFromAll(pin)
        print "Delete employee %s from devices"%pin
        try:
                emp=Employee.objects.get(PIN=pin)
        except:
                print "Employee %s not found"%pin
                return
        emp.DelTag=1
        emp.save()

def readFile(fn):
        f=file(fn, "rb")
        data=f.read()
        if data[:3]=="\xef\xbb\xbf": #UTF-8 tag of a text file
                data=data[3:]
        data=data.decode("utf-8").split('\n')
        f.close()
        return data

def processEmpFile(f, fn):
        print "Process employee file %s"%fn
        data=readFile(fn)
        for line in data:
                if line:
                        try:
                                emp=line.split("\t")
                                if emp[0]=="I":
                                        insertEmp(emp[1], emp[2], emp[3].split('\r')[0])
                                elif emp[0]=="D":
                                        deleteEmp(emp[1])
                                else:
                                        print "Not a valid employee line: %s"%line
                        except Exception, e:
                                print e.message

def readFromFtp(
                ftp_host, 
                ftp_user, 
                ftp_pwd, 
                ftp_path, 
                filePrefix, 
                iwm_e_path, 
                processor=processEmpFile):
        if iwm_e_path[-1] not in ['\\', '/']: 
                iwm_e_path=iwm_e_path+"/"
        try:
                os.makedirs(iwm_e_path)
        except: pass
        try:
                f=FTP(ftp_host)
                f.login(ftp_user,ftp_pwd)
                f.cwd(ftp_path)
        except Exception, e:
                print e.message
                return []
        print "Open FTP %s OK"%ftp_host
        fns=[]
        flist=f.nlst()
        d=datetime.datetime.now()
        minfn=(d-datetime.timedelta(30)).strftime(filePrefix+"%Y%m%d%H%M%S.txt")
        maxfn=(d+datetime.timedelta(0,30)).strftime(filePrefix+"%Y%m%d%H%M%S.txt")
        for fn in flist:
                if fn>minfn and fn<maxfn:
                        try:
                                datetime.datetime.strptime(fn, filePrefix+"%Y%m%d%H%M%S.txt")
                        except: 
                                pass
                        else: #valid filename 
                                if not os.path.exists(iwm_e_path+fn): #检查文件是否处理过
                                        fns.append(fn)
        if fns:
                fns.sort()
                cachedEmployee={}
                for fn in fns:
                        try:
                                print "Read file from ftp: ", fn
                                f.retrbinary("RETR %s"%fn, open(iwm_e_path+fn, 'w+b').write)
                                processor(f, iwm_e_path+fn)        
                        except Exception, e:
                                print e.message
                f.quit()
        return fns

def uploadSAPFile(f, logfn):
        fn=logfn.split(('\\' in logfn) and "\\" or "/")[-1] #得到不带目录的文件名
        fn=fn.split(('\\' in fn) and "\\" or "/")[-1] #得到不带目录的文件名
        print "Upload %s to ftp"%fn
        pwd=f.pwd()
        if pwd<>settings.cfg.FTP.TRANS_PATH:
                #转到考勤记录目录
                f.cwd(settings.cfg.FTP.TRANS_PATH)
        f.storbinary("STOR "+fn, file(logfn, "rb")) #上传文件
        #改为规定的文件名
        d=datetime.datetime.now()
        logfn=d.strftime("sapdata%Y%m%d%H%M%S.txt")
        print "Rename %s to %s in ftp"%(fn, logfn)
        f.rename(fn, logfn)
        if pwd<>settings.cfg.FTP.TRANS_PATH:
                #恢复到原来的目录
                f.cwd(pwd)

def processSchFile(f, fn):
        print "Process schdule file %s"%fn
        from mysite.iclock.transinout import parseTransState
        logfn=fn+'.trans.log'
        #根据上下班时间文件生成 带状态的考勤记录文件                                         
        parseTransState(fn, logfn)
        #上传到ftp服务器上                                                  
        uploadSAPFile(f, logfn)
        #上传完成后删除 考勤记录文件
        os.remove(logfn)
                                                   
#下传员工数据，通常该函数每天调用一次
def checkEmpFile():
        readFromFtp(settings.cfg.FTP.HOST, 
                settings.cfg.FTP.USER, 
                settings.cfg.FTP.PASSWORD, 
                settings.cfg.FTP.EMP_PATH, 
                'employee',
                settings.cfg.FTP.EMP_LOCAL)

#下载排班数据，并据此生成、上传考勤记录，通常该函数每周调用一次
def checkSchFile():
        readFromFtp(settings.cfg.FTP.HOST, 
                settings.cfg.FTP.USER, 
                settings.cfg.FTP.PASSWORD, 
                settings.cfg.FTP.SCH_PATH, 
                'schedule', 
                settings.cfg.FTP.SCH_LOCAL,
                processSchFile
                )

#检查是否存在数据需要上传，通常该函数每小时调用一次
def checkUpload():
        from mysite.cab import listFile
        files=listFile(settings.cfg.FTP.SCH_LOCAL, ['*.trans.log'])
        if files:
                try:
                        ftp=FTP(settings.cfg.FTP.HOST)
                        ftp.login(settings.cfg.FTP.USER, settings.cfg.FTP.PASSWORD)
                        ftp.cwd(settings.cfg.FTP.TRANS_PATH)
                except Exception, e:
                        print e.message
                        return
                for f in files:
                        uploadSAPFile(ftp, f)
                ftp.quit()

#通过Web服务器进行数据同步                                                                 
def WMDataSync(request):
        if request.method=="POST":
                from mysite.tasks import installTasks
                installTasks()
                checkUpload()
                checkSchFile()
                checkEmpFile()
                checkUpload()
                return render_to_response("info.html", {"title":  u"数据同步", 
                        "content": u"完成"
                        })
        else:
                return render_to_response("info.html", {"title":  u"数据同步", 
                        "content": u"""
<form action="" method="POST" >
<input type='submit' value='进行 SAP 数据同步'/>
</form>
"""
                        })

        
