# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from models.model_empchange  import get_empchange_postion
from views import get_dept_tree_data
from models.empwidget import get_widget_for_select_emp
import report
import views
import models

urlpatterns=patterns('mysite.personnel',
    (r'^getempchange_value/(?P<userid>[^/]*)/(?P<num>[^/]*)/$',get_empchange_postion),
    (r'^get_dept_tree_data$', get_dept_tree_data),
    (r'^GenerateEmpFlow/$', report.GenerateEmpFlow),
    (r'^GenerateDeptRoster/$', report.GenerateDeptRoster),
    (r'^GenerateEmpEducation/$', report.GenerateEmpEducation),
    (r'^GenerateEmpCardList/$', report.GenerateEmpCardList),
    (r'^choice_widget_for_select_emp/$',get_widget_for_select_emp),
    (r'^get_children_nodes/$',views.get_children_nodes),
    (r'^getchange/$', views.getchange),
    (r'^getmodeldata/(?P<app_lable>[^/]*)/(?P<model_name>[^/]*)/$',views.funGetModelData),
    (r'^personnel_guide/$',views.fun_personnel),#人员导航
    (r'^select_emp_data/$',views.select_emp_data),
    (r'^select_state/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$', views.select_state),
    (r'^select_city/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$',views.select_city),
    (r'^select_position/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$',views.select_position),
#    (r'^base_data/$',views.base_data_view),
    (r'base_data_page/$',models.basedata.base_data_page),
    (r'country_page/$',models.basedata.base_country_page),
    (r'state_page/$',models.basedata.base_state_page),
    (r'city_page/$',models.basedata.base_city_page),
    (r'national_page/$',models.basedata.base_national_page),
    (r'education_page/$',models.basedata.base_education_page),
    
    #scott meeting...会议系统使用
    (r'select_meeting_emp_data/$',views.select_emp_data2),
    
    (r'^get_issuecard_info/$',views.get_card_info),
)
 
