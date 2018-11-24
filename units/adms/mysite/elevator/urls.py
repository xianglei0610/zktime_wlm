# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
import models
#import view


urlpatterns=patterns('mysite.elevator',
    (r'^FloorSetPage/$', models.models.render_floorset_page),
    (r'^EmpElevatorLevelSetPage/$', models.models.render_empelevatorlevelset_page),
    (r'^EmpElevtorLevelByLevelPage/$', models.models.render_empelevatorlevelbylevel_page),
    (r'^EmpElevatorLevelByEmpPage/$', models.models.render_empelevatorlevelbyemp_page),
    (r'^ElevatorLevelSet/$', models.models.render_floorlevelset_page),
    (r'^ElevatorTimesegSetPage/$', models.models.render_elevatortimeseg_page),
    
    
    (r'^FloorMngPage/$',models.models.render_floormng_page),
    #(r'^GetData/$', view.get_data),#用于前端向server获取数据
    #(r'^EmpLevelOp/$', view.emp_level_op),
)