#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from base.cached_model import CachingModel,Operation
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from mysite.utils import get_option
PUBLISHED=(
(0, _(u"不共享")),
(1, _(u"共享读")),
(2, _(u"共享读写")),
)
def show_visible():
    return False
    if settings.APP_CONFIG.language.language!='zh-cn':
        return False
    else:
        if get_option("ATT"):
            return True
        else:
            return False

class EmpItemDefine(models.Model):
    ItemName=models.CharField(primary_key=True,max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(User, null=False) 
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.SmallIntegerField(null=True, choices=PUBLISHED, default=0)

    class Admin(CachingModel.Admin):
       visible =show_visible() #暂只有考勤使用
       disabled_perms=["add_empitemdefine","change_empitemdefine","delete_empitemdefine"]
    
    class Meta:
       app_label='personnel'
       verbose_name=_(u"人事报表")
       verbose_name_plural=verbose_name
       db_table = 'empitemdefine'
    class dataexport(Operation):
        help_text=_(u"数据导出") #导出
        verbose_name=_(u"导出")
        visible=False
        def action(self):
                pass
    class EmpFlowReport(Operation):
           verbose_name=_(u"""人员流动表""")
           def action(self):
              pass
    class DeptRosterReport(Operation):
           verbose_name=_(u"""部门花名册""")
           def action(self):
              pass
    class EmpEducationReport(Operation):
           verbose_name=_(u"""学历构成分析表""")
           def action(self):
              pass
    class EmpCardReport(Operation):
           verbose_name=_(u"""人员卡片清单""")
           def action(self):
              pass
