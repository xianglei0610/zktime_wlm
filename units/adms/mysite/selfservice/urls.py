#coding=utf-8
from django.conf.urls.defaults import *
from django.http import HttpResponse
from views import  get_specday,get_overtime,get_transaction,\
    self_login,get_selfreport,get_checkexact,password_change,model_list_self \
    ,operation_self,model_edit,model_new

def index(request):
    #print 'success login user:',request.user,'employee:',request.session["employee"],'\n'
    return get_checkexact(request)

urlpatterns = patterns('',
    (r"^index/$", index),
    (r"^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/$", model_list_self),
    (r"^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/_op_/(?P<op_name>[^/]*)/$", operation_self),
    (r"^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/_new_/$", model_new),
    (r"^(?P<app_label>[^/]*)/(?P<model_name>[^/]*)/(?P<DataKey>[^/]*)/$", model_edit),
    (r"^selfovertime/$", get_overtime),
    (r"^selfspecday/$", get_specday),
    (r"^selftransaction/$", get_transaction),
    (r"^selfcheckexact/$", get_checkexact),
    (r"^selfreport/$", get_selfreport),
    (r"^login/$",self_login),
    (r"^password_change/$",password_change),
)

