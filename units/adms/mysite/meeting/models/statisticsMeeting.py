#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from model_meeting import MeetingEntity,MeetingForeignKey

class StatisticsMeeting(CachingModel):
    id = models.AutoField(db_column="id", primary_key=True)
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'))
    dueMeetingEmpCount = models.IntegerField(verbose_name=_(u'应到人数'),null=True,blank=True)
    arrivalMeetingEmpCount = models.IntegerField(verbose_name=_(u'实到人数'),null=True,blank=True)
    nonArrivalMeetingEmpCount = models.IntegerField(verbose_name=_(u'未到人数'),null=True,blank=True)    
    vacateMeetingEmpCount = models.IntegerField(verbose_name=_(u'请假人数'),null=True,blank=True)
    absentMeetingEmpCount = models.IntegerField(verbose_name=_(u'缺席人数'),null=True,blank=True)
    lateEmpCount = models.IntegerField(verbose_name=_(u'迟到人数'),null=True,blank=True)
    leaveEarlyEmpCount = models.IntegerField(verbose_name=_(u'早退人数'),null=True,blank=True)
    unCheckInCount = models.IntegerField(verbose_name=_(u'未签到人数'),null=True,blank=True)
    unCheckOutCount = models.IntegerField(verbose_name=_(u'未签退人数'),null=True,blank=True)
    
    def __unicode__(self):
        return '%s %s' %(self.meetingID.nameMeeting,self.dueMeetingEmpCount)
    

    class Admin(CachingModel.Admin):
        visible=False
        default_give_perms=["contenttypes.can_MeetingCalculate"]
        sort_fields = ['meetingID.numberMeeting','dueMeetingEmpCount','arrivalMeetingEmpCount']
        list_display = ['meetingID.numberMeeting','meetingID.nameMeeting','dueMeetingEmpCount','arrivalMeetingEmpCount','nonArrivalMeetingEmpCount','vacateMeetingEmpCount','absentMeetingEmpCount',
                        'lateEmpCount','leaveEarlyEmpCount','unCheckInCount','unCheckOutCount']
        app_menu="meeting"
        menu_group = 'meeting'
        menu_index=7

    class Meta:
        app_label='meeting'
        verbose_name = _(u"会议统计汇总表")
        verbose_name_plural = verbose_name
        
