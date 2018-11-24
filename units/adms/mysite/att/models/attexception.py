# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
from base.models import CachingModel
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
from mysite.personnel.models import Employee, EmpForeignKey
from base.models import CachingModel, Operation

#统计结果用表-异常记录表
class AttException(CachingModel):
        '''
        异常结果表
        '''
        UserID = EmpForeignKey(verbose_name=_(u'人员'),db_column='UserId',  blank=False, null=False)
        StartTime = models.DateTimeField(_(u'开始时间'), db_column='StartTime')
        EndTime = models.DateTimeField(_(u'结束时间'), db_column='EndTime')
        ExceptionID=models.IntegerField(_(u'请假类型'),null=True,blank=True,default=0)
        AuditExcID=models.IntegerField(_(u'审核状态'),null=True,blank=True,default=0)
        OldAuditExcID=models.IntegerField(_(u'前次审核状态'),null=True,blank=True,default=0)
        OverlapTime=models.IntegerField(_(u'排班时长'),db_column='OverlapTime',null=True,blank=True,default=0)               
        TimeLong=models.IntegerField(_(u'总时长（分钟）'), db_column='TimeLong',null=True,blank=True,default=0)                  
        InScopeTime=models.IntegerField(_(u'有效时长（分钟）'), db_column='InScopeTime',null=True,blank=True,default=0)  
        AttDate=models.DateTimeField(_(u'日期'),db_column='AttDate',null=True,blank=True)
        OverlapWorkDayTail=models.IntegerField( db_column='OverlapWorkDayTail')
        OverlapWorkDay=models.FloatField(_(u'排班工作日'),db_column='OverlapWorkDay',null=True,default=1,blank=True)      
        schindex=models.IntegerField(db_column='schindex',null=True,blank=True,default=0)
        Minsworkday=models.IntegerField(db_column='Minsworkday',null=True,blank=True,default=0)
        Minsworkday1=models.IntegerField(db_column='Minsworkday1',null=True,blank=True,default=0)
        schid=models.IntegerField(db_column='schid',null=True,blank=True,default=0)

        class Admin(CachingModel.Admin):
                default_give_perms=["contenttypes.can_AttCalculate",]
                visible=False
                list_display=('UserID_id','UserID.PIN','UserID.EName','UserID.DeptID','StartTime','EndTime','ExceptionID|AttExceptDesc','InScopeTime')
                #hidden_fields=('AuditExcID','OldAuditExcID','OverlapTime','AttDate','OverlapWorkDayTail','OverlapWorkDay','schindex','Minsworkday','schid')
        class Meta:
                app_label='att'
                db_table='attexception'
                #unique_together = (("UserID","AttDate", "StartTime"),)
