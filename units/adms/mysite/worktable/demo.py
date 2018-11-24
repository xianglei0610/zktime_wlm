#!/usr/bin/env python
#coding=utf-8
from django.http import HttpResponse
import datetime
def index(request):
    #print "asdfsdfsdfdfd"
    return HttpResponse("这是一个向后台取数的例子!<br/>当前时间:%s"%(datetime.datetime.now()))
