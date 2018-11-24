#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from base.cached_model import CachingModel,Operation
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

PUBLISHED=(
(0, _(u"不共享")),
(1, _(u"共享读")),
(2, _(u"共享 读/写"))
)

class MeetingReport(models.Model):
    ItemName=models.CharField(primary_key=True,max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(User, null=False) 
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.SmallIntegerField(null=True, choices=PUBLISHED, default=0)
    
    class Admin(CachingModel.Admin):
       menu_group="meeting_report"
       visible=False
    class Meta:
       app_label='meeting'
       verbose_name=_(u"会议签到与报表")
       verbose_name_plural=verbose_name 
    

    