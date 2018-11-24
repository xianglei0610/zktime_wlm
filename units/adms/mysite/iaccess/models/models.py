# -*- coding: utf-8 -*-.
from django.utils.translation import ugettext_lazy as _
from base.models import AppOperation
from django.db import models
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from mysite.settings import MEDIA_ROOT
from accdoor import AccDoor
from acclevelset import AccLevelSet
from accmonitorlog import AccRTMonitor
from mysite.personnel.models import Employee
from mysite.iclock.models import Device
from dbapp.dataviewdb import seachform_for_model
from base import get_all_app_and_models
from django.contrib.auth.decorators import login_required
from dbapp.templatetags.dbapp_tags import HasPerm
from django.http import HttpResponse, HttpResponseRedirect

u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以门设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""


@login_required
def render_acc_guide_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    return render_to_response('Acc_Guide.html',
        RequestContext(request,{
            'dbapp_url': dbapp_url,
            'MEDIA_URL': MEDIA_ROOT,
            'current_app': 'iaccess', 
            'apps': apps,
            'help_model_name': "AccGuidePage",
            'myapp': [a for a in apps if a[0]=="iaccess"][0][1],
            'app_label': 'iaccess',
            'model_name': 'AccGuidePage',
            'menu_focus': 'AccGuidePage',
            'position': _(u'门禁系统->导航'),
        })
    )

class AccGuidePage(AppOperation):
    u'''导航'''
    verbose_name=_(u'导航')
    view = render_acc_guide_page
    _app_menu = "iaccess"
    _menu_group = "iaccess"
    _menu_index = 9999

#生成查询的表单
def get_searchform(request, model):
    if hasattr(model.Admin,"query_fields_iaccess") and model.Admin.query_fields_iaccess:        
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields_iaccess))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform

#门设置视图
@login_required
def render_doorset_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    if HasPerm(request.user, 'contenttypes.can_DoorMngPage'):
        template = DoorMngPage._template
        position = DoorMngPage._position
        searchform = get_searchform(request, Device)
        help_model_name = DoorMngPage.__name__

    elif HasPerm(request.user, 'contenttypes.can_DoorSetPage'):#其他跟模型相关的界面需要到模板中重定向
        template = "Acc_Door_Set.html"
        position = ""
        searchform = ""
        help_model_name = ""
#local variable 'searchform' referenced before assignment
#    else:
#        template = "Acc_Door_Set.html"
#        position = ""
#        searchform = ""
        
    if searchform:
        has_header=True          
    else:
        has_header=False
        
    return render_to_response(template, RequestContext(request, {
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
     	"current_app": "iaccess",
        "menu_focus": "DoorSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name,
    }))


class DoorSetPage(AppOperation):
    u"""
    门设置菜单
    """
    verbose_name = _(u'门设置')
    view = render_doorset_page
    _app_menu = "iaccess"
    _menu_index = 10002
    _cancel_perms = [("can_DoorMngPage.browse_accinterlock.browse_accantiback.browse_acclinkageio","can_DoorSetPage")]
    _hide_perms = ["can_DoorSetPage"]
    
    
#门管理视图
@login_required
def render_doormng_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, Device)
    if searchform:
        has_header=True          
    else:
        has_header=False     
    return HttpResponseRedirect("/iaccess/DoorSetPage/");
    return render_to_response(DoorMngPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "DoorSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": DoorMngPage._position,
        "help_model_name": DoorMngPage.__name__
    }))
    
class DoorMngPage(AppOperation):
    u"""
    门管理菜单
    """
    verbose_name = _(u'门管理')
    view = render_doormng_page
    _app_menu = 'iaccess'
    _menu_group = "acc_doorset"
    _parent_model = 'DoorSetPage'
    _menu_index = 100021
    _hide_perms = ["can_DoorMngPage"]
    _template = "Acc_Door_Mng.html"
    _position = _(u'门禁系统 -> 门设置 -> 门管理')
    _cancel_perms = [("opchangeipofacpanel_device.opdisabledevice_device.openabledevice_device.resetpassword_device.syncacpaneltime_device.uploadlogs_device.browse_accdoor","can_DoorMngPage")]
    
#人员权限设置-默认以权限组显示
@login_required
def render_emplevelset_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
        
    if HasPerm(request.user, 'contenttypes.can_EmpLevelByLevelPage'):
        model_name = EmpLevelByLevelPage._model_name
        template = EmpLevelByLevelPage._template
        position = EmpLevelByLevelPage._position
        searchform = get_searchform(request, AccLevelSet)
        help_model_name = "EmpLevelSetPage"
        
    elif HasPerm(request.user, 'contenttypes.can_EmpLevelByEmpPage'):
        model_name = EmpLevelByEmpPage._model_name
        template = EmpLevelByEmpPage._template
        position = EmpLevelByEmpPage._position
        searchform = get_searchform(request, Employee)
        help_model_name = "EmpLevelSetPage"

    if searchform:
        has_header=True          
    else:
        has_header=False
 
    return render_to_response(template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "EmpLevelSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "model_name": model_name,
        "help_model_name": "EmpLevelSetPage"
    }))    
    

class EmpLevelSetPage(AppOperation):
    u"""
    人员门禁权限设置菜单
    """
    #verbose_name = 'Emp LevelSet'
    verbose_name = _(u'人员门禁权限设置')
    view = render_emplevelset_page
    _menu_index = 10004
    _app_menu = 'iaccess'
    _hide_perms = ["can_EmpLevelSetPage"]   
    _cancel_perms = [("can_EmpLevelByLevelPage.can_EmpLevelByEmpPage","can_EmpLevelSetPage")]
   
    
#人员权限设置-以权限组显示(主要用于菜单显示)
@login_required
def render_emplevelbylevel_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, AccLevelSet)
    if searchform:
        has_header = True          
    else:
        has_header = False 

    return render_to_response(EmpLevelByLevelPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "EmpLevelSetPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": EmpLevelByLevelPage._position,
        "model_name": EmpLevelByLevelPage._model_name,
        "help_model_name": "EmpLevelSetPage"
    }))    
    

class EmpLevelByLevelPage(AppOperation):
    u"""
    人员门禁权限设置菜单-以权限组显示
    """
    verbose_name = _(u'以权限组显示')
    view = render_emplevelbylevel_page
    _menu_index = 100041
    _app_menu = 'iaccess'
    _menu_group = 'acc_emplevelset'
    _parent_model = 'EmpLevelSetPage'
    _hide_perms = ["can_EmpLevelByLevelPage"] 
    _template = "Acc_EmpLevel_Bylevel.html"
    _position = _(u'门禁系统 -> 人员门禁权限设置 -> 以权限组显示')
    _model_name = 'AccLevelSet'#用在导出时
    _cancel_perms = [("opaddemptolevel_acclevelset.opdelempfromlevel_acclevelset","can_EmpLevelByLevelPage")]

#人员权限设置-以人显示 
@login_required
def render_emplevelbyemp_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    searchform = get_searchform(request, Employee)
    if searchform:
        has_header=True          
    else:
        has_header=False     

    return render_to_response(EmpLevelByEmpPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "EmpLevelSetPage",
        "has_header": has_header,
        "searchform": searchform, 
        "position": EmpLevelByEmpPage._position,
        "model_name": EmpLevelByEmpPage._model_name,
        "help_model_name": "EmpLevelSetPage"
    }))    
    

class EmpLevelByEmpPage(AppOperation):
    u"""
    人员门禁权限设置菜单-以人员显示
    """
    #verbose_name = 'Emp LevelSet'
    verbose_name = _(u'以人员显示')
    view = render_emplevelbyemp_page
    #_app_menu = "acc_emplevelset"
    _menu_index = 100042
    _app_menu = 'iaccess'
    _menu_group = 'acc_emplevelset'
    _parent_model = 'EmpLevelSetPage'
    _hide_perms = ["can_EmpLevelByEmpPage"]
    _template = "Acc_EmpLevel_Byemp.html"
    _position = _(u'门禁系统 -> 人员门禁权限设置 -> 以人员显示')
    _model_name = 'Employee'
    _cancel_perms = [("opaddleveltoemp_employee.opdellevelfromemp_employee","can_EmpLevelByEmpPage")]

#实时监控视图
@login_required
def render_rtmonitor_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    if HasPerm(request.user, 'contenttypes.can_MonitorAllPage'):
        template = MonitorAllPage._template
        position = MonitorAllPage._position
        help_model_name = "RTMonitorPage"
    elif HasPerm(request.user, 'contenttypes.can_MonitorAlarmPage'):
        template = MonitorAlarmPage._template
        position = MonitorAlarmPage._position
        help_model_name = "RTMonitorPage"

    return render_to_response(template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "app_label": "iaccess",
        "menu_focus": "RTMonitorPage",
        "position": position,
        "help_model_name": "RTMonitorPage"
    }))    

class RTMonitorPage(AppOperation):
    u"""
    实时监控菜单
    """
    #verbose_name = 'RealTime Monitor'
    verbose_name = _(u'实时监控')
    view = render_rtmonitor_page
    _app_menu = "iaccess"
    _menu_index = 10005
    _select_related_perms = {"can_RTMonitorPage":"can_MonitorAllPage"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
    _cancel_perms = [("can_MonitorAllPage.can_MonitorAlarmPage","can_RTMonitorPage")]
    _hide_perms = ["can_RTMonitorPage"]   

#监控全部 视图---
@login_required
def render_monitorall_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    return render_to_response(MonitorAllPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "RTMonitorPage",
        "position": MonitorAllPage._position,
        "help_model_name": "RTMonitorPage"
    }))    

class MonitorAllPage(AppOperation):
    u"""
    实时监控-监控全部菜单
    """
    verbose_name = _(u'监控全部')
    view = render_monitorall_page
    #_app_menu = "acc_monitor"
    _menu_index = 100051
    _app_menu = 'iaccess'
    _menu_group = 'acc_monitor'
    _parent_model = 'RTMonitorPage'
    _position = _(u'门禁系统 -> 实时监控 -> 监控全部')
    _template = "Acc_Monitor_All.html"

#报警事件视图
@login_required
def render_monitoralarm_page(request):
    from dbapp.urls import dbapp_url
    logid = request.GET.get("a_logid", 0)#直接访问监控报警时从0开始
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    return render_to_response(MonitorAlarmPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "menu_focus": "RTMonitorPage",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "current_app": "iaccess",
        "logid": logid,
        "position": MonitorAlarmPage._position,
        "help_model_name": "RTMonitorPage"
    }))    

class MonitorAlarmPage(AppOperation):
    u"""
    实时监控-报警事件菜单
    """
    verbose_name = _(u'报警事件')
    view = render_monitoralarm_page
    #_app_menu = "acc_monitor"
    _menu_index = 100052
    _app_menu = 'iaccess'
    _menu_group = 'acc_monitor'
    _parent_model = 'RTMonitorPage'
    _position = _(u'门禁系统 -> 实时监控 -> 报警事件')
    _template = "Acc_Monitor_Alarm.html"

#电子地图视图
@login_required
def render_electromap_page(request):
    from dbapp.urls import dbapp_url
    #logid = request.GET.get("a_logid", 0)#直接访问监控报警时从0开始
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    return render_to_response(ElectroMapPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "menu_focus": "RTMonitorPage",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "current_app": "iaccess",
        #"logid": logid,
        "position": ElectroMapPage._position,
        "help_model_name": "RTMonitorPage"
    }))    

class ElectroMapPage(AppOperation):
    u"""
    实时监控-电子地图菜单
    """
    verbose_name = _(u'电子地图')
    view = render_electromap_page
    #_app_menu = "acc_monitor"
    _menu_index = 100053
    _app_menu = 'iaccess'
    _menu_group = 'acc_monitor'
    _parent_model = 'RTMonitorPage'
    _position = _(u'门禁系统 -> 实时监控 -> 电子地图')
    _template = "Acc_Electro_Map.html"
    #_select_related_perms = {"can_AllEventReportPage":"browse_accmap.add_accmap.opclearrtlogs_accmap.opclearabnormitylogs"}


#报表视图
@login_required
def render_reportform_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    
    if HasPerm(request.user, 'contenttypes.can_AllEventReportPage'):
        model_name = AllEventReportPage._model_name
        template = AllEventReportPage._template
        position = AllEventReportPage._position
        searchform = get_searchform(request, AccRTMonitor)
        help_model_name = "AllEventReportPage"
    elif HasPerm(request.user, 'contenttypes.can_AlarmEventReportPage'):
        model_name = AlarmEventReportPage._model_name
        template = AlarmEventReportPage._template
        position = AlarmEventReportPage._position
        searchform = get_searchform(request, AccRTMonitor)
        help_model_name = "AllEventReportPage"
    elif HasPerm(request.user, 'contenttypes.can_EmpLevelReportPage'):
        model_name = EmpLevelReportPage._model_name
        template = EmpLevelReportPage._template
        position = EmpLevelReportPage._position
        searchform = get_searchform(request, AccLevelSet)
        help_model_name = "AllEventReportPage"

    if searchform:
        has_header = True          
    else:
        has_header = False

    return render_to_response(template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "model_name": model_name,
        "current_app": "iaccess",
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "ReportFormPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": help_model_name
    }))    
    

class ReportFormPage(AppOperation):
    u"""
    报表菜单
    """
    #verbose_name = 'Report Forms'
    verbose_name = _(u'报表')
    view = render_reportform_page
    _app_menu = "iaccess"
    _menu_index = 10006 

    add_model_permission=[AccRTMonitor,]
    _cancel_perms=[
            ("can_AllEventReportPage.can_AlarmEventReportPage","dataexport_accrtmonitor"),
            ("can_AllEventReportPage.can_AlarmEventReportPage","browse_accrtmonitor"),
            ("can_AllEventReportPage.can_AlarmEventReportPage","opclearrtlogs_accrtmonitor"),
            ("can_AllEventReportPage.can_AlarmEventReportPage","opclearabnormitylogs_accrtmonitor"),
            ("can_AllEventReportPage.can_AlarmEventReportPage.can_EmpLevelReportPage","can_ReportFormPage")
    ]
    _disabled_perms = ['clear_accrtmonitor', 'dataimport_accrtmonitor', 'add_accrtmonitor', 'view_accrtmonitor', 'clear_accrtmonitor', 'change_accrtmonitor', 'delete_accrtmonitor']#只保留浏览、导出、清空权限
    _hide_perms = ['can_ReportFormPage', 'can_AllEventReportPage', 'browse_accrtmonitor', 'dataexport_accrtmonitor', 'opclearrtlogs_accrtmonitor', 'opclearabnormitylogs_accrtmonitor']
    
    
# 报表-全部事件
@login_required
def render_alleventreport_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    searchform = get_searchform(request, AccRTMonitor)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(AllEventReportPage._template, RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "ReportFormPage",
        "current_app": "iaccess",
        "model_name": AllEventReportPage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": AllEventReportPage._position,
        "help_model_name": "AllEventReportPage"      
    }))    

class AllEventReportPage(AppOperation):
    u"""
    报表-全部事件
    """
    verbose_name = _(u'全部门禁事件')
    view = render_alleventreport_page
    #_app_menu = "acc_report"
    _menu_index = 100061
    _app_menu = 'iaccess'
    _menu_group = 'acc_report'
    _model_name = "AccRTMonitor"
    _template = "Acc_Reportform_allevent.html"
    _position = _(u'门禁系统 -> 报表 -> 全部门禁事件')
    
    _parent_model = 'ReportFormPage'
    _select_related_perms = {"can_AllEventReportPage":"browse_accrtmonitor.dataexport_accrtmonitor.opclearrtlogs_accrtmonitor.opclearabnormitylogs_accrtmonitor.can_ReportFormPage"}

    
# 报表-异常事件
@login_required
def render_alarmeventreport_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    
    searchform = get_searchform(request, AccRTMonitor)
    if searchform:
        has_header=True          
    else:
        has_header=False  
    
    return render_to_response(AlarmEventReportPage._template,RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "ReportFormPage",
        "current_app": "iaccess",
        "model_name": AlarmEventReportPage._model_name,
        "has_header": has_header,
        "searchform": searchform,
        "position": AlarmEventReportPage._position,
        "help_model_name": "AllEventReportPage"
    }))
    
class AlarmEventReportPage(AppOperation):
    u"""
    报表-门禁异常事件
    """
    verbose_name = _(u'门禁异常事件')
    view = render_alarmeventreport_page
    #_app_menu = "acc_report"
    _menu_index = 100062
    _app_menu = 'iaccess'
    _model_name = "AccRTMonitor"
    _menu_group = 'acc_report'
    _template = "Acc_Reportform_alarm.html"
    _position = _(u'门禁系统 -> 报表 -> 门禁异常事件')

    _parent_model = 'ReportFormPage'
    _select_related_perms = {"can_AlarmEventReportPage":"browse_accrtmonitor.dataexport_accrtmonitor.can_ReportFormPage.opclearrtlogs_accrtmonitor.opclearabnormitylogs_accrtmonitor"}
    
# 报表-人员门禁权限
@login_required
def render_emplevelreport_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()

    searchform_AccLevelSet = get_searchform(request, AccLevelSet)
    searchform_AccDoor = get_searchform(request, AccDoor)
    searchform_Employee = get_searchform(request, Employee)
    
    if searchform_AccLevelSet:
        has_header=True          
    else:
        has_header=False    
    
    return render_to_response(EmpLevelReportPage._template,RequestContext(request,{
        "app_label": "iaccess",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
        "menu_focus": "ReportFormPage",
        "current_app": "iaccess",
        "has_header": has_header,
        "searchform_AccLevelSet": searchform_AccLevelSet,
        "searchform_AccDoor":searchform_AccDoor,
        "searchform_Employee":searchform_Employee,
        "model_name": EmpLevelReportPage._model_name,
        "position": EmpLevelReportPage._position,
        "help_model_name": "AllEventReportPage"
    })) 

class EmpLevelReportPage(AppOperation):
    u"""
    报表-人员门禁权限
    """
    verbose_name = _(u'人员门禁权限')
    view = render_emplevelreport_page
    _menu_index = 100063
    _app_menu = 'iaccess'
    _menu_group = 'acc_report'
    _model_name = "AccLevelSet" 
    _parent_model = 'ReportFormPage'
    _template = "Acc_Reportform_emplevel.html"
    _position = _(u'门禁系统 -> 报表 -> 人员门禁权限') 
        
@login_required
def render_acc_option(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    from mysite.settings import MEDIA_ROOT
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    apps = get_all_app_and_models()
    
    return render_to_response('Acc_Option.html',
       RequestContext(request,{
               'dbapp_url': dbapp_url,
               'MEDIA_URL':MEDIA_ROOT,
               "current_app":'iaccess', 
               'apps':apps,
               "help_model_name":"AccOption",
               "myapp": [a for a in apps if a[0]=="iaccess"][0][1],
               'app_label':'iaccess',
               'menu_focus':'AccOption',
               'position':_(u'门禁系统 -> 门禁参数设置'),
               'data':1234,
               })
       )
    
class AccOption(AppOperation):
        from django.conf import settings
        u'''门禁参数设置'''
        verbose_name = _(u'门禁参数设置')
        view = render_acc_option
        _app_menu = "iaccess"
        _menu_index = 10007
        visible = "mysite.iaccess" in settings.INSTALLED_APPS


    
    

    

