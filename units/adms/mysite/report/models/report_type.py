# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from base.models import CachingModel

class ReportType(CachingModel):
    name=models.CharField(max_length=20,verbose_name=_(u'报表类别名称'),editable=True)
    remark=models.CharField(max_length=300,verbose_name=_(u'备注'),editable=True)
    class Admin(CachingModel.Admin):
        list_display=["name","create_time"]
        menu_index=1
    class Meta:
        verbose_name=_(u'报表类别')
        verbose_name_plural=verbose_name
        app_label='report'
    def __unicode__(self):
        return u"%s"%self.name
    
