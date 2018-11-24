#coding=utf-8
from django.conf.urls.defaults import *

def index(request):
        pass

urlpatterns = patterns('mysite.testapp',
("^/", index)
)

