# -*- coding: utf-8 -*-
from django.db import models
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django import forms
 
from base.cached_model import CachingModel
from base.operation import Operation,ModelOperation
from mysite.personnel.models.model_emp import Employee,EmpPoPMultForeignKey,EmpForeignKey,EmpMultForeignKey

ATTTYPE=(
    (0,_(u'正常上班')),
    (2,_(u'休息')),
)

class SetUserAtt(CachingModel):
    UserID=EmpForeignKey(verbose_name=_(u'人员'),blank=True,null=True)
    starttime=models.DateTimeField(_(u'开始时间'),blank=False,null=False)
    endtime=models.DateTimeField(_(u'结束时间'),blank=False,null=False)
    atttype=models.SmallIntegerField(_(u'考勤类型'),default=2,choices=ATTTYPE,blank=False,null=False,editable=False)
    
    def save(self,**args):
        if self.UserID=="" or self.UserID==None:
            raise Exception(_(u'请选择人员！'))
        if self.endtime<=self.starttime:
            raise Exception(_(u'结束时间不能小于或等于开始时间！'))
        sua=SetUserAtt.objects.filter(UserID=self.UserID,starttime__lte=self.endtime,endtime__gte=self.starttime)
        if sua and sua[0].pk!=self.pk:
            raise Exception(_(u'调休记录输入重复'))
            
        
        super(SetUserAtt,self).save(**args)  
        from mysite.att.models.__init__ import get_autocalculate_time as gct
        from model_waitforprocessdata import WaitForProcessData as wfpd
        import datetime
        gct_time=gct()
        if self.starttime<gct_time or self.endtime<=gct_time:
              wtmp=wfpd()                
              st=self.starttime
              et=self.endtime
              wtmp.UserID=self.UserID
              wtmp.starttime=st
              wtmp.endtime=et
              wtmp.save()

    def __unicode__(self):
        emp_obj=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
        except:
            pass
        return u"%s"%emp_obj
        
    class OpAddManyObj(ModelOperation):
        verbose_name=_(u'新增')
        help_text=_(u'新增')
        params=(
            ('UserID',EmpMultForeignKey(verbose_name=_(u'人员'),null=True,blank=True)),
            ('starttime',models.DateTimeField(_(u'开始时间'),blank=False,null=False)),
            ('endtime',models.DateTimeField(_(u'结束时间'),blank=False,null=False)),
#            ('atttype',models.SmallIntegerField(_(u'考勤类型'),default=2,choices=ATTTYPE,blank=False,null=False)),
            
        )
        def action(self,UserID,starttime,endtime):     
            users = UserID        
            if self.request:
                if not users:
                    raise Exception(u"%s"%_(u'请选择人员'))
                if len(users)>1000:
                    raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
                for u in users:
                    sua=SetUserAtt()
                    sua.UserID=u
                    sua.starttime=starttime
                    sua.endtime=endtime
#                    sua.atttype=atttype
                    sua.save()
    class _add(ModelOperation):
        visible=False
        verbose_name=_(u'新增')
        help_text=_(u'新增')
        def action(self):
            pass
    def get_emp_pin(self):
        u'''从缓存中得到人员PIN号'''
        emp_pin=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
            emp_pin=emp_obj.PIN
        except:
            pass
        return emp_pin
    
    def get_emp_name(self):
        u'''从缓存中得到人员姓名'''
        emp_name=""
        try:
            emp_obj=Employee.objects.get(id=self.UserID_id)
            emp_name=emp_obj.EName
        except:
            pass
        return emp_name
    
    class Admin(CachingModel.Admin):
        list_display=('UserID.PIN','UserID.EName','starttime','endtime')
        query_fields=('UserID.PIN','UserID.EName')
        adv_fields=('UserID.PIN','UserID.EName','starttime','endtime')
        help_text=_(u'设置人员调休：可以在已经安排了排班的情况下，设置人员为休息')
        #default_widgets={'UserID':EmpPoPMultForeignKey}
        hide_perms = ["add_setuseratt",]

        menu_index = 7
    class Meta:
        app_label="att"
        db_table="setuseratt"
        verbose_name=_(u'调休')
