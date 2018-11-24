from django.conf.urls.defaults import *
import views     

urlpatterns = patterns('',
   url(r'^$', views.manager),
   url(r'^login/$', views.login),
   url(r'^getDevInfo/$', views.getDevInfo),
   url(r'^loadUrl/$', views.loadUrl),
   url(r'^(?P<fileName>.*)$', views.html),
   )

