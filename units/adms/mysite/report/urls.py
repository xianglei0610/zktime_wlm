# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
urlpatterns = patterns('mysite.report',
    (r'^datasources/$','views.get_all_datasources'),
    (r'^get_model_attributes/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$','views.response_model_attributes'),
    (r'^new_report/$','views.new_report'),
    (r'^edit_report/(?P<key>[^/]*)/$','views.edit_report'),
    (r'^browse_file/$','views.browse_report'),
    (r'^download_file/$','views.download_report'),
)
