# -*- coding: utf-8 -*-.
from django.utils.translation import ugettext_lazy as _
from base.models import AppOperation
from django.db import models
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from mysite.settings import MEDIA_ROOT
from mysite.iaccess.models.accdoor import AccDoor
from mysite.iaccess.models.acclevelset import AccLevelSet
from mysite.iaccess.models.accmonitorlog import AccRTMonitor
from mysite.iaccess.models.acctimeseg import AccTimeSeg
from mysite.personnel.models import Employee
from mysite.iclock.models import Device
from dbapp.dataviewdb import seachform_for_model
from base import get_all_app_and_models
from django.contrib.auth.decorators import login_required
from dbapp.templatetags.dbapp_tags import HasPerm

u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以楼层设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""

#生成查询的表单
def get_searchform(request, model):
    if hasattr(model.Admin,"query_fields_elevator") and model.Admin.query_fields_elevator:        
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields_elevator))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform

#楼层设置视图
@login_required
def render_floorset_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    #strtest = [a for a in apps if a[0]=="elevator"][0][1]

    if HasPerm(request.user, 'contenttypes.can_FloorMngPage'):
        template = FloorMngPage._template
        position = FloorMngPage._position
        searchform = get_searchform(request, Device)
        help_model_name = FloorMngPage.__name__

    elif HasPerm(request.user, 'contenttypes.can_FloorSetPage'):#其他跟模型相关的界面需要到模板中重定向
        template = "Elevator_Floor_Set.html"
        position = ""
        searchform = ""
        help_model_name = ""
#local variable 'searchform' referenced before assignment
#    else:
#        template = "Elevator_Floor_Set.html"
#        position = ""
#        searchform = ""
        
    if searchform:
        has_header=True          
    else:
        has_header=False
    #template = "Elevator_floor_Mng.html"
    return render_to_response(template, RequestContext(request, {
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
     	"current_app": "elevator",
        "menu_focus": "FloorSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name,
    }))


class FloorSetPage(AppOperation):
    u"""
    楼层设置菜单
    """
    verbose_name = _(u'楼层设置')
    view = render_floorset_page
    _app_menu = "elevator"
    _menu_index = 10002
    _cancel_perms = [("can_FloorMngPage.browse_accinterlock.browse_accantiback.browse_acclinkageio","can_FloorSetPage")]
    _hide_perms = ["can_FloorSetPage"]
    _position = _(u'梯控系统 -> 楼层设置')
    
#楼层管理视图
@login_required
def render_floormng_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, Device)
    if searchform:
        has_header=True          
    else:
        has_header=False     
    
    is_lift =True
    
    return render_to_response(FloorMngPage._template, RequestContext(request,{
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "elevator",
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "menu_focus": "FloorSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": FloorMngPage._position,
        "help_model_name": FloorMngPage.__name__,
        "is_lift": is_lift
    }))
    

class FloorMngPage(AppOperation):
    u"""
    楼层管理菜单
    """
    verbose_name = _(u'楼层管理')
    view = render_floormng_page
    _app_menu = 'elevator'
    _menu_group = "acc_doorset"
    _parent_model = 'FloorSetPage'
    _menu_index = 100021
    _hide_perms = ["can_FloorMngPage"]
    _template = "Elevator_floor_Mng.html"
    _position = _(u'梯控系统 -> 楼层设置 -> 楼层管理')
    _cancel_perms = [("opchangeipofacpanel_device.opdisabledevice_device.openabledevice_device.resetpassword_device.syncacpaneltime_device.uploadlogs_device.browse_accdoor","can_FloorMngPage")]
    
#人员权限设置-默认以权限组显示
@login_required
def render_empelevatorlevelset_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
        
    if HasPerm(request.user, 'contenttypes.can_EmpElevtorLevelByLevelPage'):
        model_name = EmpElevtorLevelByLevelPage._model_name
        template = EmpElevtorLevelByLevelPage._template
        position = EmpElevtorLevelByLevelPage._position
        searchform = get_searchform(request, AccLevelSet)
        help_model_name = EmpElevtorLevelByLevelPage.__name__
        
    elif HasPerm(request.user, 'contenttypes.can_EmpElevatorLevelByEmpPage'):
        model_name = EmpElevatorLevelByEmpPage._model_name
        template = EmpElevatorLevelByEmpPage._template
        position = EmpElevatorLevelByEmpPage._position
        searchform = get_searchform(request, Employee)
        help_model_name = EmpElevatorLevelByEmpPage.__name__

    if searchform:
        has_header=True          
    else:
        has_header=False
 
    return render_to_response(template, RequestContext(request,{
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "elevator",
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "menu_focus": "EmpElevatorLevelSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "model_name": model_name,
        "help_model_name": help_model_name
    }))    
    

class EmpElevatorLevelSetPage(AppOperation):
    u"""
    人员电梯权限设置菜单
    """
    #verbose_name = 'Emp LevelSet'
    verbose_name = _(u'人员电梯权限设置')
    view = render_empelevatorlevelset_page
    _menu_index = 10004
    _app_menu = 'elevator'
    _hide_perms = ["can_EmpElevatorLevelSetPage"]   
    _cancel_perms = [("can_EmpElevatorLevelByEmpPage.can_EmpElevtorLevelByLevelPage","can_EmpElevatorLevelSetPage")]
   
    
#人员权限设置-以权限组显示(主要用于菜单显示)
@login_required
def render_empelevatorlevelbylevel_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, AccLevelSet)
    if searchform:
        has_header = True          
    else:
        has_header = False 

    return render_to_response(EmpElevtorLevelByLevelPage._template, RequestContext(request,{
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "elevator",
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "menu_focus": "EmpElevatorLevelSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": EmpElevtorLevelByLevelPage._position,
        "model_name": EmpElevtorLevelByLevelPage._model_name,
        "help_model_name": EmpElevtorLevelByLevelPage.__name__
    }))    
    

class EmpElevtorLevelByLevelPage(AppOperation):
    u"""
    人员电梯权限设置菜单-以权限组显示
    """
    verbose_name = _(u'以权限组显示')
    view = render_empelevatorlevelbylevel_page
    _menu_index = 100041
    _app_menu = 'elevator'
    _menu_group = 'elevator_emplevelset'
    _parent_model = 'EmpElevatorLevelSetPage'
    _hide_perms = ["can_EmpElevtorLevelByLevelPage"] 
    _template = "Elevator_EmpLevel_Bylevel.html"
    _position = _(u'梯控系统 -> 人员电梯权限设置 -> 以权限组显示')
    _model_name = 'AccLevelSet'#用在导出时
    _cancel_perms = [("opaddemptolevel_acclevelset.opdelempfromlevel_acclevelset","can_EmpElevtorLevelByLevelPage")]

#人员权限设置-以人显示 
@login_required
def render_empelevatorlevelbyemp_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    searchform = get_searchform(request, Employee)
    if searchform:
        has_header=True          
    else:
        has_header=False     

    return render_to_response(EmpElevatorLevelByEmpPage._template, RequestContext(request,{
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "elevator",
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "menu_focus": "EmpElevatorLevelSetPage",
        "has_header": has_header,
        "searchform": searchform, 
        "position": EmpElevatorLevelByEmpPage._position,
        "model_name": EmpElevatorLevelByEmpPage._model_name,
        "help_model_name": EmpElevatorLevelByEmpPage.__name__    
    }))    
    

class EmpElevatorLevelByEmpPage(AppOperation):
    u"""
    人员电梯权限设置菜单-以人员显示
    """
    #verbose_name = 'Emp LevelSet'
    verbose_name = _(u'以人员显示')
    view = render_empelevatorlevelbyemp_page
    #_app_menu = "acc_emplevelset"
    _menu_index = 100042
    _app_menu = 'elevator'
    _menu_group = 'elevator_emplevelset'
    _parent_model = 'EmpElevatorLevelSetPage'
    _hide_perms = ["can_EmpElevatorLevelByEmpPage"]
    _template = "Elevator_EmpLevel_Byemp.html"
    _position = _(u'梯控系统 -> 人员电梯权限设置 -> 以人员显示')
    _model_name = 'Employee'
    _cancel_perms = [("opaddleveltoemp_employee.opdellevelfromemp_employee","can_EmpElevatorLevelByEmpPage")]
    #default_give_perms = 


    
## 报表-人员电梯权限
#@login_required
#def render_emplevelreport_page(request):
#    from dbapp.urls import dbapp_url
#    request.dbapp_url = dbapp_url
#    apps = get_all_app_and_models()
#
#    searchform_AccLevelSet = get_searchform(request, AccLevelSet)
#    searchform_AccDoor = get_searchform(request, AccDoor)
#    searchform_Employee = get_searchform(request, Employee)
#    
#    if searchform_AccLevelSet:
#        has_header=True          
#    else:
#        has_header=False    
#    
#    return render_to_response(EmpLevelReportPage._template,RequestContext(request,{
#        "app_label": "elevator",
#        "dbapp_url": dbapp_url,
#        "MEDIA_ROOT": MEDIA_ROOT,
#        "apps": apps,
#        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
#        "menu_focus": "ReportFormPage",
#        "current_app": "elevator",
#        "has_header": has_header,
#        "searchform_AccLevelSet": searchform_AccLevelSet,
#        "searchform_AccDoor":searchform_AccDoor,
#        "searchform_Employee":searchform_Employee,
#        "model_name": EmpLevelReportPage._model_name,
#        "position": EmpLevelReportPage._position,
#        "help_model_name": EmpLevelReportPage.__name__
#    })) 
#
#class EmpLevelReportPage(AppOperation):
#    u"""
#    报表-人员电梯权限
#    """
#    verbose_name = _(u'人员电梯权限')
#    view = render_emplevelreport_page
#    _menu_index = 100063
#    _app_menu = 'elevator'
#    _menu_group = 'acc_report'
#    _model_name = "AccLevelSet" 
#    _parent_model = 'ReportFormPage'
#    _template = "Acc_Reportform_emplevel.html"
#    _position = _(u'电梯系统 -> 报表 -> 人员电梯权限') 
        
@login_required 
def render_floorlevelset_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    strtest = [a for a in apps if a[0]=="elevator"][0][1]

    if HasPerm(request.user, 'contenttypes.can_FloorLevelSetPage'):
        template = FloorLevelSetPage._template
        position = FloorLevelSetPage._position
        searchform = get_searchform(request, AccLevelSet)
        help_model_name = FloorLevelSetPage.__name__
        
    if searchform:
        has_header=True          
    else:
        has_header=False
    return render_to_response(template, RequestContext(request, {
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "current_app": "elevator",
        "menu_focus": "FloorLevelSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name,
    }))

class FloorLevelSetPage(AppOperation):
    u"""
    梯控权限组菜单
    """
    verbose_name = _(u'梯控权限组')
    view = render_floorlevelset_page
    _app_menu = 'elevator'
    _menu_group = "elevator_levelset"
    _menu_index = 10003
    _hide_perms = []
    add_model_permission=[AccLevelSet,]
    _template = "ElevatorLevelSet_list.html"
    _position = _(u'梯控系统 ->梯控权限组')
    _cancel_perms = [("opchangeipofacpanel_device.opdisabledevice_device.openabledevice_device.resetpassword_device.syncacpaneltime_device.uploadlogs_device.browse_accdoor","can_FloorLevelSetPage")]

@login_required
def render_elevatortimeseg_page(request):
    #print 'lift view'
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    strtest = [a for a in apps if a[0]=="elevator"][0][1]


    if HasPerm(request.user, 'contenttypes.can_ElevatorTimesegSetPage'):
        template = ElevatorTimesegSetPage._template
        position = ElevatorTimesegSetPage._position
        searchform = get_searchform(request, AccTimeSeg)
        help_model_name = ElevatorTimesegSetPage.__name__
        
    if searchform:
        has_header=True          
    else:
        has_header=False
    return render_to_response(template, RequestContext(request, {
        "app_label": "elevator",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="elevator"][0][1],
        "current_app": "elevator",
        "menu_focus": "ElevatorTimesegSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name,
    }))

class ElevatorTimesegSetPage(AppOperation):
    u"""
    梯控时间段菜单
    """
    verbose_name = _(u'梯控时间段')
    view = render_elevatortimeseg_page
    _app_menu = 'elevator'
    _menu_group = "elevator_timesegset"
    _menu_index = 10001
    _hide_perms = []
    add_model_permission=[AccTimeSeg,]
    _template = "ElevatorTimeSegSet_list.html"
    _position = _(u'梯控系统 ->梯控时间段')
    _cancel_perms = [("can_ElevatorTimesegSetPage")]
    #default_give_perms = ['browse_acctimeseg','add_acctimeseg','change_acctimeseg','delete_acctimeseg','dataexport_acctimeseg']
    #_bind_perms = _cancel_perms
    

    
    

    

