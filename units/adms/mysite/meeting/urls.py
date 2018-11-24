#! /usr/bin/env python
#coding=utf-8
from django.conf.urls.defaults import *
from mysite.meeting.models.meeting_empwidget import get_widget_for_select_emp
import models
import views



#(r'^choice_widget_for_select_meeting/$',get_widget_for_select_meeting),

urlpatterns=patterns('',
    (r'^choice_widget_for_select_emp/$',get_widget_for_select_emp),
    (r'select_meeting_data',views.select_meeting_data),
    (r'^MeetingCalculate/$',views.funMeetingCalculate),
    (r'getRecord/$',views.funGetRecord),#报表获取原始记录
    (r'getValidRecords/$',views.funValidRecords),
    (r'show_meetingAll/$',views.select_meeting),
    (r'show_checkTypeAll/$',views.select_checkType),
#    (r'meetingReCalc/$',views.statiMeetingRec),
    (r'meetingReCalc/$',views.funStatisticsMeetingRecord),
    (r'validRecord/$',views.funValidRecord),
    (r'^MeetingGuide/$',views.funMeetingGuide),
    #(r'^report/$',views.funMReport),#会议考勤统计
)
