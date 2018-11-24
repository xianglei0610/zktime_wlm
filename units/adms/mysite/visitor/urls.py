# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
import models
import view
import visitor_monitor

urlpatterns=patterns('mysite.visitor',
    #(r'^VisitorPreviewPage/$', models.models.render_visitor_preview_page),#用于前端向server获取数据
    #(r'^VisitorLevelSetPage/$', models.models.render_visitor_level_set_page), #访客门禁权限组设置
    (r'^VisitorOptionPage/$', models.models.render_visitor_option_page), #访客参数
#    (r'^ComeRegisterPage/$', models.models.render_come_register_page),#进入登记
#    (r'^LeaveRegisterPage/$', models.models.render_leave_register_page),#离开登记
    
    (r'^ProcessVisitorOption/$', view.process_visitor_option),#处理访客参数
    (r'^VisitorMonitor/$', visitor_monitor.get_visitor_monitor),#访客来访时长监控
    (r'^get_visited_emp/$', view.get_visited_emp),#按被访人编号获取被访人信息
    (r'^get_visitor_pin/$', view.get_visitor_pin),#获取被访人编号
    (r'^get_total_info/$', view.get_total_info),#统计当日进入、离开的次数、人数
    (r'^get_visitor_by_edit/$', view.get_visitor_by_edit),#编辑时填充没有渲染的部分
    (r'^get_visitor_by_add/$', view.get_visitor_by_add),#新增时填充没有渲染的部分
    #(r'^get_photo_save_path/$', view.get_photo_save_path),#获取图片的保存路径
)




