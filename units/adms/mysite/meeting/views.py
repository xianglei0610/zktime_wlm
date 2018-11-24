# Create your views here.
#coding=utf-8

from mysite.meeting.report import reportindex,getOriginalData,getValidRecords
from django.utils.simplejson  import dumps 
from django.utils.encoding import smart_str
from dbapp.utils import getJSResponse
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _
import sys
from django.utils.encoding import smart_str
from django.utils import simplejson
from mysite.settings import MEDIA_ROOT
from mysite.meeting.models import OriginalRecord
from mysite.meeting.models.meeting_ValidRecord import ValidRecord
from mysite.meeting.models.statisticsMeeting import StatisticsMeeting
from mysite.meeting.models.detailMeeting import DetailMeeting
from mysite.meeting.models.meeting_emp import MeetingEmp
from mysite.personnel.models.model_emp import Employee
from mysite.meeting.models.model_meeting import MeetingEntity
from mysite.meeting.models.meeting_leave import Leave
#from mysite.meeting.models.room import Room
from mysite.meeting.models.room import Room
from mysite.meeting.models.meeting_exact import MeetingExact
from mysite.iclock.models.model_trans import Transaction
from mysite.meeting.report import parse_meetingreport_arg
import datetime
from mysite.meeting.models.meeting_empwidget import ZMulEmpChoiceWidget
type1 = sys.getfilesystemencoding()

def funMeetingCalculate(request):
    return reportindex(request)


def funGetRecord(request):
    return getOriginalData(request)

def funValidRecords(request):
    return getValidRecords(request)

def getAndSaveMeetingOriginalRecord(meetingids):

        """
            获取会议原始记录
        """
        try:
            if meetingids != None and meetingids != '' and len(meetingids)>0:
                for id in meetingids:
                    meetingE = MeetingEntity.objects.get(id = id)
                    mRoom = meetingE.roomMeeting
                    room = Room.objects.filter(numberRoom = mRoom.numberRoom)
                    meetingEmp = MeetingEmp.objects.filter(meetingID = meetingE)
                    for emp in meetingEmp:
                        for r in room:#2012.7.30修改
                            meetingDevices = r.devices.all()#2012.7.30修改
                            for m in meetingDevices:#2012.7.30修改
                                sn = m.sn  #设备序列号
                                SN = m.pk
                                startT = meetingE.startCheckInTime #2012.4.19修改
                                endT = meetingE.endCheckOutTime          #2012.4.19修改
                                #取得会议签到考勤时间 2012.7.30修改
                                startInTime = datetime.datetime(meetingE.startTime.year,meetingE.startTime.month,meetingE.startTime.day,meetingE.startCheckInTime.hour,meetingE.startCheckInTime.minute,meetingE.startCheckInTime.second)#meetingE.startCheckInTime
                                endInTime = datetime.datetime(meetingE.startTime.year,meetingE.startTime.month,meetingE.startTime.day,meetingE.endCheckInTime.hour,meetingE.endCheckInTime.minute,meetingE.endCheckInTime.second)#meetingE.endCheckInTime
                                #取得会议签退考勤时间 2012.7.30修改
                                startOutTime = datetime.datetime(meetingE.endTime.year,meetingE.endTime.month,meetingE.endTime.day,meetingE.startCheckOutTime.hour,meetingE.startCheckOutTime.minute,meetingE.startCheckOutTime.second)#meetingE.startCheckOutTime
                                endOutTime = datetime.datetime(meetingE.endTime.year,meetingE.endTime.month,meetingE.endTime.day,meetingE.endCheckOutTime.hour,meetingE.endCheckOutTime.minute,meetingE.endCheckOutTime.second)#meetingE.endCheckOutTime
        #                        startTime = datetime.datetime(m.startTime.year,m.startTime.month,m.startTime.day,m.startCheckInTime.hour,m.startCheckInTime.minute,m.startCheckInTime.second)
        #                        endTime = datetime.datetime(m.endTime.year,m.endTime.month,m.endTime.day,m.endCheckOutTime.hour,m.endCheckOutTime.minute,m.endCheckOutTime.second)
                                transIn = Transaction.objects.filter(TTime__range=(startInTime,endInTime),sn_name=sn,UserID=emp.user)#从考勤原始记录表中获取会议数据
                                transIn1 = Transaction.objects.filter(TTime__range=(startInTime,endInTime),SN = SN,UserID=emp.user)
                                transOut = Transaction.objects.filter(TTime__range=(startOutTime,endOutTime),sn_name=sn,UserID=emp.user)
                                transOut2 = Transaction.objects.filter(TTime__range=(startOutTime,endOutTime),SN = SN,UserID=emp.user)
#                                print transIn,'1111111111',startInTime,endInTime
#                                print transOut,'22222222222'
                                for record in transIn:
                                    originalRecord = OriginalRecord()
                                    #print originalRecord
                                    ord = OriginalRecord.objects.filter(user=record.UserID,checkTime=record.TTime)
                                    if len(ord)>0:
                                            pass
                                    else:
                                        originalRecord.user = record.UserID
                                        originalRecord.meetingID = meetingE
                                        originalRecord.checkTime = record.TTime
                                        originalRecord.checkType = 'I'
                                        originalRecord.verifyCode = record.Verify
                                        originalRecord.sn = record.SN
                                        originalRecord.sensorid = record.sensorid
                                        originalRecord.workCode = record.WorkCode
                                        originalRecord.nameSN = record.sn_name
                                        originalRecord.save()
                                for out_record in transOut:
                                    originalRecord = OriginalRecord()
                                    ord = OriginalRecord.objects.filter(user=out_record.UserID,checkTime=out_record.TTime)
                                    if len(ord)>0:
                                        pass
                                    else:
                                       originalRecord.user = out_record.UserID
                                       originalRecord.meetingID = meetingE
                                       originalRecord.checkTime = out_record.TTime
                                       originalRecord.checkType = 'O'
                                       originalRecord.verifyCode = out_record.Verify
                                       originalRecord.sn = out_record.SN
                                       originalRecord.sensorid = out_record.sensorid
                                       originalRecord.workCode = out_record.WorkCode
                                       originalRecord.nameSN = out_record.sn_name
                                       originalRecord.save()
                                for record in transIn1:
                                    originalRecord = OriginalRecord()
                                    ord = OriginalRecord.objects.filter(user=record.UserID,checkTime=record.TTime)
                                    if len(ord)>0:
                                        pass
                                    else:
                                        originalRecord.user = record.UserID
                                        originalRecord.meetingID = meetingE
                                        originalRecord.checkTime = record.TTime
                                        originalRecord.checkType = 'I'
                                        originalRecord.verifyCode = record.Verify
                                        originalRecord.sn = record.SN
                                        originalRecord.sensorid = record.sensorid
                                        originalRecord.workCode = record.WorkCode
                                        originalRecord.nameSN = record.sn_name
                                        originalRecord.save()
                                for out_record in transOut2:
                                    originalRecord = OriginalRecord()
                                    ord = OriginalRecord.objects.filter(user=out_record.UserID,checkTime=out_record.TTime)
                                    if len(ord)>0:
                                        pass
                                    else:
                                        originalRecord.user = out_record.UserID
                                        originalRecord.meetingID = meetingE
                                        originalRecord.checkTime = out_record.TTime
                                        originalRecord.checkType = 'O'
                                        originalRecord.verifyCode = out_record.Verify
                                        originalRecord.sn = out_record.SN
                                        originalRecord.sensorid = out_record.sensorid
                                        originalRecord.workCode = out_record.WorkCode
                                        originalRecord.nameSN = out_record.sn_name
                                        originalRecord.save()
        except :#2012.7.30修改
            import traceback;traceback.print_exc();
                        
def saveMeetingValidRecord(record):
    if record != None or record != '':

        valid = ValidRecord()
        valid.user = record.user
        valid.meetingID = record.meetingID
        valid.checkTime = record.checkTime
        
        #ValidRecord中的checkType为IntegerField，而record中的checkType为char
        if record.checkType in ['I','1']:#2012.7.30修改
            valid.checkType = 1
        else:
            valid.checkType = 2
        valid.verifyType = record.verifyCode
        valid.save()

        
def getMeetingValidRecord(meetingids):
    """
        选取会议有效记录
    """
    if meetingids != None and meetingids != '' and len(meetingids)>0:
        for id in meetingids:
            meetingE = MeetingEntity.objects.get(id = id)  
            start_in_time = meetingE.startCheckInTime #2012.4.19修改
            end_in_time = meetingE.endCheckInTime  #2012.4.19修改
            start_out_time = meetingE.startCheckOutTime
            end_out_time = meetingE.endCheckOutTime   
#            startT = meetingE.startTime-datetime.timedelta(seconds = meetingE.startCheckTime*60)
#            startT2 = meetingE.startTime+datetime.timedelta(seconds = meetingE.lateAllow*60)
#            endT1 = meetingE.endTime-datetime.timedelta(seconds = meetingE.leaveAllow*60)
#            endT = meetingE.endTime+datetime.timedelta(seconds = meetingE.endCheckTime*60)
            meetingEmp = MeetingEmp.objects.filter(meetingID = meetingE)
            for emp in meetingEmp:
                inRecords = OriginalRecord.objects.filter(meetingID = meetingE,user = emp.user,checkTime__range=(start_in_time,end_in_time)).order_by('checkTime')#签到记录
                #inRecords1 = MeetingExact.objects.filter(meetingID = meetingE,user = emp.user,checkTime__range=(start_in_time,end_in_time)).order_by('checkTime')
                outRecords = OriginalRecord.objects.filter(meetingID = meetingE,user = emp.user,checkTime__range=(start_out_time,end_out_time)).order_by('-checkTime')#签退记录
                #outRecords1 = MeetingExact.objects.filter(meetingID = meetingE,user = emp.user,checkTime__range=(start_out_time,end_out_time)).order_by('-checkTime')
#                try:#2012.7.30修改
#                    print inRecords,outRecords,emp.user,start_in_time,end_in_time,type(start_in_time)
#                except :#2012.7.30修改
#                    import traceback;traceback.print_exc();

                oldinRecords = ValidRecord.objects.filter(meetingID=meetingE,user = emp.user,checkTime__range=(start_in_time,end_in_time))
                oldoutRecords = ValidRecord.objects.filter(meetingID=meetingE,user = emp.user,checkTime__range=(start_out_time,end_out_time)) 
                if len(inRecords) >0: #有签到
                    if len(oldinRecords)>0:
                        oldinRecords.delete() #删除旧记录
                    saveMeetingValidRecord(inRecords[0])#保存新记录
                    if len(outRecords)>0:  #有签到有签退
                        
                        if len(oldoutRecords)>0:
                            oldoutRecords.delete()
                        saveMeetingValidRecord(outRecords[0])
                    else:#有签到没签退，则删除原来的签退记录
                        if len(oldoutRecords)>0:
                            oldoutRecords.delete()
                    #有签到没签退记录            
                else: #没有签到记录
                    if len(oldinRecords)>0:
                        oldinRecords.delete() #删除旧记录
                    if len(outRecords)>0:  #无签到有签退
                        if len(oldoutRecords)>0:
                            oldoutRecords.delete()
                        saveMeetingValidRecord(outRecords[0])
                    else:#没签到没签退，则删除原来的签退签到记录
                        if len(oldoutRecords)>0:
                            oldoutRecords.delete()
                        if len(oldinRecords)>0:
                            oldinRecords.delete()
                 
def funValidRecord(request):
    mids = []
    userIDs = request.POST.get('UserIDs',None)
    meetingIDs = request.REQUEST.get("meetingIDS",None)
    mids = meetingIDs.split(',')
    getAndSaveMeetingOriginalRecord(mids)
    getMeetingValidRecord(mids)
    return getJSResponse(None)

def detailMeetingEmp(meetingIds):

    '''
        会议统计详情
    '''

    if len(meetingIds)>0:
        for meetingId in meetingIds:
            meetingEntity = MeetingEntity.objects.get(id = meetingId)
            meetingEmps = DetailMeeting.objects.filter(meetingID__id = meetingId)
            for emp in meetingEmps:
                records = ValidRecord.objects.filter(meetingID__id = meetingId,user = emp.user).order_by('checkTime')
                validcheckInTime = meetingEntity.startTime + datetime.timedelta(minutes=(meetingEntity.lateAllow)) #此时间前签到不算迟到(会议结束签到时间之前)
                validcheckOutTime = meetingEntity.endTime - datetime.timedelta(minutes=(meetingEntity.leaveAllow)) #此时间后签退不算早退
                emp.checkInTime = None
                emp.checkOutTime = None
                if len(records) == 2:  #
                    emp.checkInTime = records[0].checkTime
                    emp.checkOutTime = records[1].checkTime
                    if emp.checkInTime > validcheckInTime:
                        emp.lateTime = (emp.checkInTime - validcheckInTime).seconds/60 #迟到时间等于签到时间-签到非迟到时间  单位分钟
                        if emp.checkOutTime < validcheckOutTime:
                            emp.leaveEarlyTime = (validcheckOutTime - emp.checkOutTime).seconds/60
                            emp.checkType = 8 #迟到早退
                        else:
                            emp.leaveEarlyTime = 0
                            emp.checkType = 6 #迟到
                    elif emp.checkOutTime < validcheckOutTime:
                        emp.leaveEarlyTime = (validcheckOutTime - emp.checkOutTime).seconds/60
                        emp.lateTime = 0
                        emp.checkType = 7 #早退
                    else:
                        emp.lateTime = 0
                        emp.leaveEarlyTime = 0
                        emp.checkType = 1 #正常
                elif len(records) == 1:
                    if records[0].checkTime <= meetingEntity.endCheckInTime:  
                        emp.checkInTime = records[0].checkTime   #签到
                        if records[0].checkTime > validcheckInTime:
                            emp.lateTime = (emp.checkInTime - validcheckInTime).seconds/60 #迟到时间等于签到时间-签到非迟到时间  单位分钟
                            emp.checkType = 10 #迟到未签退
                        else:
                            emp.checkType = 5 #签到未签退
                            emp.lateTime = 0
                    else:
                        emp.checkOutTime = records[0].checkTime #签退
                        if records[0].checkTime < validcheckOutTime:
                            emp.leaveEarlyTime = (validcheckOutTime - emp.checkOutTime).seconds/60
                            emp.checkType = 12
                        else:
                            emp.checkType = 4
                            emp.leaveEarlyTime = 0
                #考虑请假人员是没有考勤记录的
                #考虑 考勤了在考勤明细表中不存在的记录
                                
                else :
                    leeveMeetingEmp = Leave.objects.filter(employee = emp.user,meetingID__id = meetingId)
                    if len(leeveMeetingEmp)>0:
                        emp.checkType = 3
                    else:
                        emp.checkType = 2
                          
                emp.save()

def funStatisticsMeetingRecord(request):
    '''
        会议统计与汇总
    '''
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
    mids = []
    meetingIDs = request.REQUEST.get("meetingIDS",None)
    mids = meetingIDs.split(',')
    detailMeetingEmp(mids)
    for m in mids:
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
    return getJSResponse(None)

def select_meeting_data(request):
    from mysite.meeting.models.model_meeting import MeetingEntity
    from mysite.meeting.models.room import Room
#    from mysite.iclock.models.room import Room
    from dbapp.dataviewdb import model_data_list
    import json
    all_meeting = request.REQUEST.get("all_meeting",None)       
    if all_meeting == "all":
        qs = MeetingEntity.all_objects.all()
    else:
        qs = MeetingEntity.objects.all()
    return model_data_list(request, MeetingEntity, qs)

def select_meeting(request):
    from mysite.meeting.models.model_meeting import MeetingEntity
    meetingAll = MeetingEntity.objects.all()
    meetingDict = {}
    for i in meetingAll:
        meetingDict[i.pk] = None

    for m in meetingAll:
        s = u'%s'%m.nameMeeting
        meetingDict[m.pk] = s 

    
    return getJSResponse(smart_str(simplejson.dumps(meetingDict)))
def select_checkType(request):
    ATTSTATES=(
    (1,_(u"正常")),
    (2,_(u"缺席")),
    (3,_(u"请假")),
    (4,_(u"签退未签到")),
    (5,_(u"签到未签退")),
    (6,_(u"迟到")),
    (7,_(u"早退")),
    (8,_(u"迟到、早退")),
#    (9,_(u"迟到、未签到")),
    (10,_(u"迟到、未签退")),
#    (11,_(u"早退")),
    (12,_(u"早退、未签到")),
#    (13,_(u"早退、未签退")),

    )
    from mysite.meeting.models.detailMeeting import DetailMeeting
    checkType = DetailMeeting.objects.all()
#    checkType = ATTSTATES
    checkTypeDict = {}
#    for i in ATTSTATES:
#        checkTypeDict[i.pk] = None

    for m in ATTSTATES:
        s = u'%s'%m[1]
        checkTypeDict[m[0]] = s
    return getJSResponse(smart_str(simplejson.dumps(checkTypeDict)))    
    
def statiMeetingRec(request):
    from mysite.meeting.statistics import getPrimitiveMeetingData
    from mysite.meeting.models.model_meeting import MeetingEntity
    from mysite.meeting.models.meeting_emp import MeetingEmp
    meetingAll = request.REQUEST.get("meetingIDS")
    meetingId = []
    li_meeting = list(meetingAll)
    if len(li_meeting)>0:
        for i in li_meeting:
            try:
                meetingId.append(int(i))
            except:
                pass
    else:
        meetingId = None
    meetingIds = list(MeetingEntity.objects.filter(pk__in = meetingId))
    meetings = []
    for m in meetingIds:
        emps = MeetingEmp.objects.filter(meetingID=m)
        if len(emps)>0:
            meetings.append(m)
    
    getPrimitiveMeetingData(list(meetings))
    return getJSResponse(None)

def funMeetingGuide(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    request.dbapp_url =dbapp_url
    apps=get_all_app_and_models()
    return render_to_response('meeting_guide.html',
            RequestContext(request,{
                    'dbapp_url': dbapp_url,
                    'MEDIA_URL':MEDIA_ROOT,
                    "current_app":'meeting', 
                    'apps':apps,
                    "help_model_name":"MeetingGuide",
                    "myapp": [a for a in apps if a[0]=="meeting"][0][1],
                    'app_label':'att',
                    'model_name':'MeetingGuide',
                    'menu_focus':'MeetingGuide',
                    'position':_(u'会议->导航'),
                    })
            
            )
    