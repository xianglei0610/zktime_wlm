# -*- coding: utf-8 -*-
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change
from settings import MEDIA_ROOT,ADDITION_FILE_ROOT,LOGIN_REDIRECT_URL,UNIT_URL,SELFSERVICE_LOGIN_REDIRECT_URL,APP_HOME
from django.template import loader, Context, RequestContext
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from dbapp.utils import *
from staticfiles import serve
import base
from base.log import logger
from django.core.urlresolvers import RegexURLPattern
from django.utils.translation import ugettext_lazy as _
from dbapp.custom_model_view import AppPageView,GridModelView

def index(request):
        #logger.info('request: %s'%request)
        if request.session.has_key("employee"):
            return HttpResponseRedirect(SELFSERVICE_LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(LOGIN_REDIRECT_URL)
#        return render_to_response("index.html", RequestContext(request, {}),);

def my_i18n(request):
        from django.views.i18n import set_language
        from base.options import options
        r=set_language(request)
        set_cookie(r, 'django_language', request.REQUEST['language'], 365*24*60*60)
        options['base.language']=request.REQUEST['language']
        return r
    
def checkno(request,app_label,model_name):
        from dbapp.datautils import QueryData
        from dbapp.modelutils import GetModel        
        from mysite.personnel.models.model_emp import format_pin
        obj=GetModel(app_label, model_name)
        data=dict(request.REQUEST.items())
        
        #qs,cl=QueryData(request,obj)
        if 'PIN__exact' in data.keys():
            data['PIN__exact']=format_pin(str(data['PIN__exact']))
        d={}
        for k,v in data.items():
            d[str(k)]=v

        qs=obj.all_objects.filter(**d)
        if qs.count()>0:
            if model_name == "Employee":
                return HttpResponse(smart_str(simplejson.dumps({"info": "&times; " + u"%s"%_(u"重复使用"), "ret": 1})))
            else:
                return HttpResponse(smart_str(simplejson.dumps({"info": "&times; " + u"%s"%_(u"已存在"), "ret": 1})))
        else:
            return HttpResponse(smart_str(simplejson.dumps({"info": "&radic; " + u"%s"%_(u"可使用"), "ret": 2})))

surl=UNIT_URL[1:]

def tmp_url():
    return surl+'tmp/'

moleprocess = None
def RunMoleSys(request):
    import os
    global moleprocess
    if moleprocess is not None:
        return HttpResponse("RunMoleSys Runing")
    _cur = APP_HOME + '\\MoleSys'
    os.chdir(_cur)
    moleprocess = os.popen("MoleRunSer.bat")
    return HttpResponse("RunMoleSys OK")
#    return HttpResponseRedirect("http://127.0.0.1:8123")

def CloseMoleSys(request):
    global moleprocess
    if moleprocess is not None:
        moleprocess.close
    return HttpResponse("CloseMoleSys OK")
    
urlpatterns = patterns('',
    ('i18n/setlang/', my_i18n), #系统语言设置

    (r'^'+surl+'file/(?P<path>.*)$', serve, {'document_root': ADDITION_FILE_ROOT, 'show_indexes': True}),
    (r'^'+tmp_url()+'(?P<path>.*)$', serve, {'document_root': tmpDir(), 'show_indexes': True}),
    (r'^'+surl+'media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, 'show_indexes': False}),
    (r'^'+surl+'api/', include('mysite.api.urls')),         #RESTful API 接口
    (r'^'+surl+'checkno/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$',checkno),
    
    (r'^'+surl+'accounts/', include('mysite.authurls')),         #用户登录、登出、密码设置
    
    (r'^'+surl+'data/', include('dbapp.urls')),                         #通用数据管理
    (r'^'+surl+'page/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$',AppPageView),
    (r'^'+surl+'grid/(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$',GridModelView),
    (r'^'+surl+'iclock/', include('mysite.iclock.urls')),         #adms管理
    (r'^iclock/file/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ADDITION_FILE_ROOT}),
    (r'^'+surl+'testapp/', include('mysite.testapp.urls')),         #用于测试的应用
    (r'^'+surl+'personnel/',include('mysite.personnel.urls')),   #人事管理系统
    (r'^'+surl+'worktable/',include('mysite.worktable.urls')),   #我的工作面板
    (r'^'+surl+'selfservice/',include('mysite.selfservice.urls')),   #员工自助
    (r'^'+surl+'report/',include('mysite.report.urls')),   #报表设计
#    (r'^'+surl+'meeting/',include('mysite.meeting.urls')),   
        #其他
    (r'^media/(?P<path>.*)$', serve,  {'document_root': MEDIA_ROOT, 'show_indexes': True}),
    (r'^$', index),
    (r'^manager/',include('mysite.manager.urls')),
    (r'^moleopen/', RunMoleSys),
    (r'^moleclose/', CloseMoleSys),
)

dict_urls={
    "mysite.att":url(r'^'+surl+'att/',include('mysite.att.urls'),prefix=''),#考勤系统系理
    "mysite.iaccess":url(r'^'+surl+'iaccess/',include('mysite.iaccess.urls'),prefix=''),#zkaccess门禁系统管理
    "mysite.video":url(r'^'+surl+'video/',include('mysite.video.urls'),prefix=''),#视频系统管理
    "rosetta":url(r'^rosetta/', include('rosetta.urls'),prefix=''),
    "mysite.elevator":url(r'^'+surl+'elevator/',include('mysite.elevator.urls'),prefix=''),
    "mysite.visitor":url(r'^'+surl+'visitor/',include('mysite.visitor.urls'),prefix=''),
    "mysite.pos":url(r'^'+surl+'pos/',include('mysite.pos.urls')),#消费系统管理
    "mysite.meeting":url(r'^'+surl+'meeting/',include('mysite.meeting.urls'),prefix=''),#会议系统
}


for k,v in dict_urls.items():
    if k in settings.INSTALLED_APPS:
        urlpatterns.append(v)