# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from clean_data import get_html_data
urlpatterns = patterns('mysite.worktable',
        (r'^get_search_form/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$','common_panel.get_search_from'),
        (r'^outputEmpStructureImage/$', 'views.outputEmpStructureImage'),
        (r'^outputattrate/$', 'views.outputattrate'),
        (r'^instant_msg/$', 'views.get_instant_msg'),
        (r'^instant_msg/(?P<datakey>[^/]*)/$', 'views.set_msg_read'),
        (r'^test_progress','tests.test_progress'),
        (r'^progress_bar','tests.progress_bar'),
        (r'^get_clear_data_html/$', get_html_data),
        (r'^download_fingerprint_driver','views.download_fingerprint_driver'),
)

