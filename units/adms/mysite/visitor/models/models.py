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
from mysite.personnel.models import Employee
u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以门设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""

#生成查询的表单
def get_searchform(request, model):
    if hasattr(model.Admin,"query_fields_visitor") and model.Admin.query_fields_visitor:  
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields_visitor))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform

#访客监控
@login_required
def render_visitor_preview_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    
    return render_to_response(VisitorPreviewPage._template,RequestContext(request,{
        "app_label": "visitor",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="visitor"][0][1],
        "menu_focus": "VisitorPreviewPage",
        "current_app": "visitor",
        "has_header": True,#has_header,
        #"searchform": searchform,
        #"model_name": VisitorPreviewPage._model_name,
        "position": VisitorPreviewPage._position,
        "help_model_name": VisitorPreviewPage.__name__
    }))


class VisitorPreviewPage(AppOperation):
    u"""
    访客监控
    """
    verbose_name = _(u'访客监控')
    view = render_visitor_preview_page
    _app_menu = "visitor_preview"
    _menu_index = 10003
    _app_menu = 'visitor'
    #_menu_group = 'acc_report'
    #_model_name = "AccLevelSet" 
    #_parent_model = 'ReportFormPage'
    _template = "Visitor_Preview.html"
    _position = _(u'访客系统 -> 访客监控')
    
    
 
#访客门禁权限组设置 
@login_required 
def render_visitor_level_set_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()    
      
    return render_to_response(VisitorLevelSetPage._template,RequestContext(request,{
        "app_label": "visitor",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="visitor"][0][1],
        "menu_focus": "VisitorLevelSetPage",
        "current_app": "visitor",
        "has_header": True,
        #"searchform": False,
        #"model_name": VisitorLevelSetPage._model_name,
        "position": VisitorLevelSetPage._position,
        "help_model_name": VisitorLevelSetPage.__name__
    }))

    
    
class VisitorLevelSetPage(AppOperation):
    u"""
    访客门禁权限组设置页面
    """
    verbose_name = _(u'访客门禁权限组设置')
    view = render_visitor_level_set_page
    _app_menu = "visitor_level_set"
    _menu_index = 10005
    _app_menu = 'visitor'
    _menu_group = 'visitor_level_set_page'
    _hide_perms = ["can_VisitorLevelSetPage"]
    _template = "Visitor_Level_Set.html"
    _position = _(u'访客系统 -> 访客门禁权限组设置')
    _cancel_perms = [("can_VisitorLevelSetPage")]    
    visible = True



#访客参数设置
@login_required 
def render_visitor_option_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    
    return render_to_response(VisitorOptionPage._template,RequestContext(request,{
        "app_label": "visitor",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="visitor"][0][1],
        "menu_focus": "VisitorOptionPage",
        "current_app": "visitor",
        "has_header": True,#has_header,
        #"searchform": searchform,
        #"model_name": VisitorOptionPage._model_name,
        "position": VisitorOptionPage._position,
        "help_model_name": VisitorOptionPage.__name__
    }))

    
    
class VisitorOptionPage(AppOperation):
    u"""
    访客参数设置页面
    """
    verbose_name = _(u'访客参数设置')
    view = render_visitor_option_page
    _app_menu = "visitor_option"
    _menu_index = 10006
    _app_menu = 'visitor'
    _hide_perms = ["can_VisitorOptionPage"]
    #_model_name = 'Employee'
    _template = "Visitor_Option.html"
    _position = _(u'访客系统 -> 访客参数设置')
    _cancel_perms = [("can_VisitorOptionPage")]    
