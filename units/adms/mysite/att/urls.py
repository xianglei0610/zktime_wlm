# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
import models
from mysite.personnel.models.empwidget import get_widget_for_select_emp
import views
from mysite.att.models.nomodelview import getData
from mysite.att.models.schclass import getSchClass
from report_view import attRecAbnormite_report,attShifts_report
urlpatterns=patterns('mysite.att',
(r'^getallexcept/$',views.funGetAllExcept_fast),
(r'^tmpshifts/$',views.funTmpShifts),
(r'^FetchSchPlan/$',views.funFetchSchPlan),
(r'^assignedShifts/$',views.funAssignedShifts),
(r'^deleteEmployeeShift/$',views.funDeleteEmployeeShift),
(r'^worktimezone/$',views.funWorkTimeZone),
(r'^getshifts/$',views.funGetShifts),
(r'^attrule/$',views.funAttrule),
(r'^shift_detail/$',views.funShift_detail),
(r'^deleteShiftTime/$',views.funDeleteShiftTime),
(r'^deleteAllShiftTime/$',views.funDeleteAllShiftTime),
(r'^addShiftTimeTable/$',views.funAddShiftTimeTable),

(r'^getschclass/$',views.funGetSchclass),
(r'^AttCalculate/$',views.funAttCalculate),
(r'^AttReCalc/$',views.funAttReCalculate),
(r'^AttParamSetting/$',views.funAttParamSetting),#考勤参数
(r'^SaveAttParamSetting/$',views.SaveAttParamSetting),#考勤参数保存
(r'^Forget/$',views.funForget),
(r'^AttUserOfRun/$',views.funAttUerOfRun),
(r'^SaveForget/$',views.SaveForget),
(r'^newgetSchClass/$',getSchClass),
(r'^choice_widget_for_select_emp/$',get_widget_for_select_emp),
(r'^getmodeldata/(?P<app_lable>[^/]*)/(?P<model_name>[^/]*)/$',views.funGetModelData),
(r'^getData/$', getData),
(r'^DeviceUserManage/$',views.funAttDeviceUserManage),
(r'^DeviceDataManage/$',views.funAttDeviceDataManage),
(r'^DailyCalcReport/$', views.fundailycalcReport),#每日考勤统计表
(r'^CalcReport/$', views.funCalcReport),
(r'^CalcLeaveReport/$', views.funCalcLeaveReport),
(r'^GenerateEmpPunchCard/$', views.GenerateEmpPunchCard),
(r'^attRecAbnormite_report/$', attRecAbnormite_report),    #统计结果详情
(r'^attShifts_report/$', attShifts_report),    #考勤明细表
(r'^lereport/$', views.funLEReport),    #汇总最早与最晚
(r'^AttGuide/$',views.funAttGuide),
(r'^ycreport/$', views.funYCReport),
(r'^CardTimesReport', views.funCardTimesReport),
(r'^(?P<model_name>[^/]*)/select_all_emp_data/$',views.select_all_emp_data),
(r'^import_u_data', views.funImportUdata),
(r'^import_self_data', views.funImportSelfData),
)


