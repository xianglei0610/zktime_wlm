# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
import models
import view

urlpatterns=patterns('mysite.video',
    (r'^GetData/$', view.get_data),#用于前端向server获取数据

    (r'^VideoLinkagePage/$',models.models.render_videolinkage_page),
    (r'^VideoPreviewPage/$',models.models.render_videopreview_page),
    
    (r'^VideoMonitorPage/$',models.models.render_videomonitor_page),
#    (r'^GetData/$', view.get_data),#用于前端向server获取数据
)