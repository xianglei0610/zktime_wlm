#! /usr/bin/env python
#coding=utf-8

from django.utils.translation import ugettext_lazy as _
#from mysite.meeting.models.room import Room
from mysite.meeting.models.room import Room
from mysite.meeting.models.meeting_record import OriginalRecord
from mysite.iclock.models.model_trans import Transaction
from mysite.meeting.models.meeting_emp import MeetingEmp
from report import getValidRecord
from mysite.personnel.models.model_emp import Employee
from mysite.meeting.models.detailMeeting import DetailMeeting
from mysite.meeting.models.meeting_leave import Leave
from mysite.meeting.models.statisticsMeeting import StatisticsMeeting
from mysite.meeting.models.model_meeting import MeetingEntity
from mysite.meeting.models.meeting_ValidRecord import ValidRecord
import datetime


def detailMeetingEmp(meetingIDs):
    if meetingIDs != None or len(meetingIDS)>0:
        for meetingId in meetingIDs:
            records = ValidRecord.objects.filter(meetingID__id = meetingId)
            #print 'detailMeetingEmp == ',records

def getPrimitiveMeetingData(meetingIds):
    try:
        #print '==ok==========1'

        roomIDs = []
        emps = []
        #得到会议
        meetings = []
        if type(meetingIds).__name__ == "NoneType":
            meetingsAll = MeetingEntity.objects.all()
            for m in meetingsAll:
                emps = MeetingEmp.objects.filter(meetingID=m)
                if len(emps)>0:
                    meetings.append(m)
        elif type(meetingIds).__name__ == "list":
            meetings.extend(meetingIds)
        elif type(meetingIds).__name__ == "MeetingEntity":
            meetings.append(meetingIds)
        else:
            raise Exception(_(u"对象有误"))



        #print '==ok==========1'
        #根据会议取原始记录
        if len(meetings)>0:
            for m in meetings:#2012.7.30修改，把下面的都放到循环里面了
                #取得该会议处在会议室的所有考勤机器
                room = m.roomMeeting
                meetingDevices = room.devices.all()#2012.7.30修改
                for r in meetingDevices:#2012.7.30修改
                    devices = r#2012.7.30修改
                    #print devices
                #devices = room.devices

                #print '...getPrimitiveMeetingData...devices:%s' %devices
    #            OriginalByDevices = Transaction.objects.filter(SN = devices)

                    #得到考勤时间区间 2012.7.30修改
                    startTime = datetime.datetime(m.startTime.year,m.startTime.month,m.startTime.day,m.startCheckInTime.hour,m.startCheckInTime.minute,m.startCheckInTime.second)
                    endTime = datetime.datetime(m.endTime.year,m.endTime.month,m.endTime.day,m.endCheckOutTime.hour,m.endCheckOutTime.minute,m.endCheckOutTime.second)
        #            OriginalByDevicesTime = Transaction.objects.filter(SN=devices,TTime__gt=startTime)
        #            print 'startTime::',startTime,'endTime::',endTime
                    OriginalByDevicesTime = Transaction.objects.filter(TTime__range=(startTime,endTime),sn_name=devices.sn)
                    #print '---OriginalByDevicesTime:',len(OriginalByDevicesTime),devices.sn,startTime,endTime,OriginalByDevicesTime
        #            OriginalByDevicesTime = Transaction.objects.filter(TTime__range=(startTime,endTime),SN=devices.id)
        #            OriginalByDevicesTime1= Transaction.objects.filter(TTime__range=(startTime,endTime))
        #            OriginalByDevicesTime2=Transaction.objects.filter(SN=devices.id)
        #            print '---OriginalByDevicesTime:',len(OriginalByDevicesTime),devices.id
        #            print '---OriginalByDevicesTime:',len(OriginalByDevicesTime1),devices.id
        #            print '---OriginalByDevicesTime:',len(OriginalByDevicesTime2),devices.id
                    #print "-----------------------------------------------------------------"
                    orRe = OriginalRecord.objects.filter(meetingID = m)
                    if len(OriginalByDevicesTime) < 1 and len(orRe) < 1:
                        raise Exception(_(u'没有原始记录，请先上传数据'))
                    #取得参与会议的人员EmpForeignKey类型
                    emps = list(e.user for e in MeetingEmp.objects.filter(meetingID=m))
                    #根据会议人员取原始记录
                    if len(emps) > 0:
                        for emp in emps:
                            originals = OriginalByDevicesTime.filter(UserID__PIN=emp.PIN)
                            if len(originals) > 0:
                                for original in originals:
                                    originalRecord = OriginalRecord()
        #                            empMeeting = MeetingEmp.objects.get(meetingID=m,user=original.UserID)
                                    originalRecord.user = original.UserID
                                    originalRecord.meetingID = m
                                    originalRecord.checkTime = original.TTime
                                    #print original.State
                                    if original.State in ['I','1']:#2012.7.30修改
                                        originalRecord.checkType = 1
                                    else:
                                        originalRecord.checkType = 2

                                    originalRecord.verifyCode = original.Verify
                                    originalRecord.sensorid = original.sensorid
                                    originalRecord.workCode = original.WorkCode
                                    originalRecord.nameSN = original.sn_name
                                    originalRecord.sn = original.SN
                                    originalRecord.reserved = original.Reserved
                                    try:
                                        originalEEE = OriginalRecord.objects.get(user=original.UserID,nameSN=original.sn_name,checkTime=original.TTime)
                                    except:#如果有该条记录就不保存

                                        originalRecord.save()
                    else:
                        raise Exception(_(u'会议尚未添加人员，无记录可获取'))


            for m in meetings:#update DetailMeeting
                validDataEmp = getValidRecord(m)
                emps = MeetingEmp.objects.filter(meetingID=m)
                startT = m.startTime + datetime.timedelta(minutes = m.lateAllow)#迟到时间
                endT = m.endTime - datetime.timedelta(minutes = m.leaveAllow)#早退时间
                for emp in emps:
                    try:
                        detail = DetailMeeting.objects.get(user=emp.user,meetingID=emp.meetingID)
                    except:
                        raise Exception(_(u"会议人员信息异常，请删除后重新添加会议人员"))
                    inRecord = validDataEmp[str(m.pk)+'_'+str(emp.pk)][0]
                    outRecord = validDataEmp[str(m.pk)+'_'+str(emp.pk)][1]
                    if inRecord != outRecord and inRecord != 0 and outRecord != 0:
                        #正常(有签到签退记录)
                        originalInRecord = OriginalRecord.objects.get(pk=inRecord)
                        originalOutRecord = OriginalRecord.objects.get(pk=outRecord)
                        detail.checkInTime = originalInRecord.checkTime
                        detail.checkOutTime = originalOutRecord.checkTime
                        #判断迟到
                        diffLeate = (detail.checkInTime - startT)
                        detail.checkType = 1
                        detail.lateTime = 0

                        if diffLeate.days == 0 and diffLeate.seconds > 0:#迟到
                            detail.lateTime = diffLeate.seconds/60
                            detail.checkType = 6
                        elif diffLeate.days < 0:
                            detail.lateTime = 0
                            detail.checkType = 1

                        #判断是否早退
                        diffEarly = (endT - detail.checkOutTime)#早退
                        lt = diffEarly.seconds/60
                        if lt >= 1 and lt/60 < 12:
                            detail.leaveEarlyTime = lt
                            detail.checkType = 11
                            if detail.lateTime >=1:
                                detail.checkType = 8
                        elif lt/60 > 12 or 0 <= lt < 1:
                            detail.leaveEarlyTime = 0
                            detail.checkType = 1
                            if detail.lateTime >= 1:
                                detail.checkType = 6

                        detail.nameSN = originalOutRecord.nameSN
                    elif inRecord == outRecord and inRecord != 0:
                        #只有一次异常记录

                        originalInRecord = OriginalRecord.objects.get(pk=inRecord)

                        stT = abs(originalInRecord.checkTime - startT).seconds/60
                        enT = abs(originalInRecord.checkTime - endT).seconds/60
                        #print '==????==',stT,enT
                        if  stT < enT:#表示签到
                            detail.checkOutTime = None
                            detail.checkInTime = originalInRecord.checkTime
                            diffLeate = (detail.checkInTime - startT)
                            detail.checkType = 1
                            detail.lateTime = 0

                            if diffLeate.days == 0 and diffLeate.seconds > 0:#迟到
                                detail.lateTime = diffLeate.seconds/60
                                detail.checkType = 9
                            elif diffLeate.days < 0:
                                detail.lateTime = 0
                                detail.checkType = 5
                            detail.leaveEarlyTime = None#abs(diffEarly/60)
                        else: #表示签退

                            originalOutRecord = OriginalRecord.objects.get(pk=inRecord)
                            detail.checkOutTime = originalOutRecord.checkTime
                            detail.checkInTime = None
                            diffEarly = (endT - detail.checkOutTime)#早退
                            lt = diffEarly.seconds/60
                            if lt >= 1 and lt/60 < 12:
                                detail.leaveEarlyTime = lt
                                detail.checkType = 12
                            elif lt/60 > 12 or 0 <= lt < 1:
                                detail.leaveEarlyTime = 0
                                detail.checkType = 4
                            detail.lateTime = None#diffLeate/60

                        detail.nameSN = originalInRecord.nameSN

                    elif inRecord != outRecord and inRecord != 0 and outRecord == 0:
                        #签到未签退
                        originalInRecord = OriginalRecord.objects.get(pk=inRecord)
                        detail.checkOutTime = None
                        detail.checkInTime = originalInRecord.checkTime
                        detail.checkType = 5
                        diffLeate = (detail.checkInTime - startT)
                        if diffLeate.days >= 0 and diffLeate.seconds > 0:#迟到
                            detail.lateTime = diffLeate.seconds/60
                            detail.checkType = 10
                        else:
                            detail.lateTime = 0
                            detail.checkType = 5
    #                    diffEarly = (m.endTime - detail.checkInTime).seconds
                        detail.leaveEarlyTime = None#abs(diffEarly/60)
                        detail.nameSN = originalInRecord.nameSN

                    elif inRecord != outRecord and outRecord != 0 and inRecord == 0:
                        #签退未签到
                        originalOutRecord = OriginalRecord.objects.get(pk=outRecord)
                        detail.checkOutTime = originalOutRecord.checkTime
                        detail.checkInTime = None
                        detail.checkType = 4
                        diffEarly = (endT - detail.checkOutTime)#早退
                        lt = diffEarly.seconds/60
                        if lt >= 1 and lt/60 < 12:
                            detail.leaveEarlyTime = lt
                            detail.checkType = 12
                        elif lt/60 > 12 or 0 <= lt < 1:
                            detail.leaveEarlyTime = 0
    #                    diffLeate = (detail.checkOutTime - m.startTime).seconds
                        detail.lateTime = None#diffLeate/60
                        detail.nameSN = originalOutRecord.nameSN

                    else:
                        detail.checkInTime = None
                        detail.checkOutTime = None
                        detail.lateTime = None
                        detail.leaveEarlyTime = None
                        detail.checkType = 2
                    leaveEmp = Leave.objects.filter(employee=emp.user,meetingID=m)
                    if len(leaveEmp)>0:
                        detail.checkType = 3
                    #print 'change:%s' %detail.change_operator
                    detail.save()
                meetingStatistics(m)
    except :#2012.7.30修改
        import traceback;traceback.print_exc();

                
def meetingStatistics(meetingId):
    '''
        会议统计汇总计算
    '''
    meetingIds = []
    meetingIds.append(meetingId)
    for m in meetingIds:
        try:
            sm = StatisticsMeeting.objects.get(meetingID=m)
        except:
            raise Exception(_(u"会议没有正常保存，请删除后重新添加该会议"))
        meetingEmps = MeetingEmp.objects.filter(meetingID=m)
        dm = DetailMeeting.objects.filter(meetingID=m)
        sm.dueMeetingEmpCount = len(meetingEmps)   
        sm.arrivalMeetingEmpCount = len(dm.filter(checkType__in = [1,4,5,6,7,8,9,10,11,12,13]))
        sm.nonArrivalMeetingEmpCount = len(dm.filter(checkType__in = [2,3]))
        sm.vacateMeetingEmpCount = len(dm.filter(checkType__in = [3]))
        sm.absentMeetingEmpCount = len(dm.filter(checkType__in = [2]))
        sm.lateEmpCount = len(dm.filter(checkType__in = [6,8,9,10]))
        sm.leaveEarlyEmpCount = len(dm.filter(checkType__in = [7,8,11,12,13]))
        sm.unCheckInCount = len(dm.filter(checkType__in = [4,9,12]))
        sm.unCheckOutCount = len(dm.filter(checkType__in = [5,10,13]))
        sm.save()

#ATTSTATES=(
#    (1,_(u"正常")),
#    (2,_(u"缺席")),
#    (3,_(u"请假")),
#    (4,_(u"签退未签到")),
#    (5,_(u"签到未签退")),
#    (6,_(u"迟到")),
#    (7,_(u"早退")),
#    (8,_(u"迟到、早退")),
#    (9,_(u"迟到、未签到")),
#    (10,_(u"迟到、未签退")),
#    (11,_(u"早退")),
#    (12,_(u"早退、未签到")),
#    (13,_(u"早退、未签退")),
#
#)


