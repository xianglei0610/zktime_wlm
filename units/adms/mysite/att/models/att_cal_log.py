#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

class att_autocal_log(models.Model):
        cal_date = models.DateField(_(u'计算日期'), db_column='cal_date')
        cal_time = models.DateTimeField(_(u'统计时间'), db_column='cal_time',null=True)
        
        def __unicode__(self):
            return "<day:%s,cal_time:%s>"%(self.cal_date,self.cal_time)
        class Meta:
                app_label='iclock'
                verbose_name = _(u"考勤计算日志")
                verbose_name_plural = verbose_name
                db_table = 'att_autocal_log'
                unique_together = (("cal_date"),)

        class Admin:
                sort_fields=["-cal_date",]
                visible = False
                read_only=True
                list_display=('cal_date','cal_time',)
                search_fields=('cal_date',)
                tstart_end_search={
                    "cal_date":[_(u"起始时间"),_(u"结束时间")]
                }
                