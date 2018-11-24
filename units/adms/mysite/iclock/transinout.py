#coding=utf-8
from mysite.iclock.models import *
import string
import datetime
import time

def readTransFrom(UserID, startTime):
        return Transaction.objects.filter(UserID=UserID, TTime__gte=startTime).order_by('TTime').values('TTime','SN')

        
# 人员排班数据下发        
#------------------------------------------------------------------------------
#工号\t日期\t上班时间\t下班时间
#其中日期格式为YYYYMMDD，上班时间、下班时间格式为24小时制HHNNSS

invalid_pins=[]

def transASch(line):
        s=line.split("\t")
        pin=s[0]
        if pin in invalid_pins: return None
        try:        
                sch={'UserID':Employee.objByPIN(pin, None).id, 'PIN': pin}
        except:
                invalid_pins.append(pin)
                return None
        startDate=s[1]
        sch['Date']=datetime.datetime.strptime(startDate, "%Y%m%d")
        sch['Start']=datetime.datetime.strptime(startDate+s[2],"%Y%m%d%H%M%S")
        endTime=datetime.datetime.strptime(startDate+s[3][:6],"%Y%m%d%H%M%S")
        if sch['Start']==endTime:
                return None
        if endTime<sch['Start']:
                sch['End']=endTime+datetime.timedelta(1)
        else:
                sch['End']=endTime
        return sch

def cmpSch(s1, s2):
        u1=s1["UserID"]
        u2=s2["UserID"]
        if u1<u2: return -1
        if u1>u2: return 1
        t1=s1["Date"]
        t2=s2["Date"]
        if t1<t2: return -1
        if t1>t2: return 1
        t1=s1["Start"]
        t2=s2["Start"]
        if t1<t2: return -1
        if t1>t2: return 1
        return 0
                        
def readSchedule(schFile):
        fileData=file(schFile,'rb').read()
        schs=[]
        for line in fileData.split("\n"):
                try:
                        if line:
                                sch=transASch(line)
                                if sch: schs.append(sch)
                except Exception, e:
                        print "LINE  :", line
                        print "ERROR :", e.message
        schs.sort(cmpSch)
        return schs


# 考勤记录上传: Sap对考勤系统数据格式的要求
#------------------------------------------------------------------------------        
#（上班数据）P10000320080808080000200808080800000006900710000010
#（下班数据）P20000320080808080000200808080800000006900710000010
#SATZA                           CHAR3        上下班表示 P10/P20
#TERID                           CHAR4        刷卡机编号（终端标识） 0003
#LDATE                           CHAR8        日期年月日 20080808
#LTIME                           CHAR6        日期时分秒 080000
#ERDAT                           CHAR8        日期年月日 20080808（重复一次刷卡日期）
#ERTIM                           CHAR6        日期时分秒 080000（重复一次刷卡分秒）
#ZAUSW                           CHAR8        卡号 00069007
#PERNR                           CHAR8        职工编号 10000010 （该字段非必需）
#
CHECK_IN=True
CHECK_OUT=False


def writeATran(f, pin, ttime, devSN, stateIn=CHECK_IN):
        st=ttime.strftime("%Y%m%d%H%M%S")
        ssn=("0000"+(devSN or ""))[-4:]
        s="%s%s%s%s%s10000010\r\n"%(
                stateIn and "P10" or "P20",
                ssn,st,st,pin
                )
        f.write(s)

def writeATranInOut(f, sch, pin):
        if 'Saved' in sch: return
        if 'In' in sch:
                writeATran(f, pin, sch['In']['TTime'], sch['In']['SN'], CHECK_IN)
        if 'Out' in sch:
                writeATran(f, pin, sch['Out']['TTime'], sch['Out']['SN'], CHECK_OUT)
        sch['Saved']=True

def outALine(s):
        return
        print s

#将上班前4个小时到第二天上班前4个小时作为一个时间段统一考虑，例如每天上班08:30—17:30，那将落在4:30—第二天4:30（转天上班前的4个小时）这个时间段内的刷卡资料来进行判断，并且结合上下班时间进行判断：如果有多条记录，且刷卡数据的时间间隔超过一个小时，在这个时间段内的第一条数据默认为“上班签到”，最后一条默认为“下班签退”； 如果员工在这个时间段内只有一条刷卡记录,如果在上班前4个小时到上班后3小时之间,则为“上班签到”,如果在上班3小时后到第二天上班前4个小时之间,则为“下班签退”.
#                                         
# p0----in---p3-----------out------------p1
def adjustState(t, sch, p0, p1, p2, log):
        if 'In' not in sch:
                if 'Out' not in sch:
                        if t<p2:
                                sch['In']=log
                                outALine( "In : %s"%log['TTime'])
                        else:
                                sch['Out']=log
                                outALine( "Out: %s"%log['TTime'])
                        return
                #已经有了一个签退记录
                t2=sch['Out']['TTime']
                if (t-t2).seconds>=1*60*60: #超过1小时
                        sch['In']=sch['Out']
                        sch['Out']=log
                        outALine("In-: %s"%sch['In']['TTime'])
                        outALine("Out: %s"%log['TTime'])
                        return
                #没有超过1小时, 用新记录替代旧记录
                sch['Out']=log
                outALine("Out: %s"%log['TTime'])
                return
        #已经有了签到记录
#if t<sch['Start']:        #上班前
#                sch['In']=log
#                return
                
        t2=sch['In']['TTime']
        if (t-t2).seconds>=1*60*60: #超过1小时
                sch['Out']=log
                outALine("Out: %s"%log['TTime'])
                return
        outALine( "!!!: %s"%log['TTime'])
        

def writeTransState(f, logs, schs, lastEmp):
#        print "\n\nwriteTransState", lastEmp
        if not logs: return
        if not schs: return
        
        pin=schs[0]["PIN"]

        schi=0
        schl=len(schs)
        sch=schs[schi]
        sp0=sch['Start']-datetime.timedelta(0, 4*60*60)
        sp1=sp0+datetime.timedelta(1)
        sp2=sch['Start']+datetime.timedelta(0, 3*60*60)
#        print "SCH: %s - %s"%(sch['Start'], sch['End'])
        for log in logs:
                t=log['TTime']
#                print "LOG: %s"%t
                if t<sp0:
#                        print "SKIP LOG"
                        pass
                else:
                        if t>=sp1: # out the range
                                writeATranInOut(f, sch, pin)
                                #查找下一个包含t的时间段
                                schi+=1
                                while schi<schl:
                                        sch=schs[schi]
#                                        print "SCH: %s - %s"%(sch['Start'], sch['End'])
                                        sp0=sch['Start']-datetime.timedelta(0, 4*60*60)
                                        sp1=sp0+datetime.timedelta(1)
                                        sp2=sch['Start']+datetime.timedelta(0, 3*60*60)
                                        if t<sp1: break #找到一时间段包含t
                                        schi+=1
#                                        print "SKIP this SCH"
                                if t>=sp1: #已经超过了所有的时间段
#                                        print "Out of Schedule range"
                                        break
                        adjustState(t, sch, sp0, sp1, sp2, log)
        writeATranInOut(f, sch, pin)        
                                
def outLogs(logs):
        return
        for l in logs:
                print "%s"%l['TTime']

def parseTransState(schFile, fileName="l.txt"):
        schs=readSchedule(schFile)
        #schs 是按照人、日期、时间排序的，从而保证了同一个人的时间段在一起
        if not schs: return
        f=file(fileName,"w+b")
        lastEmp=""
        logs=[]
        lastSchs=[]
        for sch in schs:
                emp=sch['UserID']
                if emp<>lastEmp:
                        if lastEmp<>"":
                                writeTransState(f, logs, lastSchs, lastEmp)
                        logs=readTransFrom(emp, sch['Date']-datetime.timedelta(1))
                        outLogs(logs)
                        lastEmp=emp
                        lastSchs=[]
                lastSchs.append(sch)
        if lastSchs:
                writeTransState(f, logs, lastSchs, lastEmp)
        f.close()

                         
