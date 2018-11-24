# -*- coding: utf-8 -*-
import datetime
from django.db import models, connection
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from base.cached_model import CachingModel
from base.operation import Operation
from base.middleware.threadlocals import  get_current_request
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey
from base.operation import ModelOperation

APPLICATION = 1
AUDIT_SUCCESS = 2
REFUSE = 3
APPLICATION_AGAIN = 4

APPLICATION_STATUS=(
    (APPLICATION,_(u'申请')),
    (APPLICATION_AGAIN,_(u'重新申请')),
    (AUDIT_SUCCESS,_(u'审核通过')),
    (REFUSE,_(u'拒绝')),
)

AUDIT_STATUS=(
    (AUDIT_SUCCESS,_(u'审核通过')),
    (REFUSE,_(u'拒绝')),

)


class OverTime(CachingModel):
    emp=EmpPoPForeignKey(verbose_name=_(u'人员'), null=False, blank=False)
    starttime= models.DateTimeField(_(u'开始时间'),  null=False,  blank=False)
    endtime = models.DateTimeField(_(u'结束时间'), null=False, blank=False)
    remark=models.CharField(_(u'加班描述'),null=True,blank=True,max_length=200)
    audit_status=models.IntegerField(_(u'审核状态'),null=False,blank=False,default=APPLICATION,choices=APPLICATION_STATUS,editable=False)
    auditreason=models.CharField(_(u'审核原因'),null=True,blank=True,max_length=100,editable=False)
    
    def __unicode__(self):
        return u"%s"%(self.emp)
    
    def save(self):
        #验证
        obj_tmp=OverTime.objects.filter(emp=self.emp,starttime__lte=self.endtime,endtime__gte=self.starttime)
        if obj_tmp and obj_tmp[0].pk!=self.pk:
            raise Exception(_(u'加班记录重复'))
        if self.endtime<=self.starttime:
            raise Exception(_(u'结束时间不能小于等于开始时间'))
        
        req=get_current_request()
        if self.pk:#编辑
            tmp=OverTime.objects.get(pk=self.pk)
            if req.session.has_key("employee"):#员工自助用户申请或者重新申请
                if tmp.audit_status == REFUSE:
                    self.audit_status = APPLICATION_AGAIN
                if tmp.audit_status == AUDIT_SUCCESS:
                    raise Exception(_(u'该记录已审核'))
        elif (not req.session.has_key("employee")):#管理员，新增，默认就是审核通过
            self.audit_status=AUDIT_SUCCESS
        
        super(OverTime,self).save()
#        from mysite.att.calculate.global_cache import JBD_DATA
#        if JBD_DATA.has_key(self.emp.id):
#            del JBD_DATA[self.emp.id]
        if self.audit_status==AUDIT_SUCCESS:
            from mysite.att.models.__init__ import get_autocalculate_time as gct
            from model_waitforprocessdata import WaitForProcessData as wfpd
            
            gct_time=gct()
            if self.starttime<gct_time or self.endtime<=gct_time:
                wtmp=wfpd()                
                st=datetime.datetime(self.starttime.year,self.starttime.month,self.starttime.day,0,0,0)
                et=datetime.datetime(self.endtime.year,self.endtime.month,self.endtime.day,23,59,59)
                wtmp.UserID=self.emp
                wtmp.starttime=st
                wtmp.endtime=et
                wtmp.save()
        
    def delete(self):
        u"删除加班单"
        req=get_current_request()
        if req.session.has_key("employee"):
            if  self.audit_status==AUDIT_SUCCESS:
                raise Exception(_(u'审核通过的记录不能被删除'))
        if self.audit_status==AUDIT_SUCCESS:
            from model_waitforprocessdata import WaitForProcessData as wfpd
            wtmp=wfpd()                
            st=datetime.datetime(self.starttime.year,self.starttime.month,self.starttime.day,0,0,0)
            et=datetime.datetime(self.endtime.year,self.endtime.month,self.endtime.day,23,59,59)
            wtmp.UserID = self.emp
            wtmp.starttime = st
            wtmp.endtime = et
            wtmp.save()
        
        super(OverTime,self).delete()
#        from mysite.att.calculate.global_cache import JBD_DATA
#        if JBD_DATA.has_key(self.emp.id):
#            del JBD_DATA[self.emp.id]
        
    @staticmethod
    def clear():
        OverTime.objects.all().delete()

    class OpAuditManyEmployee(Operation):
        u"批量审核"
        verbose_name=_(u'审批')
        help_text=_(u'加班单审批')
        params=(
            ('stat',models.IntegerField(_(u'审核状态'),null=False,blank=False,default=AUDIT_SUCCESS,choices=AUDIT_STATUS)),
            ('reason',models.CharField(_(u'审核原因'),null=True,blank=True,max_length=100)),
        )
        def action(self,stat,reason):
            if self.object.audit_status ==AUDIT_SUCCESS:
                raise Exception(_(u"%(emp)s,%(st)s,%(et)s,%(rm)s 已审核")%{
                    "emp":self.object.emp,
                    "st":self.object.starttime,
                    "et":self.object.endtime,
                    "rm":self.object.remark
                })
            self.object.audit_status=stat
            self.object.auditreason=reason
            self.object.save()
    class _add(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass
    
    class OpAddManyOvertime(ModelOperation):
        help_text=_(u'''新增''')
        verbose_name=_(u"新增加班单")
        params=(
            ('UserID', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)), 
            ('starttime', models.DateTimeField(_(u'开始时间'),  null=False,  blank=False)),
            ('endtime', models.DateTimeField(_(u'结束时间'), null=False, blank=False)),
            ('remark', models.CharField(_(u'加班描述'),null=True,blank=True,max_length=200)),
        )
        def action(self, **args):
            emps=args.pop('UserID')
            if args['starttime']>=args['endtime']:
                raise Exception(_(u'结束时间不能小于等于开始时间'))
            if not emps:
                raise Exception(_(u'请选择人员'))
            if len(emps)>1000:
                raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
            for emp in emps: 
                OverTime(emp=emp, **args).save()
        
    class Admin(CachingModel.Admin):
        menu_index = 6
        query_fields=['emp.PIN','emp.EName','remark','audit_status','auditreason']
        list_display=['emp','starttime','endtime','remark','audit_status|audit_filter','auditreason']
        
    class Meta:
        app_label='att'
        verbose_name=_(u'加班单')
        unique_together = (("emp", "starttime","endtime"),)
    
        
