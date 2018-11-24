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

from base.cached_model import CachingModel
from base.operation import Operation

    ##系统参数表##
class AttParam(CachingModel):
    ParaName=models.CharField(_(u'考勤规则参数名称'),primary_key=True,max_length=20,null=False)
    ParaType=models.CharField(_(u'考勤规则参数类型'),max_length=2,null=True)
    ParaValue=models.CharField(_(u'考勤规则参数值'),max_length=100,null=False)
    class Admin(CachingModel.Admin):
        disabled_perms=['add_attparam','dataexport_attparam','dataimport_attparam','delete_attparam']
        cancel_perms=[("change_attparam","browse_attparam"),]
        hide_perms=["browse_attparam"]
        menu_index=9
        cache=False
        @staticmethod
        def initial_data():
            if AttParam.objects.all().count()==0:
                AttParam(ParaName='MinsEarly',ParaValue="5").save()
                AttParam(ParaName='MinsLate',ParaValue="10").save()
                AttParam(ParaName='MinsNoBreakIn',ParaValue="60").save()
                AttParam(ParaName='MinsNoBreakOut',ParaValue="60").save()
                AttParam(ParaName='MinsNoIn',ParaValue="60").save()
                AttParam(ParaName='MinsNoLeave',ParaValue="60").save()
                AttParam(ParaName='MinsNotOverTime',ParaValue="60").save()
                AttParam(ParaName='MinsWorkDay',ParaValue="420").save()
                AttParam(ParaName='NoBreakIn',ParaValue="1012").save()
                AttParam(ParaName='NoBreakOut',ParaValue="1012").save()
                AttParam(ParaName='NoIn',ParaValue="1001").save()
                AttParam(ParaName='NoLeave',ParaValue="1002").save()
                AttParam(ParaName='OutOverTime',ParaValue="0").save()
                AttParam(ParaName='TwoDay',ParaValue="0").save()
                AttParam(ParaName='CheckInColor',ParaValue="16777151").save()
                AttParam(ParaName='CheckOutColor',ParaValue="12910591").save()
                AttParam(ParaName='DBVersion',ParaValue="167").save()
                AttParam(ParaName='InstallDate',ParaValue=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).save()
                AttParam(ParaName='ADMSDBVersion',ParaValue="102").save()
    def __unicode__(self):
        return unicode(u"%s"%(self.ParaName))    
    class Meta:
        app_label='att'
        db_table = 'attparam'
        verbose_name=_(u'考勤参数')
        verbose_name_plural=verbose_name
