# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str
from dbapp.modelutils import GetModel
from django.db.models import Q
from django.utils.simplejson  import dumps 
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
import datetime
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from dbapp.utils import getJSResponse
from base import get_all_app_and_models
from dbapp.datautils import NoFound404Response
from dbapp.urls import dbapp_url
from dbapp.dataviewdb import model_data_list
from django.db import models
from django.contrib.auth import logout
from dbapp.dataoperation import get_form
from dbapp.data_edit import DataDetail,DataNew
from django.conf import settings

FP_IDENTIFY_SUCCESS = 1     # 10.0指纹验证成功 
FP_NO_LICENCES = 2      # 10.0许可失败
FP_IDENTIFY_FAILED = 0      # 10.0指纹验证失败

@login_required
def model_list_self(request, app_label, model_name):
    u"员工自助默认的数据列表"
    from mysite.att.models import CheckExact
    Cls_Model=GetModel(app_label, model_name)
    if not Cls_Model: return NoFound404Response(request)
    
    try:
        emp = request.session["employee"]
    except:
        emp =None
    model_fields = Cls_Model._meta.fields
    filter_dict={}#需要添加过滤条件
    for f in model_fields:
        if isinstance(f,models.fields.related.ForeignKey) and f.rel.to.__name__=="Employee":
            filter_dict[f.name]=emp
    
    qs = Cls_Model.objects.filter(**filter_dict)
    return model_data_list(request, Cls_Model, qs,)


@login_required
def operation_self(request,app_label, model_name, op_name):
    u"员工自助登入"
    return get_form(request,app_label, model_name, op_name)
        
@login_required      
def model_new(request, app_label, model_name):
    u"员工自助新增"
    return DataNew(request, app_label, model_name)

@login_required      
def model_edit(request, app_label, model_name, DataKey):
    u"员工自助编辑"
    return DataDetail(request, app_label, model_name, DataKey)

@login_required
def get_checkexact(request):
    u"补签卡视图"
    from mysite.att.models import CheckExact
    apps=get_all_app_and_models(trans_apps=["selfservice"])
    return render_to_response('checkexact_self.html',
        RequestContext(request,{
                'dbapp_url': dbapp_url,
                'model_url': "/selfservice/att/CheckExact/",
                'app_label':"att",
                'model_name':"CheckExact",
                'MEDIA_URL':MEDIA_ROOT,
                'position':_(u'员工自助->补签卡'),
                "current_app":'selfservice',                     
                "help_model_name":"CheckExact",    				
                'menu_focus':'SelfCheckexact',    
                'MEDIA_URL':MEDIA_ROOT,
                'apps':apps,       
                "myapp": [a for a in apps if a[0]=="selfservice"][0][1],          
                "help_model_name":"CheckExact",    				
                "current_app":'selfservice', 
        })            
    )
    

@login_required
def get_specday(request):
    u"请假单视图"
    from mysite.att.models import EmpSpecDay
    apps=get_all_app_and_models(trans_apps=["selfservice"])
    return render_to_response('empspecday_self.html',
            RequestContext(request,{
                    'dbapp_url': dbapp_url,
                    'model_url': "/selfservice/att/EmpSpecDay/",
                    'app_label':"att",
                    'model_name':"EmpSpecDay",
                    'MEDIA_URL':MEDIA_ROOT,
                    'position':_(u'员工自助->请假'),
                    'apps':apps,       
                    "myapp": [a for a in apps if a[0]=="selfservice"][0][1],          
                    "help_model_name":"EmpSpecDay",    				
                    'menu_focus':'SelfSpecDay', 
                    "current_app":'selfservice',                  
        })            
    )
    
@login_required
def get_overtime(request):
    u"加班单视图"
    from mysite.att.models import OverTime
    apps=get_all_app_and_models(trans_apps=["selfservice"])
    
    return render_to_response('overtime_self.html',
            RequestContext(request,{
                    'dbapp_url': dbapp_url,
                    'model_url': "/selfservice/att/OverTime/",
                    'position':_(u'员工自助->补签卡'),
                    'apps':apps,       
                    "myapp": [a for a in apps if a[0]=="selfservice"][0][1],          
                    'dbapp_url': dbapp_url,
                    'app_label':"att",
                    'model_name':"OverTime",
                    'MEDIA_URL':MEDIA_ROOT,
                    'position':_(u'员工自助->加班单'),
                    "current_app":'selfservice',                     
                    "help_model_name":"OverTime",    				
                    'menu_focus':'SelfOverTime',    
            })            
    )
    
@login_required
def get_transaction(request):
    u"原始记录视图"
    from mysite.iclock.models.model_trans import Transaction
    apps=get_all_app_and_models(trans_apps=["selfservice"])

    return render_to_response('transaction_self.html',
            RequestContext(request,{
                    'dbapp_url': dbapp_url,
                    'model_url': "/selfservice/iclock/Transaction/",
                    'app_label':"iclock",
                    'model_name':"Transaction",
                    'apps':apps,
                    "myapp": [a for a in apps if a[0]=="selfservice"][0][1], 
                    'MEDIA_URL':MEDIA_ROOT,
                    'position':_(u'员工自助->原始记录表'),
                    "current_app":'selfservice',                     
                    "help_model_name":"Transaction",    				
                    'menu_focus':'SelfTransaction',      
        })            
    )

@login_required
def get_selfreport(request):
    u"员工自助报表视图"
    from mysite.iclock.models.model_trans import Transaction
    from mysite.iclock.datas   import GetCalcUnit,GetCalcSymbol
    unit=GetCalcUnit()
    symbol=GetCalcSymbol()

    dc={}
    dc['unit']=unit
    dc['symbol']=symbol
    request.dbapp_url=dbapp_url
    apps=get_all_app_and_models(trans_apps=["selfservice"])
    
    from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
    from mysite.utils import GetFormField
    ''' 定义模型字段 '''
    m_field = EmpPoPMultForeignKey(verbose_name=_(u'选择人员'),blank=True,null=True)
    ''' 得到表单字段供前端使用 '''
    emp = GetFormField("emp",m_field)   #得到表单字段
	
    
    return render_to_response('report_self.html',
        RequestContext(request, {'latest_item_list': smart_str(dumps(dc)),
            'from': 1,
            'page': 1,
            'limit': 10,
            'item_count': 4,
            'page_count': 1,
            'userid':request.session["employee"].pk,
            'dbapp_url': dbapp_url,
            'MEDIA_URL':MEDIA_ROOT,
            'apps':apps,
            "current_app":'selfservice', 
            'position':_(u'员工自助->报表查询'),        
            "help_model_name":"SelfReport",
            'menu_focus':'SelfReport',
            "myapp": [a for a in apps if a[0]=="selfservice"][0][1],
            'empfield': emp,
        }))


def check_selfuser(request):
    u"验证用户"
    from django.contrib.auth.models import User
    from mysite.personnel.models import Employee
    emp=None
    register_finger = request.REQUEST.get("login_type", "")
    if register_finger == 'fp':#
        from mysite.authurls import identify_operatorfinger_self
        template = identify_operatorfinger_self(request)       #用户比对指纹进入系统
        if template == FP_NO_LICENCES:
            return HttpResponse('2')
        elif template == FP_IDENTIFY_FAILED:
            return HttpResponse("error")
        else:
            emp = template.UserID
    else:
        username=request.REQUEST.get("username","").strip()
        password=request.REQUEST.get("password","").strip()
        emp=None
########  此处不能用get get 是从缓存里面取,信息不能实时更新  ,密码修改,人员状态修改时会出问题##########        
#        try:
#            emp=Employee.objects.get(PIN=username,selfpassword=password,status=0)
#        except:
#            try:
#                emp=Employee.objects.get(PIN=username.rjust(settings.PIN_WIDTH,"0"),selfpassword=password,status=0)
#            except:
#                pass
        emps=Employee.objects.filter(PIN=username,selfpassword=password,status=0)
        if not emps:
            emps = Employee.objects.filter(PIN=username.rjust(settings.PIN_WIDTH,"0"),selfpassword=password,status=0)
        if emps:
            emp = emps[0]
    if emp:
        try:
            user = authenticate(username="employee",password="jq92~+>)@#$%#")
            if not user.is_staff:
                return u"%s"%_(u"员工自助被停用")
            login(request, user)
            request.session["employee"]=emp
            return "SUCCESS"
        except Exception,e:
            import traceback;traceback.print_exc()
            return u"%s"%e
    return  u"%(msg)s"%{"msg":_(u"用户名或密码错误，原因可能是:忘记密码；未区分字母大小写；未开启小键盘！")}

def self_login(request):
    u"员工自助登入"
    msg=check_selfuser(request)
    if msg=="SUCCESS":
        return HttpResponse('ok')
    else:
        return HttpResponse(msg)
    
def password_change(request):
    u"员工自助密码修改"
    from mysite.personnel.models import Employee
    emp=request.session["employee"]
    org_pwd=str(request.POST.get("org_pwd"))
    new_pwd=str(request.POST.get("new_pwd"))
    new_again_pwd=str(request.POST.get("new_again_pwd"))
    if (not new_pwd.strip()) and (not new_again_pwd.strip()):
        return HttpResponse(u'%s'%_(u'密码不能为空'))
    
    if emp.selfpassword.upper()!=org_pwd.upper():
        return HttpResponse(u'%s'%_(u'原密码不正确'))
    if new_pwd!=new_again_pwd:
        return HttpResponse(u'%s'%_(u'新密码两次输入不正确'))
    emp.selfpassword=new_pwd
    emp.save()            
    return HttpResponse('{ Info:"OK" }')