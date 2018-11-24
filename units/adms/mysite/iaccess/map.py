#! /usr/bin/env python
#coding=utf-8
from django.http import HttpResponse
from dbapp.utils import getJSResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from mysite.iclock.iutils import dumps
from traceback import print_exc
from django.utils import simplejson 
import time
import os
from django.utils.translation import ugettext_lazy as _
from models import AccMap, AccMapDoorPos, AccDoor
from mysite.personnel.models import Area

#获取当前用户权限范围内的所有门信息
def get_effective_doors(user):
    aa = user.areaadmin_set.all()
    a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）
    return AccDoor.objects.filter(device__area__pk__in=a_limit).order_by('id')
    #return AccDoor.objects.filter(device__area__pk__in=a_limit).order_by('id').values_list('id', 'device__alias', 'door_no', 'door_name')

#获取当前用户权限范围内的所有地图信息(已含区域上下级处理)
def get_effective_maps(user):
    aa = user.areaadmin_set.all()
    #print '---aa=',aa
    a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）
    #print '---a_limit=',a_limit
    return AccMap.objects.filter(area__pk__in=a_limit).order_by('id')


#列表转换
def apart_from_list(lists, cell_len):
    apart = []
    q = []#临时用

    for index, item in enumerate(lists):
        q.append(item)
        if index % cell_len == cell_len - 1:
            apart.append(q)
            q = []
    return apart



#电子地图
@login_required
def electro_map(request):
    fun_mode = request.GET.get("func", '')
    
    #init map
    if fun_mode == "init_maps":
        #暂不考虑权限控制
        #print '----------get_effective_maps(request.user)=',get_effective_maps(request.user)
        e_maps = get_effective_maps(request.user)
        maps = e_maps.values_list('id', 'map_name', 'width', 'height')#如果有，取（权限范围内，暂不考虑）'map_path'后续自定义路径？
        doors_pos = AccMapDoorPos.objects.filter(map__in=e_maps, map_door__in=get_effective_doors(request.user))#只取有效地图上的。且权限范围内的（防止本来有权限查看的但后来被取消权限）的门
        doors_pos = doors_pos.values_list('map_door__id', 'map_door__device__alias', 'map_door__door_no', 'map_door__door_name', 'id', 'map', 'width', 'left', 'top')#考虑与实时监控兼容，0-3一致，，0为记录id。4, 门id 5,6，7代表地图相关
        #print '-----doors_pos=',doors_pos
        return getJSResponse(smart_str(simplejson.dumps({ 'maps': list(maps), 'doors_pos': list(doors_pos) })))  


    map_pk = request.GET.get("map_pk", 0)#不可能为空
    map_objs = AccMap.objects.filter(pk=map_pk)
    #print '----map_objs=',map_objs
    #print '----map_pk=',map_pk

    #delete the map
    if fun_mode == "del_map":
        try:
            if map_objs:
                map_objs[0].delete()#含删除图片
                return HttpResponse(smart_str({ 'ret': 1 }))
        except:
            return HttpResponse(smart_str({ 'ret': -1 }))
    
    #get the doors 
    if fun_mode == "get_doors":
        doors_left_html = ""
        #暂一个门只能在一个地图上，故已添加包含了系统中所有已添加的（权限范围内）和未添加的
        if map_objs:
            doors_left_qs = get_effective_doors(request.user).filter(map__isnull=True)
            #doors_left = set(doors) - set(doors_added)
            from dbapp.widgets import queryset_render_multiple
            attr_str = 'class="wZBaseZManyToManyField" name="door_group" id="id_door_group"'
            doors_left_html = queryset_render_multiple(doors_left_qs, name="door_group",attr_str=attr_str, data=None, id="id_door_group")
        
        return HttpResponse(doors_left_html)
    
    #and then select some to add on the map 
    if fun_mode == "add_doors":
        doors_id = request.GET.get("doors_add_id", '0')#前端已判空
        doors_id = doors_id.split(",")
        #print '----doors_id=',doors_id#全选时 doors_id= [u'', u'1', u'2']空格需要过滤掉
        if map_objs:
            try:
                for door_id in doors_id:
                    if door_id:
                        door_obj = AccDoor.objects.get(id=int(door_id))
                        pos_obj = AccMapDoorPos(map_door=door_obj, map=map_objs[0])
                        pos_obj.save(force_insert=True, log_msg=False)
                        door_obj.map = map_objs[0]
                        door_obj.save(force_update=True)
                return HttpResponse(smart_str(simplejson.dumps({ 'ret': 1, 'pos_id': pos_obj.id })))
            except:#一旦失败是否需要回滚？
                print_exc()
                return HttpResponse(smart_str({ 'ret': -2 }))
        else:
            return HttpResponse(smart_str({ 'ret': -1 }))#意外情况？
    
    #and then select some to add on the map 
    if fun_mode == "del_door":
        door_id = int(request.GET.get("door_del_id", 0))
        #print '----door_id=',door_id
        try:
            if map_objs:
                pos_obj = AccMapDoorPos.objects.get(map_door__id=door_id)
                pos_obj.map_door.map = None
                pos_obj.map_door.save(force_update=True)
                pos_obj.delete()
                return HttpResponse(smart_str({ 'ret': 1 }))
        except:
            print_exc()
            return HttpResponse(smart_str({ 'ret': -1 }))
        
    if fun_mode == "save_mapdoorpos":
        map_info = request.GET.get("map_array", None)
        pos_info = request.GET.get("pos_array", None)

        map_apart = apart_from_list(map_info.split(","), 3)
        pos_apart = apart_from_list(pos_info.split(","), 4)
        
        #print '----map_apart=',map_apart
        #print '----pos_apart=',pos_apart
        try:
            for map in map_apart:
                #print '-----map[0]=',map[0]
                map_obj = AccMap.objects.get(pk=int(map[0]))
                map_obj.width = float(map[1])
                map_obj.height = float(map[2])
                map_obj.save(force_update=True, log_msg=False)
            for pos in pos_apart:
                #mds_objs = AccMapDoorPos.objects.filter(map_door__id=door_id, map__id=map_id)#长度为0或1
                #记录已经保存过，一定是update
                mds_obj = AccMapDoorPos.objects.get(pk=int(pos[0].split('-')[0]))
                mds_obj.width = float(pos[1])
                mds_obj.left = float(pos[2])
                mds_obj.top = float(pos[3])
                mds_obj.save(force_update=True, log_msg=False)
            return HttpResponse(smart_str({ 'ret': 1 }))
        except:
            print_exc()
            return HttpResponse(smart_str({ 'ret': -1 }))
        