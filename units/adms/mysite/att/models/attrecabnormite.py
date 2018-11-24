# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
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
from mysite.personnel.models import Employee, EmpForeignKey
from mysite.iclock.models.model_trans import ATTSTATES

#统计结果用表-记录状态表
class attRecAbnormite(models.Model):
    '''
    统计结果详情
    '''
    UserID = EmpForeignKey(verbose_name=_(u'人员'),db_column='userid')
    checktime = models.DateTimeField(_(u'考勤时间'), db_column='checktime')
    CheckType = models.CharField(_(u'考勤状态'),db_column='CheckType', max_length=5,choices=ATTSTATES)
    NewType = models.CharField(_(u'更正状态'), db_column='NewType', max_length=2,null=True,blank=True,choices=ATTSTATES)
    AbNormiteID=models.IntegerField(db_column='AbNormiteID',  null=True,blank=True)
    SchID=models.IntegerField(_(u'时段'),db_column='SchID',  null=True,blank=True)
    OP=models.IntegerField(_(u'操作'),db_column='OP',  null=True,blank=True)
    AttDate=models.DateTimeField(_(u'日期'),db_column='AttDate',null=True,blank=True)

    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    
    class Admin:
        default_give_perms=["contenttypes.can_AttCalculate"]
        sort_fields = ["UserID.PIN"]
        app_menu="att_set"
        api_fields=('UserID.PIN','UserID.EName','checktime','CheckType','NewType')
        list_display=('UserID_id','UserID.PIN','UserID.EName','checktime','CheckType','NewType')
        visible=False
    class Meta:
        app_label='att'
        verbose_name=_(u"统计结果详情")
        db_table='attrecabnormite'
        unique_together = (("UserID","AttDate", "checktime"),)
