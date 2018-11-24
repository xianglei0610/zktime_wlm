# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, login_required, PasswordChangeForm, password_change_done, password_reset, password_reset_done
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import get_user, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect,HttpResponse
from django.core.cache import cache
from django.conf import settings
from ctypes import *
from base.log import logger
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
import authorize_fun
from base.models import CachingModel
from base.login_bio import OperatorTemplate
from mysite.iclock.models import Template as Template_emp
import re
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site, RequestSite
from mysite.utils import get_option 
from ooredis import *
FP_IDENTIFY_SUCCESS = 1     # 10.0指纹验证成功 
FP_NO_LICENCES = 2      # 10.0许可失败
FP_IDENTIFY_FAILED = 0      # 10.0指纹验证失败

class EmployeeBackend(ModelBackend):
        def authenticate(self, username=None, password=None):
                from mysite.personnel.models import Employee
                try:
                        u=User.objects.get(username='employee')
                except ObjectDoesNotExist:
                        return None
                try:
                        e=Employee.objects.get(PIN=username)
                except ObjectDoesNotExist:
                        return None
                pwd=e.Password
                if not pwd: pwd=username
                if pwd!=password:
                        return None
                u.employee=e
                return u

def logon(request):
        logout(request)
        request.csrf_processing_done=True
        ret=login(request)
        if get_option("POS_IC"):
            set_ic_pos_session(request)
        if not request.POST: return ret
        
        #软件狗验证,
        #国外逻辑定义:客户端操作系统的语言非中文（IE）,浏览器语言非中文（其他浏览器ff,so）
        client_language=request.POST.get("client_language")
        check_ret=authorize_fun.login_check(request, settings.AUTHORIZE_MAGIC_KEY,client_language)
        #print '---read dog=',settings.ZKECO_DEVICE_LIMIT,settings.ATT_DEVICE_LIMIT,settings.MAX_ACPANEL_COUNT,'\n'
        if check_ret!=True:
            logout(request)
            return HttpResponse(check_ret)
        
        #指纹登入，修改request.user
        register_finger = request.REQUEST.get("login_type", "")#login_type 当前共两种类型 pwd和fp
        #print'####begin',register_finger
        if register_finger == 'fp':#
            template = identify_operatorfinger(request)       #用户比对指纹进入系统
            if template == FP_NO_LICENCES:
                return HttpResponse('2')
            elif template == FP_IDENTIFY_FAILED:
                return HttpResponse("error")
            else:
                user = template.user
                template_logon(request,user)
        
        user=request.user
        if user.is_anonymous()or user.username=="employee":
                return HttpResponse(u"%(msg)s"%{"msg":_(u"用户名或密码错误，原因可能是:忘记密码；未区分字母大小写；未开启小键盘！")})
        eb=-1
        try:
                eb=user.backend.find('EmployeeBackend')
        except: pass
        if eb==-1:
                user.employee=None
                if 'employee' in request.session:
                        del request.session["employee"]
        else:
                request.session["employee"]=user.employee
        if user.is_staff:
                from base.options import options
                from django.utils.translation import check_for_language
                from base.middleware.threadlocals import _thread_locals
                
                _thread_locals.user=user
                lang_code=options['base.language']
                if not lang_code:
                    #使用默认安装时选择的语言 
                    lang_code=settings.LANGUAGE_CODE
                if lang_code and check_for_language(lang_code):
                        if hasattr(request, 'session'):
                                request.session['django_language'] = lang_code
                        else:
                                ret.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
                
                #删除菜单缓存
                cache_key = "%s_%s_%s"%(lang_code,user.username,"menu_list")
                cache.delete(cache_key)

                try:
                    from base.models_logentry import LogEntry, LOGIN
                    from django.contrib.contenttypes.models import ContentType
                    LogEntry.objects.log_action(
                            user_id                 = user and user.pk or None,
                            content_type_id = None,
                            object_id           = user.pk,
                            object_repr         = "",
                            action_flag         = LOGIN,
                            change_message      = ""
                    )
                except:
                   import traceback; traceback.print_exc()
                return HttpResponse('ok')
        logout(request)
        return HttpResponse(u"%s"%_(u"您还没有分配权限!"))


#class MathFpTemplate(self):
#    def _init_(self):
#        self.mathpro = windll.LoadLibrary("match.dll")

def identify_operatorfinger(request):
    obj_template = request.REQUEST.get("template10", "")
    mathpro = windll.LoadLibrary("match.dll")
    if obj_template:
        from ctypes import create_string_buffer
        obj_template = create_string_buffer(obj_template)
        tmps = OperatorTemplate.objects.filter(fpversion=10)  #比对时只取10.0
        if tmps:
            for t in tmps:
                try:
                    source_template = t.template1
                    source_template = create_string_buffer(source_template)
                
                    math_result = mathpro.process10(source_template, obj_template)
                    if math_result == FP_IDENTIFY_SUCCESS:
                        user = t.user
                        backend = ModelBackend()
                        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
                        return t
                    elif math_result == FP_NO_LICENCES:
                        return math_result       
                except:
                    import traceback; traceback.print_exc()
            return FP_IDENTIFY_FAILED
        else:
            return FP_IDENTIFY_FAILED
        
def identify_operatorfinger_self(request):
    obj_template = request.REQUEST.get("template10", "")
    mathpro = windll.LoadLibrary("match.dll")
    if obj_template:
        from ctypes import create_string_buffer
        obj_template = create_string_buffer(obj_template)
        tmps = Template_emp.objects.filter(Fpversion=10)
        if tmps:
            for t in tmps:
                try:
                    source_template = t.Template
                    source_template = create_string_buffer(source_template)
                
                    math_result = mathpro.process10(source_template, obj_template)
                    if math_result == FP_IDENTIFY_SUCCESS:
                        return t
                    elif math_result == FP_NO_LICENCES:
                        return math_result       
                except:
                    import traceback; traceback.print_exc()
            return FP_IDENTIFY_FAILED
        else:
            return FP_IDENTIFY_FAILED
        
def set_ic_pos_session(request):
    from mysite.pos.models.model_posparam import PosParam
    try:
        obj_param = PosParam.objects.all()
#        request.session['obj_param'] = obj_param[0]
        redis_obj_param = Dict("pos_obj_param")
        redis_obj_param['main_fan_area'] = obj_param[0].main_fan_area
        redis_obj_param['minor_fan_area'] = obj_param[0].minor_fan_area
        redis_obj_param['system_pwd'] = obj_param[0].system_pwd
        redis_obj_param['max_money'] = str(obj_param[0].max_money)
#        request.session['main_fan_area'] = obj_param[0].main_fan_area
#        request.session['minor_fan_area'] = obj_param[0].minor_fan_area
#        request.session['system_pwd'] = obj_param[0].system_pwd
    except:
        import traceback;traceback.print_exc()
        
def template_logon(request, user, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=AuthenticationForm):
    t_redirect_to = request.REQUEST.get(redirect_field_name, '')
    try:
#        if request.method == "POST":
        form = authentication_form(data=request.POST)
        #if form.is_valid():
        if not t_redirect_to or ' ' in t_redirect_to:
            t_redirect_to = settings.LOGIN_REDIRECT_URL
        elif '//' in t_redirect_to and re.match(r'[^\?]*//', t_redirect_to):
            t_redirect_to = settings.LOGIN_REDIRECT_URL

        auth_login(request, user)
            
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        #print'###t_redirect_to:',t_redirect_to
        return HttpResponseRedirect(t_redirect_to)
  
    except:
        import traceback; traceback.print_exc()
    

@login_required
def logoff(request):
        flag=True
        get_user(request)
        logout(request)
        if 'employee' in request.session:
                del request.session["employee"]
                flag=False  
        if flag:
           #print '###logoff',flag
            return HttpResponse("ok")
        else:
            return HttpResponse("fail")
class PasswordChangeForm1(PasswordChangeForm):
        "A form that lets a user change his password."

        def isEmployeePwd(self):
                if 'employee' in self.request.session:
                        e=self.request.session["employee"]
                        pwd=e.Passwd or e.PIN
                        if pwd==self.cleaned_data['new_password1']:
                                return True
                return False

        def clean_old_password(self):
                "Validates that the old_password field is correct."
                if not self.isEmployeePwd():
                        super(PasswordChangeForm1, self).clean_old_password()

        def save(self):
                "Saves the new password."
                if 'employee' in self.request.session:
                        e=self.request.session["employee"]
                        e.Passwd=self.cleaned_data['new_password1']
                        e.save()
                else:
                        super(PasswordChangeForm1, self).save()
                        k="user_id_%s"%self.request.user.pk
                        cache.delete(k)

@login_required
def password_change1(request, template_name='registration/password_change_form.html'):
        if request.POST:
                form = PasswordChangeForm1(request.user, request.POST)
                form.request=request
                if form.is_valid():
                        form.save()
                        from base.models_logentry import LogEntry, CHANGE
                        from django.contrib.contenttypes.models import ContentType
                        LogEntry.objects.log_action(
                                user_id                 = request.user and request.user.pk or None,
                                content_type_id = ContentType.objects.get_for_model(User).pk,
                                object_id           = request.user.pk,
                                object_repr         = request.user.username,
                                action_flag         = CHANGE,
                                change_message      = ""
                        )
                        
                        return HttpResponseRedirect('%sdone/' % request.path)
        else:
                form = PasswordChangeForm1(request.user)
        
        for k in form.fields:
            if hasattr(form.fields[k],"widget"):
                form.fields[k].widget.attrs["class"]="required"
        return render_to_response(template_name, {'form': form},
                context_instance=RequestContext(request))

urlpatterns = patterns('',
        ('^logout/$', logoff),
        ('^password_change/$', password_change1),
        ('^password_change/done/$', password_change_done),
        ('^login/$', logon),
        ('^password_reset/$', password_reset),
        ('^password_reset/done/$', password_reset_done),
        ('^$', logon),

)

