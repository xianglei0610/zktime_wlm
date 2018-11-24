#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.db import models
import datetime
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey
#from model_ycm import MeetingIDForeignKey,Meeting
from model_meeting import MeetingEntity,MeetingForeignKey,MeetingManyToToManyField          
from meeting_record import OriginalRecord
from meeting_leave import Leave
from meeting_emp import MeetingEmp,MeetingEmpForeignKey,MeetingEmpMultForeignKey,Emp_MeetingMultFK
import datetime
import time
ATTSTATES=(
    (1,_(u"会议签到")),
    (2,_(u"会议签退")),
)
STATU = (
    (1,_(u"同意")),
)
def date_time(date,time):
    date=date.strftime("%Y-%m-%d")
    time=time.strftime("%H:%M:%S")
    mm=[]
    yy=date.split("-")
    for y in yy:
        mm.append(y)
    zz=time.split(":")
    for z in zz:
        mm.append(z)

    d_now = datetime.datetime( int(mm[0]),int(mm[1]),int(mm[2]),int(mm[3]),int(mm[4]),int(mm[5]) )
    return d_now

class MeetingExact(CachingModel):
    id = models.AutoField(db_column="id", primary_key=True,editable=False)
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'))
    user = EmpForeignKey(verbose_name=_(u'人员'),db_column='userid',null=True,blank=True,editable=True) 
    checkType = models.IntegerField(verbose_name=_(u'考勤状态'),choices=ATTSTATES)
    checkTime = models.DateTimeField(verbose_name=_(u'补签时间'),editable=False)
    reason = models.CharField(_(u'补签原因'), db_column='reson', max_length=100,null=True,blank=True)
    apply = models.DateTimeField(_(u'填写时间'), db_column='applydate', null=True, default=datetime.datetime.now(),editable=False)
    
    def __unicode__(self):
        return '%s %s' %(self.meetingID.nameMeeting,self.user.EName)
    
    def save(self):
        from meeting_emp import MeetingEmp
        if self.user == None:
            raise Exception(_(u"请选择人员"))
        mm = MeetingEmp.objects.filter(meetingID=self.meetingID,user=self.user)
        
        if len(mm)<1 :
            raise Exception(_(u"%s 没有参加该会议，无须补签") %self.user.EName)
        mleave = Leave.objects.filter(meetingID=self.meetingID,employee=self.user)
        if len(mleave)>0:
            raise Exception(_(u"%s 已经请假，补签前请先删除请假记录") %self.user.EName)
        me = MeetingEntity.objects.filter(pk=self.meetingID.pk)
        
        if self.checkType == 1:
            self.checkTime = me[0].startTime
        else:
            self.checkTime = me[0].endTime
#        if me.startTime.date() != self.checkTime.date():
#            raise Exception(_(u'补签日期与该会议日期(%s)不一致') % me.startTime.date() )
#        ss = (me.startTime - datetime.timedelta(minutes = me.startCheckTime)).time()
#        if self.checkType == 1 and (self.checkTime.time() < ss or self.checkTime.time() > me.startTime.time()):
#            raise Exception(_(u'补签时间不在有效区间内（%s,%s）') %(ss,me.startTime.time()))
#        ee = (me.endTime + datetime.timedelta(minutes = me.endCheckTime)).time()
#        if self.checkType == 2 and (self.checkTime.time() < me.endTime.time() or self.checkTime.time() > ee):
#            raise Exception(_(u'补签时间不在有效区间内（%s,%s）') %(me.endTime.time(),ee))
        
        
        if self.id:
            mEx = MeetingExact.objects.get(id=self.id)
#            if mEx.meetingID != self.meetingID:
#                raise Exception(_(u'会议不可更改'))
            oRecEx = OriginalRecord.objects.filter(user=mEx.user,meetingID=mEx.meetingID,checkType=mEx.checkType,verifyCode=6)
            if len(oRecEx)>0:
                oRecEx.delete()
        
#        oRec = OriginalRecord.objects.filter(user=self.user,meetingID=self.meetingID,checkType=self.checkType,verifyCode=6)
#        
#        if len(oRec)>0:
#            oRec[0].delete()
        record = OriginalRecord(user=self.user,meetingID=self.meetingID,checkTime=self.checkTime,checkType=self.checkType,verifyCode=6)
        record.save()
        
        
        
        super(MeetingExact,self).save()
        
    def delete(self):
        try:
            record = OriginalRecord.objects.get(user=self.user,meetingID=self.meetingID,checkTime=self.checkTime,checkType=self.checkType,verifyCode=6)
            record.delete()
        except:
            pass
        super(MeetingExact,self).delete()
    
    class OpMeetingCheckExact(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass
        
    class _add(ModelOperation):
        visible=False
        verbose_name = _(u"增加")
        help_text = _(u'新增')
        
    def get_dept_name(self):
        u'''从缓存中得到部门的Name'''
        from mysite.personnel.models import Department
        dept_name=""
        try:
            dept_obj=Department.objects.get(id=self.user.DeptID_id)
            dept_name=dept_obj.name
        except:
            pass
        return dept_name

    
    class AddMeetingExact(ModelOperation):
#        visible=False
        verbose_name=_(u"补签卡")
        help_text=_(u"会议补签卡")

        params=(
            ('meetingID',MeetingForeignKey(verbose_name=_(u'会议'),null=True)),
            ('users', Emp_MeetingMultFK(verbose_name=_(u'人员'),blank=True,null=True)),            
            ('checktype', models.IntegerField(_(u'考勤状态'),default="1",choices=ATTSTATES)),
#            ('checkTime', models.DateTimeField(verbose_name=_(u'补签时间'),editable=False)),
            ('reason',models.CharField(_(u'补签原因'),max_length=50,null=True,blank=True)),         
        )
        def action(self,**args):
            from mysite.meeting.models.meeting_exact import OriginalRecord
            users=args.pop('users')
            if self.request:
                if len(users)<1:
                    raise Exception(_(u"请选择人员"))
                for emp in users:
                    e = MeetingEmp.objects.filter(meetingID=args['meetingID'],user=emp)
                    if len(e)<1:
                        raise Exception(_(u"%s 没有参加该会议，无须补签") %emp)
                    
                    ce=MeetingExact.objects.filter(meetingID=args['meetingID']).filter(checkType=args['checktype']).filter(user=emp)
                    if len(ce)>0:
                        raise Exception(_(u'%s 补签卡重复')% ce[0].user.EName)
                
                    ck=MeetingExact()
                    ck.user=emp
                    ck.meetingID=args['meetingID']
                    ck.checkType=args['checktype']
#                    ck.checkTime=checkTime
                    ck.reason=args['reason']
                    ck.save()
                    
#    def action(self,meetingID,users,checktype,reason):
#            from mysite.meeting.models.meeting_exact import OriginalRecord
#            emps=args.pop('users')
#            if self.request:
#                if len(users)<1:
#                    raise Exception(_(u"请选择人员"))
#                for emp in users:
#                    e = MeetingEmp.objects.filter(meetingID=meetingID,user=emp)
#                    if len(e)<1:
#                        raise Exception(_(u"%s 没有参加该会议，无须补签") %emp)
#                    
#                    ce=MeetingExact.objects.filter(meetingID=meetingID).filter(checkType=checktype).filter(user=emp)
#                    if len(ce)>0:
#                        raise Exception(_(u'%s 补签卡重复')% ce[0].user.EName)
#                
#                    ck=MeetingExact()
#                    ck.user=emp
#                    ck.meetingID=meetingID
#                    ck.checkType=checktype
##                    ck.checkTime=checkTime
#                    ck.reason=reason
#                    ck.save()
#                    
#    

    class Admin(CachingModel.Admin):
        sort_fields = ['meetingID.numberMeeting','user.DeptID','user.PIN','-checkTime']
        menu_group = 'meeting'
        menu_index = 6
        list_display = ['meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','user.DeptID','checkType','reason','checkTime']
        query_fields=['meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','checkType']     #需要查找的字段
        newadded_column={
            "user.DeptID":"get_dept_name",             
        } 
        

    class Meta:
        verbose_name=_(u'会议补签卡')#名字
        verbose_name_plural=verbose_name
        app_label= 'meeting' #属于哪个app
        




        

