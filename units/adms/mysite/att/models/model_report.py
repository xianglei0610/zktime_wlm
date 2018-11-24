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

class AttReport(models.Model):
    ItemName=models.CharField(primary_key=True,max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(User, null=False) 
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.SmallIntegerField(null=True, choices=PUBLISHED, default=0)
    class Admin(CachingModel.Admin):
       menu_group="att_report"
       visible=False
    class Meta:
       app_label='att'
       verbose_name=_(u"考勤报表")
       verbose_name_plural=verbose_name 
    class Calculate(Operation):
           verbose_name=_(u"""统计""")
           def action(self):
              pass
    class CalcResultDetail(Operation):
           verbose_name=_(u"""统计结果详情""")
           def action(self):
              pass
    class EarchDayAttReport(Operation):
           verbose_name=_(u"""每日考勤统计表""")
           def action(self):
              pass
    class ExceptionReport(Operation):
           verbose_name=_(u"""考勤异常表""")
           def action(self):
              pass
    class OtherExceptionReport(Operation):
           verbose_name=_(u"""其它考勤异常表""")
           def action(self):
              pass
    class CalcTotalReport(Operation):
        verbose_name=_(u"""考勤汇总表""")
        def action(self):
          pass
    class OrgBrushRecord(Operation):
       verbose_name=_(u"""原始记录表""")
       def action(self):
          pass
    class CheckExact(Operation):
       verbose_name=_(u"""补签记录表""")
       def action(self):
          pass
    class LeaveTotalReport(Operation):
       verbose_name=_(u"""假类汇总""")
       def action(self):
          pass

    class dataexport(Operation):
            help_text=_(u"数据导出") #导出
            verbose_name=_(u"导出")
            visible=False
            def action(self):
                    pass
