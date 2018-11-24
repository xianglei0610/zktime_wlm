# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
import os
import string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation, ModelOperation
from dbapp.models import BOOLEANS
from base.cached_model import STATUS_PAUSED, STATUS_OK, STATUS_LEAVE

from django import forms
from base.base_code import BaseCode, base_code_by
from dbapp import data_edit
from base.crypt import encryption
from django.core.files.storage import FileSystemStorage
from django.core.files import File


photo_storage = FileSystemStorage(
    location=settings.ADDITION_FILE_ROOT,
    #base_url=settings.APP_HOME+"/file"
)


#性别
GENDER_CHOICES = (
    ('M', _(u'男')),
    ('F', _(u'女')),
)


#来访事由
VISIT_REASON = (
    (1, _(u'商谈业务')),
    (2, _(u'探亲')),
    (3, _(u'社保卡')),
    (4, _(u'军用卡')),     
)

#车类型
CAR_TYPE = (
    (1, _(u'小车')),
    (2, _(u'大巴')),
    (3, _(u'劳斯莱斯')),
)


STATE = (
    (1, _(u'出')),
    (2, _(u'入')),
)

class ReservationManage(CachingModel):
    """
    预约管理
    """
    id = models.AutoField(_(u'预约ID'), primary_key=True, editable=False, null=False)
#    EName = models.CharField(_(u'姓名'), db_column="name", null=True, max_length=24, blank=True, default="")
#    lastname = models.CharField(_(u'姓氏'), max_length=20, null=True, blank=True, editable=True)
    pin = models.CharField(_(u'被访人编号'), max_length=100, null=True, blank=True)#给访客下发权限时使用，用于查询人员表的PIN
    visited_person = models.CharField(_(u'被访人'), null=False, max_length=24, blank=True, default="")
    title = models.CharField(_(u'职务'), max_length=50, null=True, blank=True, choices=base_code_by('TITLE'))
    telephone = models.CharField(_(u'电话'), max_length=20, null=True, blank=True, default='')
    extension_set = models.CharField(_(u'分机号'), max_length=4, null=True, blank=True)
    identity_card = models.CharField(_(u'身份证号码'), max_length=20, null=True, blank=True, default='')
    
    visitor = models.CharField(_(u'来访人'), null=False, max_length=24, blank=True, default="")
    visit_company = models.CharField(_(u'来访单位'), null=False, max_length=24, blank=True, default="")
    visit_reason = models.CharField(_(u'来访事由'), max_length=30, null=True, choices=VISIT_REASON, blank=True)
    come_date = models.DateField(_(u'来访时间'), null=True, blank=True)
  
    
    
    def __unicode__(self):
        return u"%s %s"%(self.pin ,self.visited_person  or "")

    
    
    class Admin(CachingModel.Admin):
        sort_fields = ["come_date"]
        app_menu = "visitor"
        help_text = _(u"如果新增的访客在访客列表中未能显示，请联系管理员！")
        #search_fields = ['pin', 'visited_person', 'visitor']
        list_display = ('pin', 'visited_person', 'title', 'telephone', 'extension_set', 'visitor', 'visit_company', 'visit_reason', 'come_date')
        adv_fields = ['pin', 'visited_person', 'visitor', 'visit_reason', 'come_date']
#        list_filter = ('type', 'parent', 'invalidate')
#        newadded_column = {
#           'parent':'get_parent',
#        }
        
        #import_fields = ['code', 'name', 'parent']
        #default_widgets = {'parent': ZDeptChoiceWidget(attrs={"async_model":"personnel__Department"})}
        query_fields = ['pin', 'visited_person', 'visitor']
        #disabled_perms = ["clear_department"]
        menu_index = 1
        cache = 3600
        position = _(u'访客系统 -> 预约管理')
        #report_fields=['code', 'name', 'parent']

    class Meta:
        app_label = 'visitor'
        db_table = 'reservation_manage'
#        ordering = ('into_date', 'state')
        verbose_name = _(u'预约管理')
        verbose_name_plural = verbose_name



def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, ReservationManage):
       pass
    
data_edit.post_check.connect(DataPostCheck)
