#coding=utf-8

from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.settings import MEDIA_ROOT
from django.utils.translation import ugettext_lazy as _

def iclock_guide(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    request.dbapp_url =dbapp_url
    apps=get_all_app_and_models()
    return render_to_response('iclock_guide.html',
           RequestContext(request,{
                   'dbapp_url': dbapp_url,
                   'MEDIA_URL':MEDIA_ROOT,
                   "current_app":'iclock', 
                   'apps':apps,
                   "help_model_name":"IclockGuide",
                   "myapp": [a for a in apps if a[0]=="iclock"][0][1],
                   'app_label':'iclock',
                   'model_name':'IclockGuide',
                   'menu_focus':'IclockGuide',
                   'position':_(u'设备->导航'),
                   })
           
           )
    