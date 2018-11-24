from django.conf.urls.defaults import *
import views     

urlpatterns = patterns('',
   url(r'^list/(?P<tmp_name>[^/]*)/$', views.api_list),
   url(r'^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$', views.api),
   url(r'^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/count$', views.api_count),
   url(r'^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/(?P<data_key>[^/]*)/', views.api),
   )

