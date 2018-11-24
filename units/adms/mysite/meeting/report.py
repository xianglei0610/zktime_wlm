#! /usr/bin/env python
#coding=utf-8
#from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.contrib.auth.decorators import permission_required, login_required
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.shortcuts import render_to_response
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps
from mysite.settings import MEDIA_ROOT
from django.utils.translation import ugettext as _
from django.db.models import Q
from mysite.personnel.models.model_emp import Employee
#会议考勤计算  
@login_required
def reportindex(request):
    from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
    from mysite.urls import surl
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    from mysite.utils import GetFormField
    empfield = EmpPoPMultForeignKey(verbose_name=_(u'人员'),blank=True)
    m_emp = GetFormField("emp",empfield)
    request.dbapp_url=dbapp_url
    apps=get_all_app_and_models()
    return render_to_response('meetingReport.html',
        RequestContext(request, {
            'surl': surl,
            'from': 1,
            'page': 1,
            'limit': 10,
            'item_count': 4,
            'page_count': 1,
            'dbapp_url': dbapp_url,
            'MEDIA_URL':MEDIA_ROOT,
            "current_app":'meeting', 
            'position':_(u'会议->会议签到与报表'),
            'apps':apps,
            "help_model_name":"MeetingCalculate",
            "myapp": [a for a in apps if a[0]=="meeting"][0][1],
            'menu_focus':'MeetingCalculate',
            'perm_export':True,
            'empfield':m_emp,
        })
    )

def getOriginalData(request):
    from mysite.meeting.models.meeting_record import OriginalRecord
    #print '111111111111111',request
    return ''
def parse_meetingreport_arg(request,only_uid=False):
    '''
    会议报表计算请求数据处理
    '''
    deptids=request.POST.get('DeptIDs',[])
    userids=request.POST.get('UserIDs',[])
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
        userids = ids
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
        deptids=deptIDS
        #print "deptIDS:%s"%deptIDS
        ot=['PIN','DeptID']
        if only_uid:
            userids=Employee.objects.filter(DeptID__in=deptIDS).values_list('id', flat=True).order_by(*ot)
        #print "len--userids",userids
#    st=request.POST.get('ComeTime','')
#    et=request.POST.get('EndTime','')+" 23:59:59"
#    d1=datetime.datetime.strptime(st,'%Y-%m-%d')
#    d2=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
#    try:
#        offset = int(request.REQUEST.get('p', 1))
#    except:
#        offset=1
    return userids,deptids
def compareTime(baseNumber, originalRecords):
    '''
    从list列表中求出与基数最接近的一条记录
    baseNumber为会议开始时间或结束时间
    originalRecords为有效考勤记录列表
    返回originalRecords的PK，若没有则返回0
    '''
    base = baseNumber
    records = list(originalRecords)
    if len(records) == 0:
        return 0
    elif len(records) == 1:
        return records[0].pk
    else:
        accuracy = records[0]
        for i in list(range(len(records)-1)):
            if abs(accuracy.checkTime - base) > abs(records[i+1].checkTime - base):
                accuracy = records[i+1]
        return accuracy.pk

def getValidRecord(mAll):
    from mysite.meeting.models.meeting_record import OriginalRecord
    from mysite.meeting.models.model_meeting import MeetingEntity
    from mysite.meeting.models.meeting_emp import MeetingEmp
   
    #根据会议取有效记录（有签到有签退才算有效记录）
    meetingAll = []
    try:
        meetingAll.extend(mAll)
    except:
        meetingAll.append(mAll)
    if len(meetingAll) < 1:
        meetingAll = list(MeetingEntity.objects.all())
        
#    meetingAll = list(MeetingEntity.objects.all())
    validDataEmp = {}
    
    for m in meetingAll:
        startTime = m.startTime
        #会议签到取卡区间 2012.7.30修改
        earliestStartTime = datetime.datetime(m.startTime.year,m.startTime.month,m.startTime.day,m.startCheckInTime.hour,m.startCheckInTime.minute,m.startCheckInTime.second)
        latestStartTime = startTime + datetime.timedelta(minutes = m.lateAllow)
        endTime = m.endTime
        #会议签退取卡区间
        earliestEndTime = endTime - datetime.timedelta(minutes = m.leaveAllow)
        #2012.7.30修改
        latestEndTime = datetime.datetime(m.endTime.year,m.endTime.month,m.endTime.day,m.endCheckOutTime.hour,m.endCheckOutTime.minute,m.endCheckOutTime.second)

        #获得参与该会议所有人员
        meetingEmps = list(MeetingEmp.objects.filter(meetingID = m))

        #初始化字典，用来保存会议人员的两次打卡记录（签到签退），为空则为未打卡
        for emp in meetingEmps:
            validDataEmp[str(m.pk)+'_'+str(emp.pk)] = None
        for emp in meetingEmps:
            signIn = []
            signOut = []
            validData = []
            records = OriginalRecord.objects.filter(meetingID__exact=m, user__exact = emp.user)
            #获取正常记录
            for record in records:
                if record.checkTime >= earliestStartTime and record.checkTime <= latestStartTime:
                    signIn.append(record)
                elif record.checkTime >= earliestEndTime and record.checkTime <= latestEndTime:
                    signOut.append(record)
            #如果没有则获取异常记录
            if len(signIn)<1 and len(signOut)>0:
                for record in records:
                    if record.checkTime > latestStartTime and record.checkTime <= endTime:
                        signIn.append(record)
            if len(signIn)>0 and len(signOut)<1:
                for record in records:
                    if record.checkTime > startTime and record.checkTime <= earliestEndTime:
                        signOut.append(record)
            if len(signIn)<1 and len(signOut)<1:
                for record in records:
                    signIn.append(record)
                    signOut.append(record)
            recordIn = compareTime(startTime,signIn)
            validData.append(recordIn)
            
            recordOut = compareTime(endTime,signOut)
            validData.append(recordOut)
            
            validDataEmp[str(m.pk)+'_'+str(emp.pk)] = validData
#except :
#    import traceback;traceback.print_exc();
        return validDataEmp

                    
@login_required
def getValidRecords(request):
    from dbapp.datalist import save_datalist
    from headerStatistics import ConstructValidRecordFields
    
    validRecords = []
    result = {}
    
    deptIDs=request.POST.get('DeptIDs',"")
    userIDs=request.POST.get('UserIDs',"")
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
#    st=datetime.datetime.strptime(st,'%Y-%m-%d')
#    et=datetime.datetime.strptime(et,'%Y-%m-%d')
#    et=et+datetime.timedelta(days=-1)

    FieldNames = []
    FieldCaption = []
    r = []
    r,FieldNames,FieldCaption = ConstructValidRecordFields()

    result['fieldnames']=FieldNames
    result['fieldcaptions']=FieldCaption
    result['datas']=r
    heads={}
    vr = {}
    
    for i in range(len(FieldNames)):
        heads[FieldNames[i]]=FieldCaption[i]
    result['heads']=heads
    
    result['fields'] = FieldNames
    validRecords = list(getValidRecord(request))
    for key in r.keys():
        vr[key] = ""
    re=[]
    records = {}

    
    for validRecord in validRecords:
        pass
#        emp = Employee.objects.get(pk=validRecord.UserID.pk)
#        vr['badgenumber'] = emp.PIN
#        vr['username'] = emp.EName
#        vr['deptid'] = emp.DeptID.code
#        vr['deptname'] = emp.DeptID.name
#        vr['numberMeeting'] = validRecord.meetingID.numberMeeting
#        vr['nameMeeting'] = validRecord.meetingID.nameMeeting
#        vr['startTime'] = validRecord.meetingID.startTime
#        vr['endTime'] = validRecord.meetingID.endTime
#        vr['startCheckTime'] = 
#        vr['endCheckTime'] = 
#        vr['duration'] = 
#        vr['nameSN'] = validRecord.nameSN

        
        re.append(records)
    result['data'] = re
#    result['tmp_name'] = r
#    tmp_name=save_datalist(result)
#    r['tmp_name']=tmp_name
#    print 'tmp_name:%s' % tmp_name
    return getJSResponse(smart_str(dumps(result)))
        
def meetingStatistics(request):
    from mysite.meeting.models.meeting_record import OriginalRecord
    pass

