#coding=utf-8

from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse  
from mysite import settings
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 

def html(request,fileName):
    return render_to_response("manager/%s"%fileName, RequestContext(request, {}),);

def getDevInfo(request):
    from mysite.iclock.models.model_device import Device,DEVICE_TIME_RECORDER
    device_type =  request.REQUEST.get("device_type","")
    if not device_type:
        device_type = DEVICE_TIME_RECORDER
    devs= Device.objects.filter(device_type__exact= device_type)
    devs_list = [[dev.sn,dev.alias,dev.ipaddress] for dev in devs]
    ret = {}
    ret["data"] = devs_list
    return getJSResponse(smart_str(dumps(ret)))

def manager(request):
    return render_to_response("manager/manager.html", RequestContext(request, {}),);

def login(request):
    uname =  request.REQUEST.get("username")
    pwd =  request.REQUEST.get("password")
    ret = " "
    if uname == "admin" and pwd =="zkeco2013" :
        ret = "OK"
    return HttpResponse(u"%s"%ret)

def loadUrl(request):
    return render_to_response("manager/manager_main.html", RequestContext(request, {}),);