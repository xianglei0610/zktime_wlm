#coding=utf-8
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.views import iclock_guide

class IclockGuide(AppOperation):
        u'''导航'''
        verbose_name=_(u'导航')
        view=iclock_guide
        _app_menu ="iclock"
        _menu_group="iclock"
        _menu_index=0
        visible = False
