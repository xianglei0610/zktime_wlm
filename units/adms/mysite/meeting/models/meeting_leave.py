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
from meeting_emp import MeetingEmp,MeetingEmpForeignKey,MeetingEmpMultForeignKey,Emp_MeetingMultFK
from model_meeting import MeetingEntity,MeetingForeignKey,MeetingManyToToManyField          
from meeting_emp import MeetingEmp

class Leave(CachingModel):
    id = models.AutoField(db_column="id",primary_key=True,editable=False)
#    employee =  MeetingEmpForeignKey(verbose_name=_(u'人员'),  editable=True) 
    employee =  EmpForeignKey(verbose_name=_(u'人员'), null=True,blank=True,editable=True)
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'))
    reason = models.CharField(verbose_name=_(u'请假原因'), max_length=100,null=True,blank=True)
    apply = models.DateTimeField(verbose_name=_(u'填写时间'), null=True,editable=False)
    
    def __unicode__(self):
        return '%s %s' % (self.meetingID, self.employee)
    
    def save(self):
        if self.employee == None:
            raise Exception(_(u"请选择人员"))
        mm = MeetingEmp.objects.filter(meetingID=self.meetingID,user=self.employee)
        if len(mm)<1 :
            raise Exception(_(u"%s 没有参加该会议，无须请假") %self.employee.EName)
        
        super(Leave,self).save()
        
    class _add(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass

        
    class OpAddMeetingLeave(ModelOperation):
        help_text=_(u"新增会议请假")
        verbose_name=_(u"新增请假")
        
        params = (
           ('meetingID',MeetingForeignKey(verbose_name=_(u'会议'))),
           ('userLeave', Emp_MeetingMultFK(verbose_name=_(u'人员'),blank=True)),            
           ('reason', models.CharField(verbose_name=_(u'请假原因'), max_length=100,null=True,blank=True)),
        )
        
#        def action(self,meetingId,userLeave,reason):
#            print "len(userLeave)",len(userLeave)
#            if len(userLeave) < 1 :
#                raise Exception(_(u"请选择人员"))
#            
#            for emp in userLeave:
#                mm = MeetingEmp.objects.filter(meetingID=meetingId,user=emp)
#                
#                ce=Leave.objects.filter(employee=emp,meetingID=meetingId)
#                if len(ce)>=1:
#                    raise Exception(_(u'%s 请假重复') % emp)
#                
#                ck=Leave(employee=emp,meetingID=meetingId,reason=reason)
#                ck.save()
        def action(self,**args):
            from mysite.iclock.iutils import get_dept_from_all,get_max_in
            emps=args.pop('userLeave')
            if not emps :
                raise Exception(_(u"请选择人员"))
            
            for emp in emps:
                mm = MeetingEmp.objects.filter(meetingID=args['meetingID'],user=emp)
                
                ce=Leave.objects.filter(employee=emp,meetingID=args['meetingID'])
                if len(ce)>=1:
                    raise Exception(_(u'%s 请假重复') % emp)
                t_now = datetime.datetime.now()
                ck=Leave(employee=emp,apply=t_now,meetingID=args['meetingID'],reason=args['reason'])
                ck.save()
  
                

                
    def get_dept_name(self):
        u'''从缓存中得到部门的Name'''
        from mysite.personnel.models import Department
        dept_name=""
        try:
            dept_obj=Department.objects.get(id=self.employee.DeptID_id)
            dept_name=dept_obj.name
        except:
            pass
        return dept_name



    class Admin(CachingModel.Admin): 
        menu_group = 'meeting'
        menu_index=5
        query_fields = ['meetingID.numberMeeting','meetingID.nameMeeting','employee.PIN','employee.EName','employee.DeptID']
        sort_fields = ['meetingID.numberMeeting','employee.DeptID','employee.PIN','-apply']
        list_display = ['meetingID.numberMeeting','meetingID.nameMeeting','employee.PIN','employee.EName','employee.DeptID','reason','apply']
        newadded_column = {
            'employee.DeptID':'get_dept_name',                                
        }
        
        
    class Meta:
        verbose_name=_(u'会议请假')
        verbose_name_plural=verbose_name
        app_label=  'meeting'
        



#class MeetingEmpPoPMultForeignKey(models.ManyToManyField):
#    def __init__(self, *args, **kwargs):
#            super(MeetingEmpPoPMultForeignKey, self).__init__(MeetingEmp, *args, **kwargs)
#
#def update_dept_widgets():
#        from dbapp import widgets
#        if EmpForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
#                from empwidget import ZEmpChoiceWidget, ZMulEmpChoiceWidget, ZMulPopEmpChoiceWidget, ZPopEmpChoiceWidget
#                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpForeignKey] = ZEmpChoiceWidget
#                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpMultForeignKey] = ZMulEmpChoiceWidget
#                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpPoPForeignKey] = ZPopEmpChoiceWidget
#                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpPoPMultForeignKey] = ZMulPopEmpChoiceWidget
#
#update_dept_widgets()
        

