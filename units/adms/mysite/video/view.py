#! /usr/bin/env python
#coding=utf-8
from django.http import HttpResponse
from dbapp.utils import getJSResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from mysite.iaccess.models import AccDoor, AccLinkageIO
from mysite.iclock.iutils import dumps
from mysite.iclock.models.model_device import Device
from mysite.personnel.models import Area
from traceback import print_exc
from ctypes import *
from django.utils import simplejson 
import time
from base.cached_model import SAVETYPE_NEW,SAVETYPE_EDIT
from dbapp.datautils import filterdata_by_user
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from base.crypt import encryption,decryption
from mysite.iclock.models.model_device import DEVICE_VIDEO_SERVER,DEVICE_CAMERA_SERVER

#获取数据返回给前端
@login_required
def get_data(request):
    fun_mode = request.REQUEST.get("func", "")

    if fun_mode == "video":
        type = request.GET.get("type", "") 
        u = request.user
        aa = u.areaadmin_set.all()
        a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）
        #print "a_limit=", a_limit
        if type == 'all_device':
            devices = Device.objects.filter(area__pk__in=a_limit).filter(device_type=2).order_by('id').values_list('id', 'alias')
            videos = Device.objects.filter(area__pk__in=a_limit).filter(device_type=4).order_by('id').values_list('id', 'alias')
            doors = AccDoor.objects.filter(device__area__pk__in=a_limit).order_by('id').values_list('id', 'door_name')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all', 'videos': [device for device in videos], 'devices': [device for device in devices], 'doors': [door for door in doors]})))
        
        if type == 'device':    #通过设备查找相绑定的硬盘录像机
            device_id = request.GET.get("device_id", 0)
            doors = AccDoor.objects.filter(device__area__pk__in=a_limit).filter(device__id=device_id).order_by('id').values_list('id', 'door_name')
            door = [door[0] for door in doors]
            linkages = AccLinkageIO.objects.filter(device__pk__in = [device_id]).filter(in_address_hide__in = door)
            videos=[link.video_linkageio.id for link in linkages]
            devices = Device.objects.filter(area__pk__in=a_limit).filter(id__in=videos).filter(device_type=4).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'device', 'videos': [device for device in devices], 'devices': '', 'doors': [door for door in doors]})))
        
        if type == 'door':
            door_id = request.GET.get("door_id", 0)
            #print "door_id=", door_id
            doors = AccDoor.objects.filter(device__area__pk__in=a_limit).filter(id=door_id)
            #print "doors=", doors, "=", doors[0].device
            videos = []
            if doors:
                linkages = AccLinkageIO.objects.filter(device = doors[0].device).filter(in_address_hide = doors[0].door_no)
                videos=[link.video_linkageio.id for link in linkages]
            devices = Device.objects.filter(area__pk__in=a_limit).filter(id__in=videos).filter(device_type=4).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
#            print "devices=", devices
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'door', 'videos': [device for device in devices], 'devices': '', 'doors': ""})))
        
        if type == 'video':
            devices = Device.objects.filter(area__pk__in=a_limit).filter(device_type=DEVICE_VIDEO_SERVER).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'allvideo', 'videos': [device for device in devices], 'devices': ''})))            
        
        if type == 'camera':
            devices = Device.objects.filter(area__pk__in=a_limit).filter(device_type=DEVICE_CAMERA_SERVER).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'allvideo', 'videos': [device for device in devices], 'devices': ''})))            
        
        if type == 'videoserver':
            device_id = request.GET.get("server_id", 0)
            devices = Device.objects.filter(area__pk__in=a_limit).filter(device_type__in=[DEVICE_VIDEO_SERVER,DEVICE_CAMERA_SERVER], id=device_id).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
            #devices[0][5] = devices[0][5] and decrypt(devices[0][5]) or ""
            device=[devices[0][0], devices[0][1], devices[0][2], devices[0][3], devices[0][4], devices[0][5] and decryption(devices[0][5]) or ""];
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'video', 'videos': '', 'devices': device})))
