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
from base.cached_model import CachingModel
from base.operation import Operation


class attShifts(models.Model):
    UserID = EmpForeignKey(verbose_name=_(u'人员'),db_column='userid',null=False)
    SchIndex=models.IntegerField(db_column='SchIndex',  null=True,blank=True)
    AutoSch=models.SmallIntegerField(db_column='AutoSch',null=True,default=0,editable=False)
    AttDate = models.DateTimeField(_(u'日期'), db_column='AttDate')
    #SchId=models.IntegerField(_('SchName'),db_column='SchId',  null=True,blank=True)
    SchId=models.ForeignKey("SchClass", verbose_name=_(u'时段名称'), db_column='SchId', null=True,default=-1,blank=True)

    ClockInTime = models.DateTimeField(_(u'上班时间'), db_column='ClockInTime')
    ClockOutTime = models.DateTimeField(_(u'下班时间'), db_column='ClockOutTime')
    StartTime = models.DateTimeField(_(u'签到时间'), db_column='StartTime',null=True,blank=True)
    EndTime = models.DateTimeField(_(u'签退时间'), db_column='EndTime',null=True,blank=True)
    WorkDay=models.FloatField(_(u'应到'),db_column='WorkDay',null=True,blank=True)
    RealWorkDay=models.FloatField(_(u'实到'),db_column='RealWorkDay',null=True,default=0,blank=True)
    NoIn=models.SmallIntegerField(_(u'未签到'),db_column='NoIn',null=True,blank=True)
    NoOut=models.SmallIntegerField(_(u'未签退'),db_column='NoOut',null=True,blank=True)
    Late = models.FloatField(_(u'迟到'), db_column='Late',null=True,blank=True)
    Early = models.FloatField(_(u'早退'), db_column='Early',null=True,blank=True)
    Absent = models.FloatField(_(u'旷工'), db_column='Absent',null=True,blank=True)
    LateCount = models.IntegerField(_(u'迟到次数'),null=True,blank=True)
    EarlyCount = models.IntegerField(_(u'早退次数'),null=True,blank=True)
    AbsentCount = models.IntegerField(_(u'旷工次数'),null=True,blank=True)
    OverTime = models.FloatField(_(u'加班时间'), db_column='OverTime',null=True,blank=True)
    OverTime_des = models.CharField(_(u'加班时间'), db_column='OverTime_des',max_length=100,null=True,blank=True)
    WorkTime = models.IntegerField(_(u'出勤时长'), db_column='WorkTime',null=True,blank=True)
    ExceptionID=models.IntegerField(_(u'例外情况'),db_column='ExceptionID',  null=True,blank=True)
    Symbol = models.CharField(_(u'符号'), db_column='Symbol', max_length=50,null=True,blank=True)
    MustIn=models.SmallIntegerField(_(u'应签到'),db_column='MustIn',null=True,blank=True)
    MustOut=models.SmallIntegerField(_(u'应签退'),db_column='MustOut',null=True,blank=True)
    OverTime1=models.IntegerField(_(u'加班签到'),db_column='OverTime1',  null=True,blank=True)
    WorkMins = models.IntegerField(_(u'工作分钟'), db_column='WorkMins',null=True,blank=True)
    SSpeDayNormal=models.FloatField(_(u'平日'),db_column='SSpeDayNormal',null=True,blank=True)
    SSpeDayWeekend=models.FloatField(_(u'休息日'),db_column='SSpeDayWeekend',null=True,blank=True)
    SSpeDayHoliday=models.FloatField(_(u'节假日'),db_column='SSpeDayHoliday',null=True,blank=True)
    AttTime = models.IntegerField(_(u'时段时间'), db_column='AttTime',null=True,blank=True)
    SSpeDayNormalOT=models.FloatField(_(u'平日加班'),db_column='SSpeDayNormalOT',null=True,blank=True)
    SSpeDayWeekendOT=models.FloatField(_(u'休息日加班'),db_column='SSpeDayWeekendOT',null=True,blank=True)
    SSpeDayHolidayOT=models.FloatField(_(u'节假日加班'),db_column='SSpeDayHolidayOT',null=True,blank=True)
    AbsentMins=models.IntegerField(_(u'旷工时间(分钟)'),db_column='AbsentMins',  null=True,blank=True)
    AttChkTime = models.CharField(db_column='AttChkTime', max_length=10,null=True,blank=True)
    AbsentR=models.FloatField(_(u'旷工'),db_column='AbsentR',null=True,blank=True)
    ScheduleName = models.CharField(db_column='ScheduleName', max_length=20,null=True,blank=True)
    IsConfirm=models.SmallIntegerField(db_column='IsConfirm',null=True,blank=True)
    IsRead=models.SmallIntegerField(db_column='IsRead',null=True,blank=True)
    Exception=models.CharField(_(u'例外情况明细'), max_length=100,null=True,blank=True)
    def __unicode__(self):
        return unicode(u"%s"%(self.UserID))
    def get_ExceptionID(self):
        '''例外情况'''
        import datetime
        from mysite.att.models import LeaveClass,AttException
        from mysite.iclock.datas import NormalAttValue
        if settings.ATT_CALCULATE_NEW:
            from mysite.att.report_utils import NormalAttValue
        try:
            if self.Exception:
                t=[long(i) for i in self.Exception.split(",")]
                
                ex=AttException.objects.filter(UserID=self.UserID,pk__in=t)
            else:
                ex=""
            
            if ex:
                
                val={}
                for e  in ex:
                   l=LeaveClass.objects.get(pk=e.ExceptionID)
                   k=u"%s"%l.LeaveName
                   #print "e.InScopeTime:%s"%e.InScopeTime
                   ad=attShifts.objects.filter(AttDate=self.AttDate,UserID=self.UserID) 
                   atttime=0
                   for a  in ad:
                        atttime=atttime+a.AttTime
                   #print "atttime:%s"%atttime
                   if not val.has_key( k):
                      
                      val[k]=NormalAttValue(e.InScopeTime,l.MinUnit,l.Unit,l.RemaindProc,1,atttime)
                   else:

                      val[k]=float(val[k])+float(NormalAttValue(e.InScopeTime,l.MinUnit,l.Unit,l.RemaindProc,1,atttime))
                   #print "val[k]:%s"%val[k]
                return ";".join([u"%s:%s"%(k,v) for k,v in val.items()])
            else:
                return ""
        except:
            import traceback;traceback.print_exc();
    class Admin(CachingModel.Admin):
        default_give_perms=["contenttypes.can_AttCalculate",]
        sort_fields = ["UserID.PIN"]
        visible=False
        list_display=('UserID.pk','UserID.DeptID.code','UserID.DeptID.name','UserID.PIN','UserID.EName','AttDate|format_date','SchId','ClockInTime|format_shorttime','ClockOutTime|format_shorttime',
                      'StartTime','EndTime','WorkDay','RealWorkDay','MustIn','MustOut','NoIn','NoOut','Late','Early','AbsentR',
                      'WorkTime','get_ExceptionID','OverTime_des','WorkMins','SSpeDayNormal|format_int','SSpeDayWeekend|format_int',
                      'SSpeDayHoliday|format_int','AttTime','SSpeDayNormalOT',
                      'SSpeDayWeekendOT','SSpeDayHolidayOT'
                      )
        if settings.ATT_CALCULATE_NEW:
            list_display=('UserID.pk','UserID.DeptID.code','UserID.DeptID.name','UserID.PIN','UserID.EName','AttDate|format_date','SchId','ClockInTime|format_shorttime','ClockOutTime|format_shorttime',
                          'StartTime|format_shorttime','EndTime|format_shorttime','WorkDay','RealWorkDay','MustIn','MustOut','NoIn','NoOut','Late','Early','AbsentR',
                          'WorkTime','get_ExceptionID','OverTime_des','AttTime','SSpeDayNormalOT',
                          'SSpeDayWeekendOT','SSpeDayHolidayOT'
                          )
        #newadded_column = { 'ExceptionID':'get_ExceptionID'}
    class Meta:
        app_label='att'
        db_table='attshifts'
        verbose_name=_(u'考勤明细表')
        unique_together = (("UserID","AttDate", "SchId","StartTime"),)
