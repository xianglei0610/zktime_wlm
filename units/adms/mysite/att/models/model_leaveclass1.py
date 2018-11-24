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
from base.models import CachingModel, Operation


BOOLEANS = ((0, _(u"否")), (1, _(u"是")),)
LEAVE_UNITS = (

    (1, _(u'小时')),
    (2, _(u'分钟')),
    (3, _(u'天')),
)

    ##统计项目表##
class LeaveClass1(CachingModel):
    LeaveID = models.AutoField(primary_key=True, db_column="LeaveID", null=False, editable=False)
    name = models.CharField(_(u'假类名称'), db_column="LeaveName", max_length=20, null=False)
    MinUnit = models.FloatField(_(u'最小单位'), db_column="MinUnit", null=False, default=1, blank=False)
    Unit = models.SmallIntegerField(_(u'单位'), null=False, default=1, blank=False, choices=LEAVE_UNITS)
    RemaindProc = models.SmallIntegerField(_(u'累计后再进行舍入'), null=False, default=1, blank=True, choices=BOOLEANS)
    RemaindCount = models.SmallIntegerField(_(u'按次计算'), null=False, default=1, blank=True, choices=BOOLEANS)
    ReportSymbol = models.CharField(_(u'报表中的表示符号'), max_length=4, null=False, default='_')
    Deduct = models.FloatField(_(u'每一最小单位扣款'), null=False, default=0, blank=False)
    Color = models.IntegerField(_(u'显示颜色'), null=False, default=0, blank=True, editable=False)
    Classify = models.SmallIntegerField(null=False, default=0, blank=True, editable=False)
    LeaveType = models.SmallIntegerField(_(u'假类类型'), null=False, default=0, blank=True)
    Calc = models.TextField(max_length=2048, null=True, editable=False)

    def save(self, *args, **kwargs):
        super(LeaveClass1, self).save()

    class Admin(CachingModel.Admin):
        visible = False
        cache = False
        initial_data = (
            {"LeaveID":1000, "name": u'应到/实到', "MinUnit": 0.5, "Unit": 3, "RemaindProc": 1, "RemaindCount": 0, "ReportSymbol": ' ', "LeaveType": "3"},
            {"LeaveID": 1001, "name": u'迟到', "MinUnit": 10, "Unit": 2, "RemaindProc": 2, "RemaindCount": 1, "ReportSymbol": '>', "LeaveType": "3", "Calc": 'AttItem(minLater)'},
            {"LeaveID": 1002, "name": u'早退', "MinUnit": 10, "Unit": 2, "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": '<', "LeaveType": "3", "Calc": 'AttItem(minEarly)'},
            {"LeaveID": 1003, "name": u'请假', "MinUnit": "1", "Unit": "1", "RemaindProc": "1", "RemaindCount": "1", "ReportSymbol": 'V', "LeaveType": "3", "Calc": 'if((AttItem(LeaveType1)>0) and (AttItem(LeaveType1)<999), "AttItem(LeaveTime1), "0)+if((AttItem(LeaveType2)>0) and (AttItem(LeaveType2)<999), "AttItem(LeaveTime2), "0)+if((AttItem(LeaveType3)>0) and (AttItem(LeaveType3)<999), "AttItem(LeaveTime3), "0)+if((AttItem(LeaveType4)>0) and (AttItem(LeaveType4)<999), "AttItem(LeaveTime4), "0)+if((AttItem(LeaveType5)>0) and (AttItem(LeaveType5)<999), "AttItem(LeaveTime5), "0)'},
            {"LeaveID": 1004, "name": u'旷工', "MinUnit": "0.5", "Unit": "3", "RemaindProc": "1", "RemaindCount": "0", "ReportSymbol": 'A', "LeaveType": "3", "Calc": 'AttItem(MinAbsent)'},
            {"LeaveID": 1005, "name": u'加班', "MinUnit": "1", "Unit": "1", "RemaindProc": "1", "RemaindCount": "1", "ReportSymbol": '+', "LeaveType": "3", "Calc": 'AttItem(MinOverTime)'},
            {"LeaveID": 1008, "name": u'未签到', "MinUnit": "1", "Unit": "4", "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": '[', "LeaveType": "2", "Calc": 'If(AttItem(CheckIn)": null, "If(AttItem(OnDuty)": null, "0, "if(((AttItem(LeaveStart1)": null) or (AttItem(LeaveStart1)>AttItem(OnDuty))) and AttItem(DutyOn), "1, "0)), "0)'},
            {"LeaveID": 1009, "name": u'未签退', "MinUnit": "1", "Unit": "4", "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": ']', "LeaveType": "2", "Calc": 'If(AttItem(CheckOut)": null, "If(AttItem(OffDuty)": null, "0, "if((AttItem(LeaveEnd1)": null) or (AttItem(LeaveEnd1)<AttItem(OffDuty)), "if((AttItem(LeaveEnd2)": null) or (AttItem(LeaveEnd2)<AttItem(OffDuty)), "if(((AttItem(LeaveEnd3)": null) or (AttItem(LeaveEnd3)<AttItem(OffDuty))) and AttItem(DutyOff), "1, "0), "0), "0)), "0)'},

#            {"name": u"%s" % _(u'应到/实到'), "MinUnit": 0.5, "Unit": 3, "RemaindProc": 1, "RemaindCount": 0, "ReportSymbol": ' ', "LeaveType": "3"},
#            {"name": u"%s" % _(u'迟到'), "MinUnit": 10, "Unit": 2, "RemaindProc": 2, "RemaindCount": 1, "ReportSymbol": '>', "LeaveType": "3", "Calc": 'AttItem(minLater)'},
#            {"name": u"%s" % _(u'早退'), "MinUnit": 10, "Unit": 2, "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": '<', "LeaveType": "3", "Calc": 'AttItem(minEarly)'},
#            {"name": u"%s" % _(u'请假'), "MinUnit": "1", "Unit": "1", "RemaindProc": "1", "RemaindCount": "1", "ReportSymbol": 'V', "LeaveType": "3", "Calc": 'if((AttItem(LeaveType1)>0) and (AttItem(LeaveType1)<999), "AttItem(LeaveTime1), "0)+if((AttItem(LeaveType2)>0) and (AttItem(LeaveType2)<999), "AttItem(LeaveTime2), "0)+if((AttItem(LeaveType3)>0) and (AttItem(LeaveType3)<999), "AttItem(LeaveTime3), "0)+if((AttItem(LeaveType4)>0) and (AttItem(LeaveType4)<999), "AttItem(LeaveTime4), "0)+if((AttItem(LeaveType5)>0) and (AttItem(LeaveType5)<999), "AttItem(LeaveTime5), "0)'},
#            {"name": u"%s" % _(u'旷工'), "MinUnit": "0.5", "Unit": "3", "RemaindProc": "1", "RemaindCount": "0", "ReportSymbol": 'A', "LeaveType": "3", "Calc": 'AttItem(MinAbsent)'},
#            {"name": u"%s" % _(u'加班'), "MinUnit": "1", "Unit": "1", "RemaindProc": "1", "RemaindCount": "1", "ReportSymbol": '+', "LeaveType": "3", "Calc": 'AttItem(MinOverTime)'},
#            {"name": u"%s" % _(u'未签到'), "MinUnit": "1", "Unit": "4", "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": '[', "LeaveType": "2", "Calc": 'If(AttItem(CheckIn)": null, "If(AttItem(OnDuty)": null, "0, "if(((AttItem(LeaveStart1)": null) or (AttItem(LeaveStart1)>AttItem(OnDuty))) and AttItem(DutyOn), "1, "0)), "0)'},
#            {"name": u"%s" % _(u'未签退'), "MinUnit": "1", "Unit": "4", "RemaindProc": "2", "RemaindCount": "1", "ReportSymbol": ']', "LeaveType": "2", "Calc": 'If(AttItem(CheckOut)": null, "If(AttItem(OffDuty)": null, "0, "if((AttItem(LeaveEnd1)": null) or (AttItem(LeaveEnd1)<AttItem(OffDuty)), "if((AttItem(LeaveEnd2)": null) or (AttItem(LeaveEnd2)<AttItem(OffDuty)), "if(((AttItem(LeaveEnd3)": null) or (AttItem(LeaveEnd3)<AttItem(OffDuty))) and AttItem(DutyOff), "1, "0), "0), "0)), "0)'},
        )
    class Meta:
        app_label = 'att'
        db_table = 'leaveclass1'
        verbose_name = _(u'统计项目表')
        verbose_name_plural = verbose_name
