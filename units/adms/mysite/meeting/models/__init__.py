#! /usr/bin/env python
#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _ #导入国际化模块


from meeting_emp import MeetingEmp
from model_meeting import MeetingEntity
#from mysite.iclock.models.room import Room
from room import Room
from type  import Type 
from meeting_exact import MeetingExact
from meeting_record import OriginalRecord
from meeting_ValidRecord import ValidRecord
from meeting_leave import Leave
from meeting_report import MeetingReport
from meeting_operation import MeetingCalculate
from meeting_operation import MeetingGuide
from detailMeeting import DetailMeeting
from statisticsMeeting import StatisticsMeeting


verbose_name=_(u"会议")       #应用app名称
_menu_index=8                 #在菜单中摆放的位置
def app_options():
    from base.options import SYSPARAM,PERSONAL
    return (
        ('meeting_default_page','meeting/MeetingGuide/', u"%s"%_(u'会议默认页面'), '',PERSONAL,False),
    )


