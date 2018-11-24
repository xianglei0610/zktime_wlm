#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *
import views
import models
import pos_utils
from mysite.personnel.models.empwidget import get_widget_for_select_emp
urlpatterns = patterns('',
#消费系统其它功能
    (r'^consume/$', views.consumeReport),
    (r'^report/$', views.fun_posreport),
    (r'^getdiningroom',views.get_diningroom),
    (r'^posreport/$',views.posreport),#消费统计报表 入口
     (r'^pos_list_report/$',views.pos_list_report),#消费报表 入口
#    (r'^totalreport/$',views.fun_pos_danne),
#    (r'^SettingOp/',views.renderLeftOp),

   
#    (r'^subsidiesreport/$',views.get_subsidiesreport),#补贴明细表
#    (r'^diningcalculatereport/$',views.get_diningcalculatereport),#餐厅统计表
    (r'^DeviceManage/',views.funPosDeviceDataManage),
#    (r'^CarManage/',views.funPosCarManage),
    (r'^posguide/',views.funPosGuide),
    
    (r'^posdatabase/',models.database.render_posform_page),
    (r'^splittimepage/',models.database.render_splittime_page),
    (r'^batchtimepage/',models.database.render_batchtime_Page),
    (r'^diningpage/',models.database.render_dining_page),
    (r'^mealpage/',models.database.render_meal_page),
    (r'^merchandisepage/',models.database.render_merchandise_page),
    (r'^keyvaluepage/',models.database.render_keyvalue_page),
    
#IC消费
    (r'^load_pos_param/',views.funposParamSetting),
    (r'^save_pos_param/',views.funSavePosParamSetting),
    (r'^save_operate_data/',views.funIssueCardSave),
    (r'^save_operate_bak_data/',views.funIssueCardBakSave),
    
    (r'^save_add_card_bak_data/',views.funIssueAddCardBakSave),#发卡funIssueAddCardSave
    (r'^save_issuecard_data/',views.funIssueAddCardSave),
    (r'^valid_card/$',views.funValidCard),
    (r'^save_card_manage/$',views.funSaveCardmanage),
    (r'^change_card_info/$',views.funChangeCardInfo),
    (r'^choice_widget_for_select_emp/$',get_widget_for_select_emp),
    (r'^get_device_redis/$',pos_utils.get_pos_device_redis),
    
#ic消费报表
    (r'^get_ic_list/$',views.get_ic_pos_record),#消费明细表
#    (r'^get_search_form/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$','common_panel.get_search_from'),
  )
