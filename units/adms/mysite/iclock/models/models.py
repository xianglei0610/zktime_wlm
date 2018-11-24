# -*- coding: utf-8 -*-.
from django.utils.translation import ugettext_lazy as _
from base.models import AppOperation
from django.template import RequestContext
from django.shortcuts import render_to_response
from mysite.settings import MEDIA_ROOT
from base import get_all_app_and_models
from django.contrib.auth.decorators import login_required
from django.conf import settings
from mysite.utils import get_option
u"""在与模型无关的类生成的菜单中,用menu_focus来使主菜单获取焦点,每个主菜单（上侧）中左侧的二级菜单menu_focus和主菜单相同.
 模型相关的类,则采取menu_focus优先原则,比如互锁/反潜等都需要在单击时以门设置为焦点,如果模型中没有设置menu_cocus,则将model_name给menu_focus"""


#设备实时监控视图
@login_required
def render_devrtmonitor_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()

    return render_to_response("Dev_RTMonitor.html",RequestContext(request,{
        "app_label": "iclock",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="iclock"][0][1],
        "current_app": "iclock",#"dev_monitor",
        "menu_focus": "DevRTMonitorPage",
        "position": _(u'设备 -> 设备监控'),
        "help_model_name": DevRTMonitorPage.__name__
    }))    

class DevRTMonitorPage(AppOperation):
    u"""
    设备监控菜单
    """
    verbose_name = _(u'设备监控')
    view = render_devrtmonitor_page
    visible=get_option("IACCESS")
    _app_menu = "iclock"
    _menu_index = 10005 
    


    
    

    

