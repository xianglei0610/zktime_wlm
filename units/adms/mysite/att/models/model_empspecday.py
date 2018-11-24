# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
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
from base.models import CachingModel, Operation
from model_leaveclass import LeaveClass
from django.db.models import Q
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey
from mysite.personnel.models.empwidget import ZMulPopEmpChoiceWidget
from base.operation import ModelOperation
from base.middleware.threadlocals import   get_current_request


APPLICATION = 1
AUDIT_SUCCESS = 2
REFUSE = 3
APPLICATION_AGAIN = 4

APPLICATION_STATUS=(
    (APPLICATION,_(u'申请')),
    (APPLICATION_AGAIN,_(u'重新申请')),
)

AUDIT_STATUS=(
    (AUDIT_SUCCESS,_(u'审核通过')),
    (REFUSE,_(u'拒绝')),

)

ALL_STATUS=tuple(list(APPLICATION_STATUS) +list(AUDIT_STATUS))

AUDIT_STATES=(
    (0,_(u'申请')),
    (1,_(u'正在审核')),
    (2,_(u'已接受')),
    (3,_(u'拒绝')),
    (4,_(u'暂停')),
    (5,_(u'重申请')),
    (6,_(u'重新申请')),
    (7,_(u'取消请假'))
)


#员工考勤例外（请假/公出）表##
class EmpSpecDay(CachingModel):
    emp=EmpPoPForeignKey(verbose_name=_(u'人员'),db_column='UserID', editable=True)
    start= models.DateTimeField(_(u'开始时间'), db_column='StartSpecDay', null=False, default=nextDay(), blank=False)
    end = models.DateTimeField(_(u'结束时间'), db_column='EndSpecDay', null=True, default=endOfDay(nextDay()),blank=False)
    leaveclass=models.ForeignKey(LeaveClass, verbose_name=_(u'假类'), db_column='DateID', null=False, blank=False,default=1)
    reson=models.CharField(_(u'请假原因'), db_column='YUANYING', max_length=100,null=True,blank=True)
    apply=models.DateTimeField(_(u'填写时间'), db_column='Date',auto_now=True, null=True, default=datetime.datetime.now, blank=True)
    audit_status=models.SmallIntegerField(_(u'审核状态'),blank=True,null=True,default=APPLICATION,choices=ALL_STATUS,editable=False)
    audit_reason=models.CharField(_(u'审核原因'),  max_length=100,null=True,blank=True,editable=False)
    state=models.CharField(_(u'申请状态'),max_length=2, null=True, db_column="State", default=APPLICATION, blank=True, choices=AUDIT_STATES, editable=False)
    def save(self, *args, **kwargs):
        if not self.emp:
            raise Exception(_(u'必须选择人员'))
        if self.start>=self.end:
            raise Exception(_(u'结束时间不能小于或等于开始时间'))
        tt=EmpSpecDay.objects.filter(emp=self.emp,start__lte=self.end,end__gte=self.start)
        if tt and tt[0].id !=self.id:
            raise Exception(_(u'请假时间重复'))
#        if tt and int(tt[0].audit_status)== AUDIT_SUCCESS:
        if self.id and  tt and tt[0].audit_status ==AUDIT_SUCCESS:
            raise Exception(_(u'审核通过的请假记录不能修改'))
#        tmp=EmpSpecDay.objects.filter(Q(emp=self.emp,start__lte=self.start,end__gte=self.end)| Q(emp=self.emp,start__gte=self.start,end__lte=self.end)).exclude(pk=1)
#        if tmp and tmp[0].pk !=self.pk :
#            raise Exception(_(u'已存在相同请假记录！'))
        
        req = get_current_request()
        if self.pk:
               tx=EmpSpecDay.objects.get(pk=self.pk)
               if req.session.has_key("employee"):
                   if int(tx.audit_status)==AUDIT_SUCCESS:
                      raise Exception(_(u'该记录已审核'))            
                   if int(tx.state)==REFUSE:
                       self.audit_status=APPLICATION_AGAIN
        elif (not req.session.has_key("employee")):
                   self.audit_status=AUDIT_SUCCESS
        
        super(EmpSpecDay,self).save()
        from mysite.att.models.__init__ import get_autocalculate_time as gct
        from model_waitforprocessdata import WaitForProcessData as wfpd
        import datetime
        gct_time=gct()
        if self.start<gct_time or self.end<=gct_time:
            wtmp=wfpd()                
            st=self.start
            et=self.end
            wtmp.UserID=self.emp
            wtmp.starttime=st
            wtmp.endtime=et
            #wtmp.customer=self.customer
            wtmp.save()
    def delete(self):
        req=get_current_request()
        if req.session.has_key("employee"):
            if int(self.audit_status)== AUDIT_SUCCESS:
                raise Exception(_(u'审核通过的记录不能被删除'))
        if int(self.audit_status)==AUDIT_SUCCESS:
            from model_waitforprocessdata import WaitForProcessData as wfpd
            wtmp=wfpd()               
            st=datetime.datetime(self.start.year,self.start.month,self.start.day,0,0,0)
            et=datetime.datetime(self.end.year,self.end.month,self.end.day,23,59,59)
            
            wtmp.UserID=self.emp
            wtmp.starttime=st
            wtmp.endtime=et
            wtmp.save()
        
        super(EmpSpecDay,self).delete()
    
    def __unicode__(self):
        emp_obj=""
        leavetype_name=""
        try:
            emp_obj=Employee.objects.get(id=self.emp_id)
            leavetype_obj=LeaveClass.objects.get(LeaveID=self.leaveclass_id)
            leavetype_name=leavetype_obj.LeaveName
        except:
            pass
        return u"%s: %s, %s"%(emp_obj, self.start and self.start.strftime("%m-%d") or "", leavetype_name)
#        return u"%s: %s, %s"%(self.emp, self.start and self.start.strftime("%m-%d") or "", self.leaveclass)
    class _add(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass
    class OpAddManyUserID(ModelOperation):
        help_text=_(u'''新增''')
        verbose_name=_(u"新增请假")
        params=(
            ('UserID', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)),          
            ('start',models.DateTimeField(_(u'开始时间'))),
            ('end',models.DateTimeField(_(u'结束时间'))),
            ('leaveclass',models.ForeignKey(LeaveClass, verbose_name=_(u'假类'))),
            ('reson',models.CharField(_(u'请假原因'),blank=True,null=True,max_length=100)),
            ('apply',models.DateTimeField(_(u'填写时间'), default=datetime.datetime.now, blank=True)),
        )
        def action(self, **args):
            from mysite.iclock.iutils import get_dept_from_all,get_max_in
            emps=args.pop('UserID')
                        
            if args['start']>=args['end']:
                raise Exception(_(u'结束时间不能小于开始时间'))
            if not emps:
                raise Exception(_(u'请选择人员'))
            if len(emps)>1000:
                raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
            for emp in emps: 
                EmpSpecDay(emp=emp, **args).save()
    
    def get_emp_pin(self):
        u'''从缓存中得到人员PIN号'''
        emp_pin=""
        try:
            emp_obj=Employee.objects.get(id=self.emp_id)
            emp_pin=emp_obj.PIN
        except:
            pass
        return emp_pin
    
    def get_emp_name(self):
        u'''从缓存中得到人员姓名'''
        emp_name=""
        try:
            emp_obj=Employee.objects.get(id=self.emp_id)
            emp_name=emp_obj.EName
        except:
            pass
        return emp_name
    
    def get_leaveclass_name(self):
        leaveclass_name=""
        try:
            leavetype_obj=LeaveClass.objects.get(LeaveID=self.leaveclass_id)
            leaveclass_name=leavetype_obj.LeaveName
        except:
            pass
        return leaveclass_name
    
    class OpSpecAudit(Operation):
        u"请假单审核"
        verbose_name=_(u'审批')
        help_text=_(u'请假审批')
        params=(
                   ('stat',models.IntegerField(_(u'审核状态'),null=False,blank=False,default=AUDIT_SUCCESS,choices=AUDIT_STATUS)),
                   ('reason',models.CharField(_(u'审核原因'),null=True,blank=True,max_length=100)),
               )
        
        def action(self,stat,reason):
            if self.object.audit_status == AUDIT_SUCCESS:
                raise Exception(_(u"%(emp)s,%(st)s,%(et)s,%(rm)s 已审核")%{
                    "emp":self.object.emp,
                    "st":self.object.start,
                    "et":self.object.end,
                    "rm":self.object.reson
                })
            self.object.audit_status=stat
            self.object.audit_reason=reason
            self.object.save()
    
    class Admin(CachingModel.Admin):
        from mysite.personnel.models.empwidget import ZMulPopEmpChoiceWidget
        sort_fields=["emp.PIN","start","end"]
        disabled_perms=['add_empspecday','dataimport_empspecday']
        #default_widgets={"emp":ZMulPopEmpChoiceWidget}
        list_filter =['emp','reson','state','leaveclass']
        query_fields=['emp.PIN','emp.EName','reson','state']
        list_display=['emp.PIN','emp.EName','start','end','reson','leaveclass','apply','audit_status|audit_filter','audit_reason']
        newadded_column={
            "leaveclass":"get_leaveclass_name",
        }
        
        report_fields=['emp','start','end','reson','leaveclass']
        menu_index=4
    class Meta:
        app_label='att'
        db_table = 'user_speday'
        verbose_name = _(u'请假')
        verbose_name_plural=verbose_name
        unique_together = (("emp", "start","leaveclass"),)

