# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from base.cached_model import CachingModel
from base.operation import Operation
from django.contrib.auth.models import User, Permission, Group
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
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey

from mysite.iclock.models.model_trans   import Transaction
from base.operation import ModelOperation
from base.middleware.threadlocals import   get_current_request
from django import forms
 ##员工考勤修改日志##

ATTSTATES=(
    ("I",_(u"上班签到")),
    ("O",_(u"下班签退")),
)
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


class CheckExact(CachingModel):
    UserID = EmpPoPForeignKey(verbose_name=_(u'人员'),db_column='UserID',  editable=True)    
    CHECKTIME = models.DateTimeField(_(u'签卡时间'),null=False, blank=False)
    CHECKTYPE=models.CharField(_(u'考勤状态'),max_length=5, default=" ",blank=True,choices=ATTSTATES)
    ISADD=models.SmallIntegerField(null=True, blank=True,editable=False)
    YUYIN=models.CharField(_(u'签卡原因'),max_length=100, null=True, blank=True)
    ISMODIFY=models.SmallIntegerField(null=True, default=0,blank=True,editable=False)
    ISDELETE=models.SmallIntegerField(null=True,default=0, blank=True,editable=False)
    INCOUNT=models.SmallIntegerField(null=True,default=0, blank=True,editable=False)
    ISCOUNT=models.SmallIntegerField(null=True, default=0,editable=False)
    MODIFYBY = models.CharField(_(u'修改'),max_length=20,null=True, blank=True,editable=False)
    DATE=models.DateTimeField(_(u'员工考勤修改日志日期'),null=True, blank=True,editable=False)
    audit_status=models.SmallIntegerField(_(u'审核状态'),blank=True,null=True,default=APPLICATION,choices=APPLICATION_STATUS,editable=False)
    audit_reason=models.CharField(_(u'审核原因'),max_length=100,blank=True,null=True,editable=False)
    
    def save(self,**args):
        
        ce=CheckExact.objects.filter(UserID=self.UserID,CHECKTIME=self.CHECKTIME)
        if ce and ce[0].id!=self.id:
                   raise Exception(_(u'补签记录输入重复'))
        if self.pk!=None:
            ce=CheckExact.objects.get(pk=self.pk)
        old=""
        if ce:
            old=Transaction.objects.filter(PIN=self.UserID.PIN,TTime=ce.CHECKTIME)
       
        req=get_current_request()
        if self.pk:
            ce=CheckExact.objects.get(pk=self.pk)
            if req.session.has_key("employee"):
                if ce.audit_status==REFUSE:
                   self.audit_status=APPLICATION_AGAIN
                if ce.audit_status== AUDIT_SUCCESS:
                   raise Exception(_(u'已经审核的记录不能被修改'))
        elif not req.session.has_key("employee"):
            self.audit_status= AUDIT_SUCCESS
        
        super(CheckExact,self).save(**args)
        if old: #---修改
            t=old[0]
            if  self.audit_status != AUDIT_SUCCESS:
                t.delete()
                t = None
        else:   #---新增
            if self.audit_status == AUDIT_SUCCESS:            
                t=Transaction()
            else:
                t = None
        if t:
            t.PIN=self.UserID.PIN
            t.TTime=self.CHECKTIME
            t.State=self.CHECKTYPE
            t.Verify=5
            t.save()
        from mysite.att.models.__init__ import get_autocalculate_time as gct
        from model_waitforprocessdata import WaitForProcessData as wfpd
        gct_time=gct()
        if self.CHECKTIME<gct_time:
            wtmp=wfpd()                
            st=datetime.datetime(self.CHECKTIME.year,self.CHECKTIME.month,self.CHECKTIME.day,0,0,0)
            et=datetime.datetime(self.CHECKTIME.year,self.CHECKTIME.month,self.CHECKTIME.day,23,59,59)
            wtmp.UserID=self.UserID
            wtmp.starttime=st
            wtmp.endtime=et
            wtmp.save()
        
    class _add(ModelOperation):
        visible=False
        verbose_name=_(u'新增')
        def action(self):
            pass
    def delete(self):
        Transaction.objects.filter(PIN=self.UserID.PIN,TTime=self.CHECKTIME).delete()
        super(CheckExact,self).delete()
        
    def __unicode__(self):
        u'''修改从 内存中获取 '''
        emp_obj=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
        except:
            pass
        return u"%s"%emp_obj
    
    class OpAddManyCheckExact(ModelOperation):
        verbose_name=_(u"新增补签卡")
        help_text=_(u'新增补签卡同时会在原始记录表中增加一条相同记录，修改时会同时修改原始记录表中的相同记录')
        params=(
            ('UserID', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)),            
            ('checktime',models.DateTimeField(_(u'签卡时间'))),
            ('checktype',models.CharField(_(u'考勤状态'),max_length=5, default=" ",blank=True,choices=ATTSTATES)),
            ('reason',models.CharField(_(u'签卡原因'),blank=True,null=True,max_length=100)),
        )
        def action(self,UserID,checktime,checktype,reason):
            users = UserID
            if self.request:
                if not users:
                    raise Exception(u"%s"%_(u'请选择人员'))
                if checktime>datetime.datetime.now():
                    raise Exception(_(u'补签时间不能大于现在'))
                ce=CheckExact.objects.filter(UserID__in=UserID,CHECKTIME=checktime)
                pins = [u.PIN for u in users]
                trs=Transaction.objects.filter(PIN__in=pins,TTime=checktime).count()
                if ce.count()>0 :
                    raise Exception(_(u'补签记录输入重复'))
                if trs>0:
                    raise Exception(_(u'原始记录中已经有该记录'))
                if len(UserID)>1000:
                    raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
                for emp in UserID:
                    ck=CheckExact()
                    ck.UserID=emp
                    ck.CHECKTIME=checktime
                    ck.YUYIN=reason
                    ck.CHECKTYPE=checktype
                    ck.save()
    def get_emp_name(self):
        u'''从缓存中得到人员name'''
        
        emp_name=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
            emp_name=emp_obj.EName
        except:
            pass
        return emp_name

    def get_emp_pin(self):
        u'''从缓存中得到人员PIN号'''
        emp_pin=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
            emp_pin=emp_obj.PIN
        except:
            pass
        return emp_pin
    
    def delete(self):
        req=get_current_request()
        if req.session.has_key("employee"):
            if self.audit_status== AUDIT_SUCCESS:
                raise Exception(_(u'审核通过的记录不能被删除'))
        if self.audit_status== AUDIT_SUCCESS:
            from model_waitforprocessdata import WaitForProcessData as wfpd
            import datetime
            wtmp=wfpd()                
            st=datetime.datetime(self.CHECKTIME.year,self.CHECKTIME.month,self.CHECKTIME.day,0,0,0)
            et=datetime.datetime(self.CHECKTIME.year,self.CHECKTIME.month,self.CHECKTIME.day,23,59,59)
            wtmp.UserID=self.UserID
            wtmp.starttime=st
            wtmp.endtime=et
            wtmp.save()
        
        Transaction.objects.filter(PIN=self.UserID.PIN,TTime=self.CHECKTIME).delete()
        super(CheckExact,self).delete()
    
    class OpAuditCheckexact(Operation):
        verbose_name=_(u'审批')
        help_text=_(u'补签卡审批')
        params=(
                   ('stat',models.IntegerField(_(u'审核状态'),null=False,blank=False,default=AUDIT_SUCCESS,choices=AUDIT_STATUS)),
                   ('reason',models.CharField(_(u'审核原因'),null=True,blank=True,max_length=100)),
               )
        
        def action(self,stat,reason):
            if self.object.audit_status ==AUDIT_SUCCESS:
                raise Exception(_(u"%(emp)s,%(ct)s,%(ctype)s,%(rm)s 已审核")%{
                    "emp":self.object.UserID,
                    "ct":self.object.CHECKTIME,
                    "ctype":self.object.CHECKTYPE,
                    "rm":self.object.YUYIN
                })
            
            self.object.audit_status=stat
            self.object.audit_reason=reason
            self.object.save()
    
    class Admin(CachingModel.Admin):
        default_give_perms=["contenttypes.can_AttCalculate",]
        sort_fields=["UserID.PIN","CHECKTIME"]
        menu_index=5
        app_menu="att"
        api_fields=('UserID.PIN','UserID.EName','CHECKTIME','CHECKTYPE','YUYIN')
        list_display=('UserID_id','UserID.PIN','UserID.EName','CHECKTIME','CHECKTYPE','YUYIN','audit_status|audit_filter','audit_reason')
        
        list_filter =('UserID','CHECKTIME','CHECKTYPE','YUYIN')
        query_fields=('UserID__PIN','UserID__EName','CHECKTIME')
        tstart_end_search={
            "CHECKTIME":[_(u"起始时间"),_(u"结束时间")]
        }
        hide_fields=('UserID_id',)
        disabled_perms=["add_checkexact",'dataimport_checkexact']
    class Meta:
        app_label='att'
        db_table = 'checkexact'
        verbose_name=_(u'补签卡')
        verbose_name_plural=verbose_name
        
