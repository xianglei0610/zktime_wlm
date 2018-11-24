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

from model_country import  Country
from model_state import State
from model_city import  City
from model_education import Education
from model_national import National 

#生成查询的表单
def get_searchform(request, model):
    if hasattr(model.Admin,"query_fields_Personnel") and model.Admin.query_fields_Personnel:        
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields_Pos))
    elif hasattr(model.Admin,"query_fields") and model.Admin.query_fields:
        searchform = seachform_for_model(request, model, fields=list(model.Admin.query_fields))
    else:
        return None
    return searchform

#基本资料视图
@login_required
def base_data_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = None
    model_name = None
    position = _(u'人事 ->基本资料')
    help_model_name = None
    template = CountryPage._template
    if HasPerm(request.user, 'contenttypes.can_CountryPage'):
        model_name = CountryPage._model_name
        template = CountryPage._template
        position = CountryPage._position
        searchform = get_searchform(request, Country)
        help_model_name = CountryPage.__name__
    elif HasPerm(request.user, 'contenttypes.can_StatePage'):
        model_name = StatePage._model_name
        template = StatePage._template
        position = StatePage._position
        searchform = get_searchform(request, State)
        help_model_name = StatePage.__name__
    elif HasPerm(request.user, 'contenttypes.can_CityPage'):
        model_name = CityPage._model_name
        template = CityPage._template
        position = CityPage._position
        searchform = get_searchform(request, City)
        help_model_name = CityPage.__name__        
    elif HasPerm(request.user, 'contenttypes.can_NationalPage'):
        model_name = NationalPage._model_name
        template = NationalPage._template
        position = NationalPage._position
        searchform = get_searchform(request, National)
        help_model_name = NationalPage.__name__        
    elif HasPerm(request.user, 'contenttypes.can_EducationPage'):
        model_name = EducationPage._model_name
        template = EducationPage._template
        position = EducationPage._position
        searchform = get_searchform(request, Education)
        help_model_name = EducationPage.__name__        

    if searchform:
        has_header = True          
    else:
        has_header = False

    return render_to_response(template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "model_name": model_name,
        "current_app": "personnel",
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "has_header": has_header,
        "searchform": searchform,
        "position": position,
        "help_model_name": "base_data_page"
    }))    
    

class BaseDataPage(AppOperation):
    u"""
    基本资料菜单
    """
    verbose_name = _(u'基本资料')
    view = base_data_page
    _app_menu = "personnel"
    _menu_index = 1
    
# 基本资料--国家
@login_required
def base_country_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, Country)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(CountryPage._template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "current_app": "personnel",
        "model_name": CountryPage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": CountryPage._position,
        "help_model_name": "base_data_page"    
    }))    

class CountryPage(AppOperation):
    u"""
    基本资料-国家
    """
    verbose_name = _(u'国家')
    view = base_country_page
    _menu_index = 100061
    _app_menu = 'personnel'
    _menu_group = 'personnel'
    _model_name = "Country"
    _template = "personnel_country.html"
    _position = _(u'人事 -> 基本资料 -> 国家')
    _parent_model = 'BaseDataPage'

# 基本资料--省份
@login_required
def base_state_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, State)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(StatePage._template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "current_app": "personnel",
        "model_name": StatePage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": StatePage._position,
        "help_model_name": "base_data_page"      
    }))    

class StatePage(AppOperation):
    u"""
    基本资料-省份
    """
    verbose_name = _(u'省份')
    view = base_state_page
    _menu_index = 100062
    _app_menu = 'personnel'
    _menu_group = 'personnel'
    _model_name = "State"
    _template = "personnel_state.html"
    _position = _(u'人事 -> 基本资料 -> 省份')
    _parent_model = 'BaseDataPage'

# 基本资料--城市
@login_required
def base_city_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, City)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(CityPage._template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "current_app": "personnel",
        "model_name": CityPage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": CityPage._position,
        "help_model_name": "base_data_page"    
    }))    

class CityPage(AppOperation):
    u"""
    基本资料-城市
    """
    verbose_name = _(u'城市')
    view = base_city_page
    _menu_index = 100063
    _app_menu = 'personnel'
    _menu_group = 'personnel'
    _model_name = "City"
    _template = "personnel_city.html"
    _position = _(u'人事 -> 基本资料 -> 城市')
    _parent_model = 'BaseDataPage'

# 基本资料--民族
@login_required
def base_national_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, National)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(NationalPage._template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "current_app": "personnel",
        "model_name": NationalPage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": NationalPage._position,
        "help_model_name": "base_data_page"    
    }))    

class NationalPage(AppOperation):
    u"""
    基本资料-民族
    """
    verbose_name = _(u'民族')
    view = base_national_page
    _menu_index = 100064
    _app_menu = 'personnel'
    _menu_group = 'personnel'
    _model_name = "National"
    _template = "personnel_national.html"
    _position = _(u'人事 -> 基本资料 -> 民族')
    _parent_model = 'BaseDataPage'

# 基本资料--学历
@login_required
def base_education_page(request):
    from dbapp.urls import dbapp_url
    request.dbapp_url = dbapp_url          
    apps = get_all_app_and_models()
    searchform = get_searchform(request, Education)
    if searchform:
        has_header=True          
    else:
        has_header=False   

    return render_to_response(EducationPage._template, RequestContext(request,{
        "app_label": "personnel",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps,
        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
        "menu_focus": "BaseDataPage",
        "current_app": "personnel",
        "model_name": EducationPage._model_name,
        "has_header": has_header,
        "searchform": searchform, 
        "position": EducationPage._position,
        "help_model_name": "base_data_page"  
    }))    

class EducationPage(AppOperation):
    u"""
    基本资料-学历
    """
    verbose_name = _(u'学历')
    view = base_education_page
    _menu_index = 100065
    _app_menu = 'personnel'
    _menu_group = 'personnel'
    _model_name = "Education"
    _template = "personnel_education.html"
    _position = _(u'人事 -> 基本资料 -> 学历')
    _parent_model = 'BaseDataPage'

