#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from mysite.meeting.views import funMeetingCalculate,funMeetingGuide



class MeetingCalculate(AppOperation):
        u'''会议计算与报表'''
        from mysite.meeting.models.meeting_report import MeetingReport
        verbose_name=_(u'会议签到与报表')
        view=funMeetingCalculate
        visible = True
        _app_menu="meeting"
       
        
        _menu_index=10


class MeetingGuide(AppOperation):
        u'''导航'''
        verbose_name=_(u'导航')
        visible = True
        view=funMeetingGuide
        _app_menu ="meeting"
        _menu_index=0
