#coding=utf-8
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.views import fun_personnel

class PersonnelGuide(AppOperation):
    u'''导航'''
    verbose_name = _(u'导航')
    view = fun_personnel
    _app_menu = "personnel"
    _menu_group = "personnel"
    _menu_index = 0
