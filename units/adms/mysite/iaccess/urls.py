# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
import models
import view, rtmonitor
import map
from models.models import render_acc_option

urlpatterns=patterns('mysite.iaccess',
    #(r'^media/(?P<path>.*)$', serve, {'document_root': APP_HOME+'/iaccess/media/', 'show_indexes': False}),
    (r'^DoorSetPage/$', models.models.render_doorset_page),
    (r'^EmpLevelSetPage/$', models.models.render_emplevelset_page),
    (r'^EmpLevelByLevelPage/$', models.models.render_emplevelbylevel_page),
    (r'^EmpLevelByEmpPage/$', models.models.render_emplevelbyemp_page),
    (r'^RTMonitorPage/$', models.models.render_rtmonitor_page),
    
    (r'^ReportFormPage/$', models.models.render_reportform_page),
    (r'^AllEventReportPage/$',models.models.render_alleventreport_page),
    (r'^AlarmEventReportPage/$',models.models.render_alarmeventreport_page),
    (r'^EmpLevelReportPage/$',models.models.render_emplevelreport_page),
    
    (r'^DoorMngPage/$',models.models.render_doormng_page),
    (r'^MonitorAllPage/$', models.models.render_monitorall_page),
    (r'^GetRTLog/$', rtmonitor.get_redis_rtlog),
    (r'^MonitorAlarmPage/$', models.models.render_monitoralarm_page),
    (r'^ElectroMapPage/$', models.models.render_electromap_page),#电子地图
    (r'^AccGuidePage/$', models.models.render_acc_guide_page),#门禁导航页面
    
    (r'^GetData/$', view.get_data),#用于前端向server获取数据
    (r'^SearchACPanel/$', view.search_acpanel),#搜索控制器
    (r'^SendDoorData/$', view.send_doors_data),#开关门等
    (r'^CancelAlarm/$', view.cancel_alarm),#确认报警
    (r'^EmpLevelOp/$', view.emp_level_op),
    (r'^MCEGroupEmpOp/$', view.mcegroup_emp_op),#多卡开门人员组中人的操作（删除）
    (r'^FCOpenEmpOp/$', view.fcopen_emp_op),#删除首卡开门的人（不包括人本身）
    (r'^GetDevLog/$', rtmonitor.get_device_monitor),
    (r'^comm_error_msg/$', rtmonitor.comm_error_msg),
    (r'^downdata_progress/$', rtmonitor.downdata_progress),
    (r'^ClearCmdCache/$', rtmonitor.ClearCmdCache),
    (r'^ProcessAccData/$', rtmonitor.process_acc_data), #第三方数据接口
    
    (r'^ElectroMap/$', map.electro_map),#电子地图
    (r'^get_card_number/$', view.get_card_number),#实时获得未注册的卡号
    (r'^check_pwd/$', view.check_pwd),#验证旧密码是否正确
    (r'^download_fingerprint_driver',view.download_fingerprint_driver),
    (r'^AccOption/$', render_acc_option),#设置门禁参数前端页面
    (r'^set_acc_option/$', view.set_acc_option),#设置门禁参数
    (r'^update_visitor_level/$', view.update_visitor_level),#更新访客门禁权限
)