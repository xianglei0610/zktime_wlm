# -*- coding: utf-8 -*-.
from django.utils.translation import ugettext_lazy as _
from base.models import AppOperation
from django.db import models
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from mysite.settings import MEDIA_ROOT
from dbapp.dataviewdb import seachform_for_model
from base import get_all_app_and_models
from django.contrib.auth.decorators import login_required
from dbapp.templatetags.dbapp_tags import HasPerm
from base.crypt import encryption,decryption

u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以门设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""

#生成查询的表单
def get_searchform(model):
    if hasattr(model.Admin,"query_fields_video") and model.Admin.query_fields_video:        
        searchform = seachform_for_model(model, fields=list(model.Admin.query_fields_video))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform

# 视频监控
@login_required
def render_videopreview_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()

    #searchform = get_searchform(AccLevelSet)
#    if searchform:
#        has_header=True          
#    else:
#        has_header=False    
    
    return render_to_response(VideoPreviewPage._template,RequestContext(request,{
        "app_label": "video",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="video"][0][1],
        "menu_focus": "VideoPreviewPage",
        "current_app": "video",
        "has_header": True,#has_header,
        #"searchform": searchform,
        #"model_name": VideoLinkagePage._model_name,
        "position": VideoPreviewPage._position,
        "help_model_name": VideoPreviewPage.__name__
    }))

class VideoPreviewPage(AppOperation):
    u"""
    报表-视频监控
    """
    verbose_name = _(u'视频预览')
    view = render_videopreview_page
    _app_menu = "vid_preview"
    _menu_index = 10001
    _app_menu = 'video'
    #_menu_group = 'acc_report'
    #_model_name = "AccLevelSet" 
    #_parent_model = 'ReportFormPage'
    _template = "Vid_Preview.html"
    _position = _(u'视频 -> 视频预览')
        
# 视频联动记录
@login_required
def render_videolinkage_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()

    #searchform = get_searchform(AccLevelSet)
#    if searchform:
#        has_header=True          
#    else:
#        has_header=False    
    
    return render_to_response(VideoLinkagePage._template,RequestContext(request,{
        "app_label": "video",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="video"][0][1],
        "menu_focus": "VideoLinkagePage",
        "current_app": "video",
        "has_header": True,#has_header,
        #"searchform": searchform,
        #"model_name": VideoLinkagePage._model_name,
        "position": VideoLinkagePage._position,
        "help_model_name": VideoLinkagePage.__name__
    }))

class VideoLinkagePage(AppOperation):
    u"""
    视频联动记录
    """
    verbose_name = _(u'视频联动记录')
    view = render_videolinkage_page
    _app_menu = "vid_linkage"
    _menu_index = 10002
    _app_menu = 'video'
    #_menu_group = 'acc_report'
    #_model_name = "AccLevelSet" 
    #_parent_model = 'ReportFormPage'
    _template = "Vid_Linkage.html"
    _position = _(u'视频 -> 视频联动记录')


def render_videomonitor_page(request):
#    from mysite.iclock.models.model_device import Device
#    from mysite.personnel.models import Area
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    
#    u = request.user
#    aa = u.areaadmin_set.all()
#    a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）
    
#    vod_id = request.REQUEST.get("vodid", "0")
#    ch = request.REQUEST.get("ch", "0")
#    vod_id = 5
    #searchform = get_searchform(AccLevelSet)
#    if searchform:
#        has_header=True          
#    else:
#        has_header=False
#    devices = Device.objects.filter(area__pk__in=a_limit).filter(device_type=4, id=vod_id).order_by('id').values_list('id', 'alias', 'ipaddress', 'ip_port', 'video_login', 'comm_pwd')
    return render_to_response('Vid_Monitor.html',RequestContext(request,{'dbapp_url': dbapp_url, 'videos': "", 'ch': 1}))
