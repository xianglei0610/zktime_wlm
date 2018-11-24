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

from model_splittime import SplitTime
from model_batchtime import BatchTime
from mysite.iclock.models.model_dininghall import Dininghall
from mysite.personnel.models.model_meal import Meal
from model_merchandise import Merchandise
from django.contrib.contenttypes.models import ContentType
from model_keyvalue import KeyValue
from mysite.utils import get_option

u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以门设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""

#生成查询的表单
def get_searchform(request, model):
    if hasattr(model.Admin,"query_fields_Pos") and model.Admin.query_fields_Pos:        
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields_Pos))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform




#基本资料视图
@login_required
def render_posform_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    if HasPerm(request.user, 'contenttypes.can_SplitTimePage'):
        try:
           ct=ContentType.objects.get_for_model(SplitTime)
           log_search = "content_type__id=%s"%ct.pk
        except: 
           log_search =""
        model_name = SplitTimePage._model_name
        template = SplitTimePage._template
        position = SplitTimePage._position
        searchform = get_searchform(request, SplitTime)
        if get_option("POS_IC"):
            help_model_name = "ic_splittimepage"
        else:
            help_model_name = SplitTimePage.__name__
    elif HasPerm(request.user, 'contenttypes.can_BatchTimePage'):
        model_name = BatchTimePage._model_name
        template = BatchTimePage._template
        position = BatchTimePage._position
        searchform = get_searchform(request, BatchTime)
        if get_option("POS_IC"):
            help_model_name = "ic_batchtimepage"
        else:
            help_model_name = BatchTimePage.__name__
    elif HasPerm(request.user, 'contenttypes.can_DiningPage'):
        model_name = DiningPage._model_name
        template = DiningPage._template
        position = DiningPage._position
        searchform = get_searchform(request, Dininghall)
        if get_option("POS_IC"):
            help_model_name = "ic_diningpage"
        else:
            help_model_name = DiningPage.__name__
        
    elif HasPerm(request.user, 'contenttypes.can_MealPage'):
        model_name = MealPage._model_name
        template = MealPage._template
        position = MealPage._position
        searchform = get_searchform(request, Meal)
        help_model_name = MealPage.__name__
        if get_option("POS_IC"):
            help_model_name = "ic_mealpage"
        else:
            help_model_name = MealPage.__name__
        
    elif HasPerm(request.user, 'contenttypes.can_MerchandisePage'):
        model_name = MerchandisePage._model_name
        template = MerchandisePage._template
        position = MerchandisePage._position
        searchform = get_searchform(request, Merchandise)
        help_model_name = MerchandisePage.__name__
        if get_option("POS_IC"):
            help_model_name = "ic_merchandisepage"
        else:
            help_model_name = MerchandisePage.__name__
        
    elif HasPerm(request.user, 'contenttypes.can_KeyValuePage'):
        model_name = KeyValuePage._model_name
        template = KeyValuePage._template
        position = KeyValuePage._position
        searchform = get_searchform(request, KeyValue)
        help_model_name = KeyValuePage.__name__
        if get_option("POS_IC"):
            help_model_name = "ic_keyvaluepage"
        else:
            help_model_name = KeyValuePage.__name__
    else:
        template = "pos_informaform.html"
        position = ""
        searchform = ""
        help_model_name = ""
        log_search = ""
    if searchform:
        has_header = True          
    else:
        has_header = False

    return render_to_response(template, RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
#        "model_name": model_name,
        "current_app": "pos",
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name,
        "log_search" : log_search 
    }))    
    

class PosFormPage(AppOperation):
    u"""
    基本资料菜单
    """
    verbose_name = _(u'基本资料')
    view = render_posform_page
    _app_menu = "pos"
    _menu_index = 1 
#    _select_related_perms = {"can_SplitTimePage":"browse_SplitTimePage.dataexport_accrtmonitor.opclearrtlogs_accrtmonitor.opclearabnormitylogs_accrtmonitor.can_PosFormPage"}
#    add_model_permission=[PosFormPage,]
#    _cancel_perms=[
#            ("can_SplitTimePage.browse_accrtmonitor","dataexport_accrtmonitor"),
#            ("can_BatchTimePage.can_AlarmEventReportPage","browse_accrtmonitor"),
#            ("can_AllEventReportPage.can_AlarmEventReportPage","opclearrtlogs_accrtmonitor"),
#            ("can_AllEventReportPage.can_AlarmEventReportPage","opclearabnormitylogs_accrtmonitor"),
#            ("can_AllEventReportPage.can_AlarmEventReportPage.can_EmpLevelReportPage","can_PosFormPage")
#    ]
#    _disabled_perms = ['clear_accrtmonitor', 'dataimport_accrtmonitor', 'add_accrtmonitor', 'view_accrtmonitor', 'clear_accrtmonitor', 'change_accrtmonitor', 'delete_accrtmonitor']#只保留浏览、导出、清空权限
#    _hide_perms = ['can_PosFormPage', 'can_AllEventReportPage', 'browse_accrtmonitor', 'dataexport_accrtmonitor', 'opclearrtlogs_accrtmonitor', 'opclearabnormitylogs_accrtmonitor']
    
    
# 基本资料--分段定值
@login_required
def render_splittime_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, SplitTime)
    if searchform:
        has_header=True          
    else:
        has_header=False   
    try:
       ct=ContentType.objects.get_for_model(SplitTime)
       log_search = "content_type__id=%s"%ct.pk
    except: 
       log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_splittimepage"
    else:
        help_model_name = SplitTimePage.__name__

    return render_to_response(SplitTimePage._template, RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "model_name": SplitTimePage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": SplitTimePage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search      
    }))    

class SplitTimePage(AppOperation):
    u"""
    基本资料-分段定值
    """
    verbose_name = _(u'分段定值')
    view = render_splittime_page
    #_app_menu = "acc_report"
    _menu_index = 100061
    _app_menu = 'pos'
    _menu_group = 'pos'
    _model_name = "SplitTime"
    _template = "Pos_SplitTime.html"
    _position = _(u'消费 -> 基本资料 -> 分段定值')
    
    _parent_model = 'PosFormPage'
    add_model_permission=[SplitTime]
    _disabled_perms = ["delete_splittime","add_splittime"]
 
    
 #消费-消费时间段设置
@login_required
def render_batchtime_Page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, BatchTime)
    if searchform:
        has_header=True          
    else:
        has_header=False  
    
    try:
        ct=ContentType.objects.get_for_model(BatchTime)
        log_search = "content_type__id=%s"%ct.pk
    except: 
        log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_batchtimepage"
    else:
        help_model_name = BatchTimePage.__name__
    
    return render_to_response(BatchTimePage._template,RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "model_name": BatchTimePage._model_name,
        "has_header": has_header,
        "searchform": searchform,
        "position": BatchTimePage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search
    }))
    
class BatchTimePage(AppOperation):
    u"""
    消费-消费时间段设置
    """
    verbose_name = _(u'消费时间段设置')
    view = render_batchtime_Page
    #_app_menu = "acc_report"
    _menu_index = 100062
    _app_menu = 'pos'
    _model_name = "BatchTime"
    _menu_group = 'pos'
    _template = "Pos_BatchTime.html"
    _position = _(u'消费 -> 基本资料 -> 消费时间段设置')

    _parent_model = 'PosFormPage'
    
#    _select_related_perms={
#                 "can_BatchTimePage":"change_batchtime",
#        }
#    
    add_model_permission=[BatchTime]
    _disabled_perms = ["delete_batchtime","add_batchtime"]
# 餐厅资料
@login_required
def render_dining_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    searchform = get_searchform(request, Dininghall)
    if searchform:
        has_header=True          
    else:
        has_header=False  
    try:
          ct=ContentType.objects.get_for_model(Dininghall)
          log_search = "content_type__id=%s"%ct.pk
    except: 
          log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_diningpage"
    else:
        help_model_name = DiningPage.__name__
    
    return render_to_response(DiningPage._template,RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "has_header": has_header,
        "searchform": searchform,
        "model_name": DiningPage._model_name,
        "position": DiningPage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search
    })) 

class DiningPage(AppOperation):
    u"""
    基本资料-餐厅资料
    """
    verbose_name = _(u'餐厅资料')
    view = render_dining_page
    _menu_index = 100063
    _app_menu = 'pos'
    _menu_group = 'pos'
    _model_name = "Dininghall" 
    _parent_model = "PosFormPage"
    _template = "Pos_Dininghall.html"
    _position = _(u'消费 -> 基本资料 -> 餐厅资料') 
    add_model_permission=[Dininghall]
#餐别资料
@login_required
def render_meal_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    searchform = get_searchform(request, Meal)
    if searchform:
        has_header=True          
    else:
        has_header=False  
  
    try:
          ct=ContentType.objects.get_for_model(Meal)
          log_search = "content_type__id=%s"%ct.pk
    except: 
          log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_mealpage"
    else:
        help_model_name = MealPage.__name__
    
    return render_to_response(MealPage._template,RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "has_header": has_header,
        "searchform": searchform,
        "model_name": MealPage._model_name,
        "position": MealPage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search
    })) 

class MealPage(AppOperation):
    u"""
    基本资料-餐厅资料
    """
    verbose_name = _(u'餐别资料')
    view = render_meal_page
    _menu_index = 100064
    _app_menu = 'pos'
    _menu_group = 'pos'
    _model_name = "Meal" 
    _parent_model = "PosFormPage"
    _template = "Pos_Meal.html"
    _position = _(u'消费 -> 基本资料 -> 餐别资料') 
    add_model_permission=[Meal]
    _disabled_perms = ["delete_meal","add_meal"]


#商品资料
@login_required
def render_merchandise_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    searchform = get_searchform(request, Merchandise)
    if searchform:
        has_header=True          
    else:
        has_header=False  
  
    try:
          ct=ContentType.objects.get_for_model(Merchandise)
          log_search = "content_type__id=%s"%ct.pk
    except: 
          log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_merchandisepage"
    else:
        help_model_name = MerchandisePage.__name__
    
    return render_to_response(MerchandisePage._template,RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "has_header": has_header,
        "searchform": searchform,
        "model_name": MerchandisePage._model_name,
        "position": MerchandisePage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search,
    })) 

class MerchandisePage(AppOperation):
    verbose_name = _(u'商品资料')
    view = render_merchandise_page
    _menu_index = 100065
    _app_menu = 'pos'
    _menu_group = 'pos'
    _model_name = "Merchandise" 
    _parent_model = "PosFormPage"
    _template = "Pos_Merchandise.html"
    _position = _(u'消费 -> 基本资料 -> 商品资料') 
    add_model_permission=[Merchandise]

#键值资料
@login_required
def render_keyvalue_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    searchform = get_searchform(request,KeyValue)
    if searchform:
        has_header=True          
    else:
        has_header=False  
  
    try:
          ct=ContentType.objects.get_for_model(KeyValue)
          log_search = "content_type__id=%s"%ct.pk
    except: 
          log_search =""
    if get_option("POS_IC"):
        help_model_name = "ic_keyvaluepage"
    else:
        help_model_name = KeyValuePage.__name__
    
    
    return render_to_response(KeyValuePage._template,RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        "menu_focus": "PosFormPage",
        "current_app": "pos",
        "has_header": has_header,
        "searchform": searchform,
        "model_name": KeyValuePage._model_name,
        "position": KeyValuePage._position,
        "help_model_name": help_model_name,
        "log_search" : log_search
    })) 

class KeyValuePage(AppOperation):
    verbose_name = _(u'键值资料')
    view = render_keyvalue_page
    _menu_index = 100066
    _app_menu = 'pos'
    _menu_group = 'pos'
    _model_name = "KeyValue" 
    _parent_model = "PosFormPage"
    _template = "Pos_KeyValue.html"
    _position = _(u'消费 -> 基本资料 -> 键值资料') 
    add_model_permission=[KeyValue]
        
    

    
    

    

